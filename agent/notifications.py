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

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID", "test_onesignal_app_id")
ONESIGNAL_REST_KEY = os.getenv("ONESIGNAL_REST_KEY", "")
ONESIGNAL_API_URL = "https://onesignal.com/api/v1/notifications"


def _send_push(headings: dict[str, str], contents: dict[str, str],
               custom_data: dict[str, Any], tag_filters: list[dict[str, str]]) -> dict[str, Any]:
    """Dispatches a notification via OneSignal or logs in simulated mode."""
    if not ONESIGNAL_REST_KEY:
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
        "app_id": ONESIGNAL_APP_ID,
        "headings": headings,
        "contents": contents,
        "data": custom_data,
        "filters": tag_filters,
    }
    headers = {
        "Authorization": f"Basic {ONESIGNAL_REST_KEY}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(ONESIGNAL_API_URL, json=payload, headers=headers)
            data = resp.json()
            return {"ok": resp.status_code == 200, "data": data}
    except (httpx.HTTPError, OSError) as exc:
        log.warning("OneSignal dispatch failed: %s", exc)
        return {"ok": False, "error": str(exc)}


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
    reason_str = "; ".join(reasons) if reasons else "Severe threat or OTP ask detected"
    return _send_push(
        headings={"en": "🚨 URGENT: Scam Intercepted on Dad's Phone"},
        contents={"en": f"Blocked scammer ({caller_hash[:8]}...). Threat: {reason_str}. Open War Room to intervene."},
        custom_data={"type": "scam_alert", "household_id": household_id, "caller_hash": caller_hash},
        tag_filters=[
            {"field": "tag", "key": "household_id", "relation": "=", "value": household_id},
            {"field": "tag", "key": "role", "relation": "=", "value": "manager"},
        ]
    )
