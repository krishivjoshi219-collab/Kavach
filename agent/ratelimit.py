"""Single shared slowapi limiter.

app.py and mobile_api.py must use THIS instance: slowapi enforces limits
through ``request.app.state.limiter``, so two separate Limiter objects mean
one router's limits silently never fire. Import here, set
``app.state.limiter = limiter`` once in app.py AND add SlowAPIMiddleware —
without the middleware, @limiter.limit decorators are parsed but never
enforced (silent fail-open).
"""
from __future__ import annotations

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

#: Kill-switch for load tests / pytest: RATE_LIMIT_ENABLED=false.
#: Production default is enabled.
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() not in (
    "0", "false", "no", "off")

limiter = Limiter(key_func=get_remote_address, enabled=RATE_LIMIT_ENABLED)

#: Abuse budget for relay mutations (pair/push/block/command/consent/tier).
#: Reads stay unlimited (senior polls commands every ~8s by design).
RELAY_LIMIT = "60/minute"
