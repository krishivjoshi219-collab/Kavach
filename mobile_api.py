"""Mobile contract routes: /api/v1/* — households, pairing, relay, screen, consent."""
from __future__ import annotations

import hmac
import logging
import os
import re
from typing import Annotated, Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agent import config as cfg
from agent import mobile, rulepack
from agent.ratelimit import RELAY_LIMIT, limiter

router = APIRouter(prefix="/api/v1")
_log = logging.getLogger("kavach.mobile_api")

#: Query-string IDs share the same alphabet as body IDs (IdStr), but remain
#: plain str so FastAPI keeps them as query params. Validated per-request.
_ID_RE = re.compile(r"^[\w\-.|]{1,64}$")


def _qid(value: str) -> str | None:
    """Validate a query-string id; None means 422-shape rejection upstream."""
    if value and len(value) <= 64 and _ID_RE.match(value):
        return value
    return None


def _bad_id(request: Request) -> JSONResponse:
    return _err("invalid_id", 422, request,
                detail="IDs must match ^[\\w\\-.|]{1,64}$ (max 64 chars).")

#: Sender hashes only — 64 lowercase hex chars. Raw numbers are rejected
#: at the schema layer (422) before any relay logic runs.
HashStr = Annotated[str, Field(min_length=64, max_length=64, pattern=r"^[0-9a-fA-F]{64}$")]

#: IDs are opaque tokens (hh_*, demo-senior, ch_*). Constrain the alphabet so
#: they can never carry path traversal, SQL (parameterized anyway), or log
#: injection payloads.
IdStr = Annotated[str, Field(max_length=64, pattern=r"^[\w\-.|]{1,64}$")]


def _err(error: str, status: int, request: Request | None = None, **extra: Any) -> JSONResponse:
    rid = getattr(request.state, "rid", "-") if request is not None else "-"
    return JSONResponse({"ok": False, "error": error, "request_id": rid, **extra},
                        status_code=status)


class PairInit(BaseModel):
    household_id: str = Field(max_length=64)
    manager_pubkey: str = Field(min_length=32, max_length=8000)


class PairComplete(BaseModel):
    pairing_code: str = Field(min_length=6, max_length=16)
    senior_pubkey: str = Field(min_length=32, max_length=8000)
    senior_id: str = Field(max_length=64, pattern=r"^[\w\-.]{1,64}$")


class BlobIn(BaseModel):
    household_id: str = Field(max_length=64)
    sender: str = Field(pattern=r"^(senior|manager)$")
    nonce: str = Field(min_length=8, max_length=100)
    ciphertext: str = Field(min_length=80, max_length=200_000)


class LookupIn(BaseModel):
    household_id: str = Field(max_length=64)
    number_hash: HashStr


class BlockIn(BaseModel):
    household_id: str = Field(max_length=64)
    number_hash: HashStr
    label: str = Field(default="", max_length=120)
    action: str = Field(default="block", pattern=r"^(block|silence|allow)$")


class ConsentIn(BaseModel):
    household_id: str = Field(max_length=64)
    senior_id: str = Field(max_length=64, pattern=r"^[\w\-.]{1,64}$")
    capabilities: dict[str, bool] = Field(max_length=16)
    granted_by: str = Field(default="", max_length=64)


class CommandIn(BaseModel):
    household_id: str = Field(max_length=64)
    senior_id: str = Field(max_length=64, pattern=r"^[\w\-.]{1,64}$")
    target: str = Field(pattern=r"^(senior|manager)$")
    type: str = Field(pattern=r"^(cut_call|sound_siren|show_message)$")
    payload_cipher: str = Field(default="", max_length=5000)


class BrainIn(BaseModel):
    household_id: str = Field(max_length=64)
    senior_id: str = Field(max_length=64, pattern=r"^[\w\-.]{1,64}$")
    snippet: str = Field(max_length=2000)


class TierIn(BaseModel):
    household_id: str = Field(max_length=64)
    tier: str = Field(pattern=r"^(free|pro|ultra)$")


