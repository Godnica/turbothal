# cli-anything-activepieces

CLI-Anything harness for **Activepieces** — control your automation platform from the command line.

## Prerequisites

- **Python 3.10+**
- **Activepieces** instance running (self-hosted or cloud)
- An **API key** from your Activepieces instance

## Installation

```bash
cd activepieces/agent-harness
pip install -e .
```

Verify:

```bash
which cli-anything-activepieces
cli-anything-activepieces --help
```

## Configuration

### Quick setup

```bash
cli-anything-activepieces config init
```

### Environment variables

```bash
export AP_API_URL="http://localhost:3000"
export AP_API_KEY="sk-your-api-key"
export AP_PROJECT_ID="your-project-id"
```

### CLI flags

```bash
cli-anything-activepieces --api-url http://localhost:3000 --api-key sk-xxx flow list
```

## Usage

### One-shot commands

```bash
# List flows
cli-anything-activepieces flow list

# JSON output for agents
cli-anything-activepieces --json flow list

# Get flow details
cli-anything-activepieces --json flow get FLOW_ID

# Create and manage flows
cli-anything-activepieces flow create --name "My Automation"
cli-anything-activepieces flow enable FLOW_ID
cli-anything-activepieces flow export FLOW_ID -o backup.json

# Manage connections
cli-anything-activepieces connection list
cli-anything-activepieces connection upsert --piece-name @ap/slack --display-name "Slack" --type SECRET_TEXT --value '{"token":"xoxb-..."}'

# Discover pieces
cli-anything-activepieces piece list --search gmail
cli-anything-activepieces --json piece get @activepieces/piece-gmail

# Tables
cli-anything-activepieces table create --name "Contacts"
cli-anything-activepieces table field create --table-id TID --name "Email" --type TEXT
cli-anything-activepieces table record create --table-id TID --cells '{"fld1":"alice@example.com"}'

# Flow runs
cli-anything-activepieces run list --flow-id FLOW_ID --status FAILED
cli-anything-activepieces run retry RUN_ID
```

### REPL mode

```bash
cli-anything-activepieces
```

Enters interactive mode with command history and styled output.

## Command Groups

| Command | Description |
|---------|-------------|
| `config` | Manage CLI configuration and profiles |
| `project` | Project CRUD |
| `flow` | Flow management (create, enable, disable, publish, export, import) |
| `run` | Flow run management (list, retry, cancel) |
| `connection` | App connection management |
| `piece` | Piece discovery and info |
| `trigger` | Trigger management and testing |
| `table` | Table, field, and record management |
| `store` | Key-value store operations |
| `folder` | Folder management |
| `platform` | Platform administration (Enterprise) |

## Running Tests

```bash
cd activepieces/agent-harness
python3 -m pytest cli_anything/activepieces/tests/ -v
```

Force-installed mode:

```bash
CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest cli_anything/activepieces/tests/ -v -s
```
