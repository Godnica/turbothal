"""REPL session state management."""

from __future__ import annotations


class Session:
    """Mutable session state for REPL mode."""

    def __init__(self, project_id: str = "", output_json: bool = False):
        self.project_id = project_id
        self.output_json = output_json
        self.history: list[str] = []

    def push_history(self, cmd: str) -> None:
        self.history.append(cmd)

    def get_prompt_context(self) -> str:
        if self.project_id:
            short = self.project_id[:8]
            return f"[{short}]"
        return ""