@router.post("/households")
@limiter.limit(RELAY_LIMIT)
def api_household(request: Request):
    _ = request
    return {"household_id": mobile.create_household()}


@router.post("/pair/init")
@limiter.limit(RELAY_LIMIT)
def api_pair_init(body: PairInit, request: Request):
    _ = request
    out = mobile.open_pairing(body.household_id, body.manager_pubkey)
    if not out:
        return _err("unknown_household_or_key", 404, request)
    return {"ok": True, **out}


@router.post("/pair/complete")
@limiter.limit(RELAY_LIMIT)
def api_pair_complete(body: PairComplete, request: Request):
    _ = request
    out = mobile.complete_pairing(body.pairing_code, body.senior_pubkey, body.senior_id)
    if not out:
        return _err("bad_or_expired_code", 404, request)
    return {"ok": True, **out}


@router.get("/pair/peer")
def api_pair_peer(household_id: str, request: Request):
    hid = _qid(household_id)
    if hid is None:
        return _bad_id(request)
    out = mobile.get_pair_peer(hid)
    if not out:
        return _err("not_paired", 404, request)
    return {"ok": True, **out}


@router.post("/sync/push")
@limiter.limit(RELAY_LIMIT)
def api_push(body: BlobIn, request: Request):
    _ = request
    bid = mobile.push_blob(body.household_id, body.sender, body.nonce, body.ciphertext)
    if bid is None:
        return _err("rejected", 400, request,
                    detail="Blob failed the E2E gate (plaintext, replay, or unknown household).")
    return {"ok": True, "blob_id": bid}


@router.get("/sync/pull")
def api_pull(household_id: str, since_id: int = 0, request: Request = None):  # type: ignore[assignment]
    hid = _qid(household_id)
    if hid is None:
        return _bad_id(request)
    if since_id < 0:
        return _err("bad_since_id", 422, request)
    return {"ok": True, "blobs": mobile.pull_blobs(hid, since_id)}


@router.post("/screen/lookup")
def api_lookup(body: LookupIn):
    return {"ok": True, **mobile.lookup_number(body.household_id, body.number_hash.lower())}


@router.post("/screen/block")
@limiter.limit(RELAY_LIMIT)
def api_block(body: BlockIn, request: Request):
    _ = request
    ok = mobile.block_number(body.household_id, body.number_hash.lower(),
                             body.label, body.action)
    if not ok:
        return _err("rejected", 400, request, detail="Invalid hash or action.")
    return {"ok": True}


@router.post("/screen/unblock")
@limiter.limit(RELAY_LIMIT)
def api_unblock(body: LookupIn, request: Request):
    _ = request
    if not mobile.unblock_number(body.household_id, body.number_hash.lower()):
        return _err("not_found", 404, request)
    return {"ok": True}


@router.get("/screen/list")
def api_blocklist(household_id: str, request: Request):
    """This-household blocklist so sibling devices sync (no 3-household wait)."""
    hid = _qid(household_id)
    if hid is None:
        return _bad_id(request)
    return {"ok": True, "entries": mobile.list_blocklist(hid)}


@router.post("/consent/set")
@limiter.limit(RELAY_LIMIT)
def api_consent_set(body: ConsentIn, request: Request):
    _ = request
    return {"ok": mobile.set_consent(body.household_id, body.senior_id,
                                     body.capabilities, body.granted_by)}


@router.post("/consent/revoke")
@limiter.limit(RELAY_LIMIT)
def api_consent_revoke(household_id: str, senior_id: str, request: Request):
    hid, sid = _qid(household_id), _qid(senior_id)
    if hid is None or sid is None:
        return _bad_id(request)
    if not mobile.revoke_consent(hid, sid):
        return _err("not_found", 404, request,
                    detail="No consent record for this household/senior.")
    return {"ok": True}


@router.get("/consent")
def api_consent_get(household_id: str, senior_id: str, request: Request):
    hid, sid = _qid(household_id), _qid(senior_id)
    if hid is None or sid is None:
        return _bad_id(request)
    return {"ok": True, **mobile.get_consent(hid, sid)}


