---
name: "cli-anything-activepieces"
description: "CLI harness for Activepieces automation platform — manage flows, connections, pieces, tables, and runs from the command line"
---

# cli-anything-activepieces

Control an Activepieces automation platform instance via structured CLI commands.

## Prerequisites

- Activepieces instance running (Docker, self-hosted, or cloud)
- API key configured via `AP_API_KEY` env var or `config init`

## Installation

```bash
cd activepieces/agent-harness && pip install -e .
```

## Command Groups

| Group | Description |
|-------|-------------|
| `config` | CLI configuration and profiles |
| `project` | Project management |
| `flow` | Flow CRUD, enable/disable, publish, export/import |
| `run` | Flow execution management, retry, cancel |
| `connection` | App integration connections |
| `piece` | Discover available pieces (280+) |
| `trigger` | Trigger events and testing |
| `table` | Table, field, record CRUD |
| `store` | Key-value store |
| `folder` | Flow folder organization |
| `platform` | Platform admin and API keys |

## Usage Examples

```bash
# List all flows as JSON
cli-anything-activepieces --json flow list

# Create a flow
cli-anything-activepieces --json flow create --name "Daily Report"

# Enable a flow
cli-anything-activepieces flow enable FLOW_ID

# Export a flow as template
cli-anything-activepieces flow export FLOW_ID -o template.json

# List recent runs
cli-anything-activepieces --json run list --flow-id FLOW_ID --limit 5

# Search for pieces
cli-anything-activepieces --json piece list --search slack

# Create a table with fields and records
cli-anything-activepieces --json table create --name "Leads"
cli-anything-activepieces --json table field create --table-id TID --name "Email" --type TEXT
cli-anything-activepieces --json table record create --table-id TID --cells '{"fld1":"user@example.com"}'
```

## Agent Guidance

- Use `--json` flag on all commands for machine-readable output
- All list commands return `{"data": [...], "next": "cursor|null"}` (SeekPage format)
- Use `--limit` and `--cursor` for pagination
- Configure via env vars: `AP_API_URL`, `AP_API_KEY`, `AP_PROJECT_ID`
- Flow operations use a discriminated union pattern: `enable`, `disable`, `publish` are separate commands
- Error responses include `code` and `params.message` fields
