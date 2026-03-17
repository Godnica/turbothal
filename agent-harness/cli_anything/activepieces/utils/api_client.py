"""HTTP client wrapper for the Activepieces REST API."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Iterator


class ActivepiecesError(Exception):
    def __init__(self, status: int, code: str, message: str, raw: dict | None = None):
        self.status = status
        self.code = code
        self.raw = raw
        super().__init__(f"[{status}] {code}: {message}")


class ActivepiecesClient:
    """Lightweight HTTP client for Activepieces API v1."""

    def __init__(self, api_url: str, api_key: str, project_id: str | None = None, timeout: int = 30):
        self.base_url = f"{api_url.rstrip('/')}/api/v1"
        self.api_key = api_key
        self.project_id = project_id
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _request(self, method: str, path: str, params: dict | None = None, body: dict | None = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if qs:
                url = f"{url}?{qs}"

        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode()
                if not raw:
                    return {}
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            raw_body = e.read().decode() if e.fp else ""
            try:
                err = json.loads(raw_body)
            except (json.JSONDecodeError, ValueError):
                err = {}
            code = err.get("code", "UNKNOWN")
            params_msg = err.get("params", {})
            msg = params_msg.get("message", raw_body) if isinstance(params_msg, dict) else str(params_msg)
            raise ActivepiecesError(e.code, code, msg, err) from e

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, body: dict | None = None, params: dict | None = None) -> Any:
        return self._request("POST", path, params=params, body=body or {})

    def delete(self, path: str, params: dict | None = None) -> Any:
        return self._request("DELETE", path, params=params)

    def paginate(self, path: str, params: dict | None = None, limit: int | None = None) -> Iterator[dict]:
        """Auto-paginate through a SeekPage response, yielding individual items."""
        p = dict(params or {})
        count = 0
        while True:
            page = self.get(path, params=p)
            data = page.get("data", [])
            for item in data:
                yield item
                count += 1
                if limit and count >= limit:
                    return
            next_cursor = page.get("next")
            if not next_cursor or not data:
                return
            p["cursor"] = next_cursor