@router.post("/device/command")
@limiter.limit(RELAY_LIMIT)
def api_command(body: CommandIn, request: Request):
    _ = request
    # Remote powers require live consent: cut_call needs remote_cut, etc.
    need = {"cut_call": "remote_cut", "sound_siren": "screen_calls",
            "show_message": "forward_sms"}.get(body.type, "")
    if need and not mobile.may(need, body.household_id, body.senior_id):
        return _err("consent_required", 403, request,
                    summary=f"Senior has not granted '{need}'.")
    out = mobile.queue_command(body.household_id, body.target, body.type,
                               body.payload_cipher)
    if not out:
        return _err("rejected", 400, request)
    return {"ok": True, **out}


@router.get("/device/commands")
def api_commands(household_id: str, target: str = "senior", request: Request = None):  # type: ignore[assignment]
    hid = _qid(household_id)
    if hid is None:
        return _bad_id(request)
    if target not in ("senior", "manager"):
        return _err("bad_target", 422, request)
    return {"ok": True, "commands": mobile.pending_commands(hid, target)}


@router.post("/device/commands/{command_id}/ack")
@limiter.limit(RELAY_LIMIT)
def api_ack(command_id: int, request: Request):
    _ = request
    if command_id <= 0:
        return _err("bad_command_id", 422, request)
    if not mobile.ack_command(command_id):
        return _err("not_found", 404, request)
    return {"ok": True}


@router.post("/brain/ask")
@limiter.limit(RELAY_LIMIT)
def api_brain(body: BrainIn, request: Request):
    _ = request
    # Cloud brain additionally requires the household's cloud_brain consent.
    if not mobile.may("cloud_brain", body.household_id, body.senior_id):
        return _err("consent_required", 403, request,
                    summary="Household has not enabled the cloud brain.")
    out = mobile.brain_ask(body.household_id, body.snippet)
    if out.get("error") == "quota_exceeded":
        return JSONResponse(out, status_code=429)
    return out


@router.post("/household/tier")
@limiter.limit(RELAY_LIMIT)
def api_tier(body: TierIn, request: Request):
    _ = request
    # Sandbox path (Next Gen test mode): client reconciles after sandbox purchase.
    # Production path: POST /billing/webhook (Bearer-authenticated, idempotent,
    # server is authority). See docs/REVENUECAT.md.
    if not mobile.set_tier(body.household_id, body.tier):
        return _err("unknown_household", 404, request)
    return {"ok": True}


class WebhookIn(BaseModel):
    event_id: str = Field(max_length=128)
    household_id: str = Field(max_length=64)
    event_type: str = Field(max_length=64)
    entitlement: str = Field(default="", max_length=64)


@router.post("/billing/webhook")
@limiter.limit(RELAY_LIMIT)
def api_billing_webhook(body: WebhookIn, request: Request):
    """RevenueCat webhook (server authority). TEST MODE label when no secret set."""
    secret = os.getenv("RC_WEBHOOK_AUTH", "")
    if not secret and cfg.IS_PROD:
        # Fail closed: an unauthenticated money endpoint must never apply
        # tiers in production. Demo/dev keeps TEST MODE (documented).
        return _err("webhook_not_configured", 503, request,
                    detail="Set RC_WEBHOOK_AUTH in production.")
    if secret:
        auth = request.headers.get("authorization", "")
        # Constant-time compare: plain != leaks prefix length via timing.
        if not hmac.compare_digest(auth, f"Bearer {secret}"):
            return _err("unauthorized", 401, request)
    t = body.event_type.upper()
    if t in ("INITIAL_PURCHASE", "RENEWAL", "PRODUCT_CHANGE"):
        if not body.entitlement.strip():
            # Empty entitlement must never mint paid quota (was: else→"pro").
            return _err("missing_entitlement", 400, request)
        tier = "ultra" if "family" in body.entitlement.lower() or "ultra" in body.entitlement.lower() else "pro"
    elif t in ("CANCELLATION", "EXPIRATION", "BILLING_ISSUE"):
        tier = "free"
    elif t == "TEST":
        tier = "pro"
    else:
        return _err("unknown_event", 400, request)
    new = mobile.record_webhook("revenuecat", body.event_id, body.household_id, tier)
    if not new:
        # Replay: report the STORED tier, not this request's recomputation —
        # a replayed event with different fields must not rewrite history.
        stored = mobile.stored_webhook_tier("revenuecat", body.event_id) or tier
        return {"ok": True, "duplicate": True, "tier": stored}
    if not mobile.set_tier(body.household_id, tier):
        return _err("unknown_household", 404, request, tier=tier, test_mode=not bool(secret))
    return {"ok": True, "tier": tier, "test_mode": not bool(secret)}


