"""OneSignal notification journeys and caregiver safety rhythms for Kavach.

Supports automated morning check-ins, missed check-in caregiver nudges,
and breakthrough emergency alerts. Uses OneSignal REST API.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

log = logging.getLogger("kavach.notifications")

ONESIGNAL_API_URL = "https://onesignal.com/api/v1/notifications"
_PUSH_TIMEOUT_S = 10


def _onesignal_config() -> tuple[str, str]:
    """Read env lazily so tests / redeploys can rotate keys without reimport."""
    return (os.getenv("ONESIGNAL_APP_ID", "test_onesignal_app_id"),
            os.getenv("ONESIGNAL_REST_KEY", ""))


def _send_push(headings: dict[str, str], contents: dict[str, str],
               custom_data: dict[str, Any], tag_filters: list[dict[str, str]]) -> dict[str, Any]:
    """Dispatches a notification via OneSignal or logs in simulated mode."""
    app_id, rest_key = _onesignal_config()
    if not rest_key:
        log.info("[OneSignal Test Mode] Notification dispatched: %s | %s", headings.get("en"), contents.get("en"))
        return {
            "ok": True,
            "simulated": True,
            "id": f"sim_{int(time.time()*1000)}",
            "recipients": 1,
            "headings": headings,
            "contents": contents,
            "data": custom_data,
        }

    payload = {
        "app_id": app_id,
        "headings": headings,
        "contents": contents,
        "data": custom_data,
        "filters": tag_filters,
    }
    headers = {
        "Authorization": f"Basic {rest_key}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=_PUSH_TIMEOUT_S) as client:
            resp = client.post(ONESIGNAL_API_URL, json=payload, headers=headers)
            try:
                data = resp.json()
            except ValueError:
                data = {"raw": resp.text[:500]}
            if resp.status_code != 200:
                log.warning("OneSignal non-200: %s", resp.status_code)
                return {"ok": False, "error": f"onesignal_{resp.status_code}", "data": data}
            return {"ok": True, "data": data}
    except Exception as exc:  # noqa: BLE001 - push must never 500 the relay
        log.warning("OneSignal dispatch failed: %s", exc)
        return {"ok": False, "error": str(exc)[:200]}


def send_morning_checkin(household_id: str, senior_id: str) -> dict[str, Any]:
    """Daily morning check-in notification for the senior."""
    return _send_push(
        headings={"en": "Kavach Morning Shield ☀️"},
        contents={"en": "Good morning! Tap to confirm you're safe and start your protected day."},
        custom_data={"type": "morning_checkin", "household_id": household_id, "senior_id": senior_id},
        tag_filters=[
            {"field": "tag", "key": "household_id", "relation": "=", "value": household_id},
            {"field": "tag", "key": "role", "relation": "=", "value": "senior"},
        ]
    )


def send_missed_checkin_nudge(household_id: str, senior_name: str = "Dad") -> dict[str, Any]:
    """Gentle nudge sent to family manager if morning check-in is missed."""
    return _send_push(
        headings={"en": "Family Check-In Reminder 💛"},
        contents={"en": f"{senior_name} hasn't checked in this morning. A quick phone call brings peace of mind."},
        custom_data={"type": "missed_checkin_nudge", "household_id": household_id},
        tag_filters=[
            {"field": "tag", "key": "household_id", "relation": "=", "value": household_id},
            {"field": "tag", "key": "role", "relation": "=", "value": "manager"},
        ]
    )


def send_emergency_scam_alert(household_id: str, caller_hash: str, reasons: list[str]) -> dict[str, Any]:
    """High-priority alert sent to family manager upon live scam interception."""
    short = [str(r)[:120] for r in (reasons or [])[:5]]
    reason_str = "; ".join(short) if short else "Severe threat or OTP ask detected"
    reason_str = reason_str[:300]
    return _send_push(
        headings={"en": "🚨 URGENT: Scam Intercepted on Dad's Phone"},
        contents={"en": f"Blocked scammer ({caller_hash[:8]}...). Threat: {reason_str}. Open War Room to intervene."},
        custom_data={"type": "scam_alert", "household_id": household_id, "caller_hash": caller_hash},
        tag_filters=[
            {"field": "tag", "key": "household_id", "relation": "=", "value": household_id},
            {"field": "tag", "key": "role", "relation": "=", "value": "manager"},
        ]
    )
