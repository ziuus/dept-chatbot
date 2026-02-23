from __future__ import annotations

import time
import os
from collections import deque
from dataclasses import dataclass, field
from threading import Lock

from fastapi import Header, HTTPException, Request, status

from app.config import settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("SERVICE_API_KEY") or settings.service_api_key
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


@dataclass
class FixedWindowRateLimiter:
    max_requests: int
    window_seconds: int
    _events: dict[str, deque[float]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def _prune(self, key: str, now: float) -> deque[float]:
        queue = self._events.get(key, deque())
        cutoff = now - self.window_seconds
        while queue and queue[0] < cutoff:
            queue.popleft()
        self._events[key] = queue
        return queue

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            queue = self._prune(key, now)
            if len(queue) >= self.max_requests:
                return False
            queue.append(now)
            return True


rate_limiter = FixedWindowRateLimiter(
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)


def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
