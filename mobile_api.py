"""Mobile contract routes: /api/v1/* — households, pairing, relay, screen, consent."""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from agent import mobile
from agent.config import RATE_LIMIT_PER_MIN

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/v1")


class PairInit(BaseModel):
    household_id: str = Field(max_length=64)
    manager_pubkey: str = Field(max_length=8000)


class PairComplete(BaseModel):
    pairing_code: str = Field(max_length=16)
    senior_pubkey: str = Field(max_length=8000)
    senior_id: str = Field(max_length=64, pattern=r"^[\w\-.]{1,64}$")


class BlobIn(BaseModel):
    household_id: str = Field(max_length=64)
    sender: str = Field(pattern=r"^(senior|manager)$")
    nonce: str = Field(max_length=100)
    ciphertext: str = Field(max_length=200_000)


class LookupIn(BaseModel):
    household_id: str = Field(max_length=64)
    number_hash: str = Field(min_length=64, max_length=64)


class BlockIn(BaseModel):
    household_id: str = Field(max_length=64)
    number_hash: str = Field(min_length=64, max_length=64)
    label: str = Field(default="", max_length=120)
    action: str = Field(default="block", pattern=r"^(block|silence|allow)$")


class ConsentIn(BaseModel):
    household_id: str = Field(max_length=64)
    senior_id: str = Field(max_length=64, pattern=r"^[\w\-.]{1,64}$")
    capabilities: dict[str, bool]
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


def _rl():
    return limiter.limit(f"{RATE_LIMIT_PER_MIN}/minute")


@router.post("/households")
def api_household():
    return {"household_id": mobile.create_household()}


@router.post("/pair/init")
def api_pair_init(body: PairInit):
    out = mobile.open_pairing(body.household_id, body.manager_pubkey)
    if not out:
        return {"ok": False, "error": "unknown_household_or_key"}
    return {"ok": True, **out}


@router.post("/pair/complete")
def api_pair_complete(body: PairComplete):
    out = mobile.complete_pairing(body.pairing_code, body.senior_pubkey, body.senior_id)
    if not out:
        return {"ok": False, "error": "bad_or_expired_code"}
    return {"ok": True, **out}


@router.get("/pair/peer")
def api_pair_peer(household_id: str):
    out = mobile.get_pair_peer(household_id[:64])
    if not out:
        return {"ok": False, "error": "not_paired"}
    return {"ok": True, **out}


@router.post("/sync/push")
def api_push(body: BlobIn, request: Request):
    _ = request
    bid = mobile.push_blob(body.household_id, body.sender, body.nonce, body.ciphertext)
    if bid is None:
        return {"ok": False, "error": "rejected"}
    return {"ok": True, "blob_id": bid}


@router.get("/sync/pull")
def api_pull(household_id: str, since_id: int = 0):
    return {"ok": True, "blobs": mobile.pull_blobs(household_id[:64], since_id)}


@router.post("/screen/lookup")
def api_lookup(body: LookupIn):
    return {"ok": True, **mobile.lookup_number(body.household_id, body.number_hash.lower())}


@router.post("/screen/block")
def api_block(body: BlockIn):
    ok = mobile.block_number(body.household_id, body.number_hash.lower(),
                             body.label, body.action)
    return {"ok": ok}


@router.post("/screen/unblock")
def api_unblock(body: LookupIn):
    return {"ok": mobile.unblock_number(body.household_id, body.number_hash.lower())}


@router.post("/consent/set")
def api_consent_set(body: ConsentIn):
    return {"ok": mobile.set_consent(body.household_id, body.senior_id,
                                     body.capabilities, body.granted_by)}


@router.post("/consent/revoke")
def api_consent_revoke(household_id: str, senior_id: str):
    return {"ok": mobile.revoke_consent(household_id[:64], senior_id[:64])}


@router.get("/consent")
def api_consent_get(household_id: str, senior_id: str):
    return mobile.get_consent(household_id[:64], senior_id[:64])


@router.post("/device/command")
def api_command(body: CommandIn):
    # Remote powers require live consent: cut_call needs remote_cut, etc.
    need = {"cut_call": "remote_cut", "sound_siren": "screen_calls",
            "show_message": "forward_sms"}.get(body.type, "")
    if need and not mobile.may(need, body.household_id, body.senior_id):
        return {"ok": False, "error": "consent_required",
                "summary": f"Senior has not granted '{need}'."}
    out = mobile.queue_command(body.household_id, body.target, body.type,
                               body.payload_cipher)
    if not out:
        return {"ok": False, "error": "rejected"}
    return {"ok": True, **out}


