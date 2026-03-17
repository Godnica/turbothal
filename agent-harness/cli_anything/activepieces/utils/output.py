"""Output formatting utilities."""

from __future__ import annotations

import json
import sys
from typing import Any


def format_json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def format_table(headers: list[str], rows: list[list[str]], max_col_width: int = 40) -> str:
    if not rows:
        return "(no results)"
    all_rows = [headers] + rows
    widths = [0] * len(headers)
    for row in all_rows:
        for i, cell in enumerate(row):
            cell_str = str(cell)[:max_col_width]
            widths[i] = max(widths[i], len(cell_str))

    def fmt_row(row):
        cells = []
        for i, cell in enumerate(row):
            cells.append(str(cell)[:max_col_width].ljust(widths[i]))
        return "  ".join(cells)

    lines = [fmt_row(headers)]
    lines.append("  ".join("-" * w for w in widths))
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def print_output(data: Any, as_json: bool = False, headers: list[str] | None = None, row_keys: list[str] | None = None) -> None:
    """Print data in JSON or table format."""
    if as_json:
        print(format_json(data))
        return

    if isinstance(data, dict) and "data" in data:
        items = data["data"]
    elif isinstance(data, list):
        items = data
    else:
        print(format_json(data))
        return

    if not items:
        print("(no results)")
        return

    if headers and row_keys:
        rows = []
        for item in items:
            row = [str(item.get(k, "")) for k in row_keys]
            rows.append(row)
        print(format_table(headers, rows))
    else:
        print(format_json(items))


def print_success(msg: str) -> None:
    print(f"\u2713 {msg}", file=sys.stderr)


def print_error(msg: str) -> None:
    print(f"\u2717 {msg}", file=sys.stderr)
