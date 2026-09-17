"""Single shared slowapi limiter.

app.py and mobile_api.py must use THIS instance: slowapi enforces limits
through ``request.app.state.limiter``, so two separate Limiter objects mean
one router's limits silently never fire. Import here, set
``app.state.limiter = limiter`` once in app.py.
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

#: Abuse budget for relay mutations (pair/push/block/command/consent/tier).
#: Reads stay unlimited (senior polls commands every ~8s by design).
RELAY_LIMIT = "60/minute"
