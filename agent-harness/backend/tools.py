"""
Tool definitions and executors for the Activepieces flow-creation agent.

Tools:
  - bash       : run shell commands in restricted mode (read-only filesystem,
                 API calls only — no file writes, no cd, no path redirections)
  - read_file  : read a file from the knowledge/ directory (always read-only)
"""

import subprocess
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

# Secondary blocklist for operations that restricted bash alone doesn't prevent
# (process-level destructive actions, not filesystem writes)
_BLOCKED_PATTERNS = [
    "rm ",
    "dd if=",
    "mkfs",
    "kill ",
    "pkill",
    "reboot",
    "shutdown",
]


def execute_bash(command: str) -> str:
    """
    Run a bash command in the knowledge directory using restricted mode.

    bash -r (restricted) prevents:
      - Output redirections: >, >>, |tee, >&
      - Changing directories (cd)
      - Unsetting PATH / SHELL
      - Executing commands specified with absolute paths as command names

    The agent can still:
      - source test_helper.sh (relative path, no /)
      - Call curl, python3, etc. (looked up via PATH)
      - Use $() command substitution and pipe to python3 for parsing
    """
    for pattern in _BLOCKED_PATTERNS:
        if pattern in command:
            return f"ERROR: command blocked ('{pattern}' not allowed)"

    try:
        result = subprocess.run(
            ["bash", "-r", "-c", command],
            cwd=str(KNOWLEDGE_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return output.strip() if output.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: command timed out after 60s"
    except Exception as e:
        return f"ERROR: {e}"


def read_file(path: str) -> str:
    """Read a file from knowledge/ or its subdirectories."""
    # Normalise: strip leading "knowledge/" if the caller included it
    clean = path.lstrip("/")
    if clean.startswith("knowledge/"):
        clean = clean[len("knowledge/"):]

    target = (KNOWLEDGE_DIR / clean).resolve()

    # Safety: must stay inside KNOWLEDGE_DIR
    try:
        target.relative_to(KNOWLEDGE_DIR.resolve())
    except ValueError:
        return f"ERROR: path '{path}' is outside the knowledge directory"

    if not target.exists():
        return f"ERROR: file not found: {path}"
    if not target.is_file():
        return f"ERROR: path is not a file: {path}"

    try:
        return target.read_text()
    except Exception as e:
        return f"ERROR reading file: {e}"


# Anthropic tool definitions (raw JSON schema style)
TOOL_DEFINITIONS = [
    {
        "name": "bash",
        "description": (
            "Esegui un comando bash nella directory knowledge/ di Activepieces. "
            "Usa questo tool per: ottenere il token (source test_helper.sh && get_token), "
            "creare flow (create_flow), eseguire operazioni (flow_op), "
            "pubblicare (publish_and_enable), verificare i run, ecc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Il comando bash da eseguire",
                }
            },
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": (
            "Leggi il contenuto di un file dalla directory knowledge/. "
            "Usa questo tool per caricare i template JSON (es. 'templates/triggers/gmail_new_email_from_sender.json'), "
            "FLOW_SCHEMA.md, o qualsiasi altro file di riferimento. "
            "Il path è relativo alla cartella knowledge/."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path relativo alla directory knowledge/ (es. 'templates/actions/gmail_send_email.json')",
                }
            },
            "required": ["path"],
        },
    },
]


def dispatch_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatch a tool call and return the result as a string."""
    if tool_name == "bash":
        return execute_bash(tool_input.get("command", ""))
    elif tool_name == "read_file":
        return read_file(tool_input.get("path", ""))
    else:
        return f"ERROR: unknown tool '{tool_name}'"
