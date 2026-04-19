from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


class RetryError(RuntimeError):
    """Raised when a retry-wrapped operation fails all attempts."""


def with_retry(
    fn: Callable[[], T],
    attempts: int = 3,
    base_delay_seconds: float = 0.5,
    backoff_multiplier: float = 2.0,
) -> T:
    """Retry a function with exponential backoff on exceptions."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    delay = base_delay_seconds
    last_error: Exception | None = None

    for i in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # pragma: no cover - exercised in smoke test
            last_error = exc
            if i == attempts:
                break
            time.sleep(delay)
            delay *= backoff_multiplier

    raise RetryError(f"operation failed after {attempts} attempts: {last_error}") from last_error
