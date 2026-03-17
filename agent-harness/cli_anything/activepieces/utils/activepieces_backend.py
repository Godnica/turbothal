"""Backend discovery: check if Activepieces server is reachable."""

from __future__ import annotations

import json
import urllib.request
import urllib.error


def check_health(api_url: str) -> dict:
    """Check Activepieces server health. Returns status dict or raises."""
    url = f"{api_url.rstrip('/')}/api/v1/flags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Cannot reach Activepieces at {api_url}.\n"
            "Make sure the server is running.\n"
            "  Docker: docker compose up -d\n"
            "  Dev:    cd activepieces && bun run dev\n"
            f"Error: {e}"
        ) from e


def find_activepieces(api_url: str = "http://localhost:3000") -> str:
    """Verify the server is up and return the API URL."""
    check_health(api_url)
    return api_url