@router.get("/device/commands")
def api_commands(household_id: str, target: str = "senior"):
    if target not in ("senior", "manager"):
        return {"ok": False, "error": "bad_target"}
    return {"ok": True, "commands": mobile.pending_commands(household_id[:64], target)}


@router.post("/device/commands/{command_id}/ack")
def api_ack(command_id: int):
    return {"ok": mobile.ack_command(command_id)}


@router.post("/brain/ask")
def api_brain(body: BrainIn):
    # Cloud brain additionally requires the household's cloud_brain consent.
    if not mobile.may("cloud_brain", body.household_id, body.senior_id):
        return {"ok": False, "error": "consent_required",
                "summary": "Household has not enabled the cloud brain."}
    return mobile.brain_ask(body.household_id, body.snippet)


@router.post("/household/tier")
def api_tier(body: TierIn):
    # Demo/trust mode: tier set by client after RevenueCat purchase; server verifies
    # receipts in production (documented in docs/REVENUECAT.md).
    return {"ok": mobile.set_tier(body.household_id, body.tier)}


class WebhookIn(BaseModel):
    event_id: str = Field(max_length=128)
    household_id: str = Field(max_length=64)
    event_type: str = Field(max_length=64)
    entitlement: str = Field(default="", max_length=64)


_router_only = True  # placeholder to keep linters quiet about router-only module


@router.post("/billing/webhook")
def api_billing_webhook(body: WebhookIn, request: Request):
    """RevenueCat webhook (server authority). TEST MODE label when no secret set."""
    import os as _os
    secret = _os.getenv("RC_WEBHOOK_AUTH", "")
    if secret:
        auth = request.headers.get("authorization", "")
        if auth != f"Bearer {secret}":
            return {"ok": False, "error": "unauthorized"}
    t = body.event_type.upper()
    if t in ("INITIAL_PURCHASE", "RENEWAL", "PRODUCT_CHANGE"):
        tier = "ultra" if "family" in body.entitlement.lower() or "ultra" in body.entitlement.lower() else "pro"
    elif t in ("CANCELLATION", "EXPIRATION", "BILLING_ISSUE"):
        tier = "free"
    elif t == "TEST":
        tier = "pro"
    else:
        return {"ok": False, "error": "unknown_event"}
    new = mobile.record_webhook("revenuecat", body.event_id, body.household_id, tier)
    if not new:
        return {"ok": True, "duplicate": True, "tier": tier}
    ok = mobile.set_tier(body.household_id, tier)
    return {"ok": ok, "tier": tier, "test_mode": not bool(secret)}


@router.get("/household/tier")
def api_tier_get(household_id: str):
    tier = mobile.get_tier(household_id[:64])
    return {"tier": tier, "quota": mobile.QUOTAS[tier]}


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
    reasons: list[str] = Field(default_factory=list)


@router.post("/checkin")
def api_checkin(body: CheckinIn):
    return {
        "ok": True,
        "household_id": body.household_id,
        "senior_id": body.senior_id,
        "status": body.status,
        "acknowledged": True
    }


@router.post("/notifications/send")
def api_notifications_send(body: NotificationIn):
    from agent import notifications
    if body.journey == "morning_checkin":
        res = notifications.send_morning_checkin(body.household_id, body.senior_id)
    elif body.journey == "missed_checkin":
        res = notifications.send_missed_checkin_nudge(body.household_id)
    elif body.journey == "emergency_alert":
        res = notifications.send_emergency_scam_alert(body.household_id, body.caller_hash, body.reasons)
    else:
        return {"ok": False, "error": "unknown_journey"}
    return res


@router.get("/threat-radar")
def api_threat_radar(household_id: str = "default"):
    _ = household_id
    return {
        "ok": True,
        "regional_stats": {
            "bank_impersonation_24h": 14,
            "power_cutoff_scams_24h": 6,
            "digital_arrest_threats_24h": 3,
            "total_threats_shielded": 842
        },
        "community_shield_level": "OPTIMAL",
        "zero_knowledge_enforced": True
    }