@router.get("/rules/pack")
def api_rules_pack():
    """Versioned signed rule pack. Reads stay open; the app caches + verifies."""
    return {"ok": True, **rulepack.serve_pack()}


@router.get("/household/tier")
def api_tier_get(household_id: str):
    tier = mobile.get_tier(household_id[:64])
    # get_tier returns the raw DB string: a legacy/manual row could hold a
    # tier outside QUOTAS. Fall back to free instead of KeyError-500.
    quota = mobile.QUOTAS.get(tier, mobile.QUOTAS["free"])
    return {"tier": tier, "quota": quota}


class CheckinIn(BaseModel):
    household_id: str = Field(max_length=64)
    senior_id: str = Field(max_length=64, pattern=r"^[\w\-.]{1,64}$")
    status: str = Field(default="safe", pattern=r"^(safe|uneasy|need_call)$")
    note: str = Field(default="", max_length=200)


class NotificationIn(BaseModel):
    household_id: str = Field(max_length=64)
    journey: str = Field(pattern=r"^(morning_checkin|missed_checkin|emergency_alert)$")
    senior_id: str = Field(default="dad1", max_length=64)
    caller_hash: str = Field(default="", max_length=64)
    reasons: list[str] = Field(default_factory=list, max_length=8)


@router.post("/checkin")
@limiter.limit(RELAY_LIMIT)
def api_checkin(body: CheckinIn, request: Request):
    _ = request
    from agent import models
    mood = "ok" if body.status == "safe" else "needs_care"
    try:
        cid = models.add_checkin(body.senior_id, "mobile", body.note or body.status, mood)
    except Exception:  # noqa: BLE001 - locked/corrupt DB must degrade, not 500
        _log.warning("checkin persist failed")
        cid = None
    return {
        "ok": cid is not None,
        "household_id": body.household_id,
        "senior_id": body.senior_id,
        "status": body.status,
        "mood": mood,
        "checkin_id": cid,
        "acknowledged": True,
        "persisted": cid is not None,
    }


@router.post("/notifications/send")
@limiter.limit(RELAY_LIMIT)
def api_notifications_send(body: NotificationIn, request: Request):
    _ = request
    from agent import notifications
    if body.journey == "morning_checkin":
        res = notifications.send_morning_checkin(body.household_id, body.senior_id)
    elif body.journey == "missed_checkin":
        res = notifications.send_missed_checkin_nudge(body.household_id)
    elif body.journey == "emergency_alert":
        res = notifications.send_emergency_scam_alert(body.household_id, body.caller_hash, body.reasons)
    else:
        return _err("unknown_journey", 422, request)
    return res


@router.get("/threat-feed")
def api_threat_feed():
    """Community shield: hashes reported by 3+ independent households. Hashes only."""
    return {"ok": True, "threshold": mobile.COMMUNITY_THRESHOLD,
            "entries": mobile.threat_feed()}


@router.get("/threat-radar")
def api_threat_radar(household_id: str = "default", request: Request = None):  # type: ignore[assignment]
    hid = _qid(household_id)
    if hid is None:
        return _bad_id(request)
    stats = mobile.community_stats(hid)
    level = "OPTIMAL" if stats["household_blocks"] > 0 else "LEARNING"
    return {
        "ok": True,
        "household_stats": stats,
        "community_shield_level": level,
        "zero_knowledge_enforced": True,
        "note": "Counts from this relay only (household blocklist + blobs). Not carrier regional data."
    }

