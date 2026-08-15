from __future__ import annotations

import json
import time
from typing import Any, Callable, Protocol, Optional

import requests

from ..contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError
from ..instruments import Instrument


class SourceAdapter(Protocol):
    source_id: str

    def supports(self, request: DataRequest, instrument: Instrument) -> bool: ...
    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]: ...


class HttpClient:
    """Small retrying HTTP client with explicit classified failures."""

    def __init__(
        self,
        *,
        session: Optional[Any] = None,
        timeout: float = 8.0,
        max_retries: int = 2,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self.sleeper = sleeper

    def _get(self, url: str, **kwargs: Any) -> Any:
        timeout = kwargs.pop("timeout", self.timeout)
        last_error: Optional[FinancialDataError] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=timeout, **kwargs)
            except Exception as exc:
                last_error = FinancialDataError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    f"network request failed: {exc}",
                    {"url": url, "attempt": attempt + 1},
                )
                if attempt < self.max_retries:
                    self.sleeper(0.5 * (2**attempt))
                    continue
                raise last_error from exc

            status = int(getattr(response, "status_code", 200))
            if 200 <= status < 300:
                return response
            if status == 401:
                raise FinancialDataError(ErrorCode.AUTH_REQUIRED, "source returned HTTP 401", {"url": url})
            if status == 403:
                raise FinancialDataError(ErrorCode.SOURCE_BLOCKED, "source returned HTTP 403", {"url": url})
            if status == 429:
                last_error = FinancialDataError(ErrorCode.RATE_LIMITED, "source rate-limited the request", {"url": url})
            elif status >= 500:
                last_error = FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, f"source returned HTTP {status}", {"url": url})
            else:
                raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, f"source returned HTTP {status}", {"url": url})

            if attempt < self.max_retries:
                self.sleeper(0.5 * (2**attempt))
                continue
            raise last_error
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "unreachable HTTP state", {"url": url})

    def get_text(self, url: str, *, encoding: Optional[str] = None, **kwargs: Any) -> str:
        response = self._get(url, **kwargs)
        if encoding:
            content = getattr(response, "content", None)
            if content is not None:
                try:
                    return bytes(content).decode(encoding)
                except UnicodeDecodeError:
                    # Fixture/fake sessions may already expose decoded text; use it rather
                    # than replacing invalid bytes silently.
                    text = getattr(response, "text", None)
                    if text is not None:
                        return str(text)
                    raise
        return str(getattr(response, "text", ""))

    def get_json(self, url: str, **kwargs: Any) -> Any:
        response = self._get(url, **kwargs)
        try:
            return response.json()
        except Exception as exc:
            try:
                return json.loads(getattr(response, "text", ""))
            except Exception:
                raise FinancialDataError(
                    ErrorCode.NORMALIZATION_ERROR,
                    f"source returned invalid JSON: {exc}",
                    {"url": url},
                ) from exc
