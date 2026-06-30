from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, status

LOGIN_WINDOW_SECONDS = 60
LOGIN_MAX_ATTEMPTS = 5

_attempts: dict[str, deque[float]] = defaultdict(deque)


def check_login_rate_limit(identifier: str) -> None:
    now = monotonic()
    attempts = _attempts[identifier]
    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
        attempts.popleft()
    if len(attempts) >= LOGIN_MAX_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts")
    attempts.append(now)


def clear_login_rate_limit(identifier: str) -> None:
    _attempts.pop(identifier, None)


def reset_login_rate_limits() -> None:
    _attempts.clear()
