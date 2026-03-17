# ACTIVEPIECES.md — Software-Specific SOP

## Software Overview

**Activepieces** is an open-source automation platform (alternative to Zapier/Make).
It provides a visual flow builder for creating automations using 280+ integrations (pieces).

## Architecture

- **Backend**: Fastify 5 + TypeORM + PostgreSQL (or SQLite)
- **Frontend**: React 18 + Vite
- **Execution**: BullMQ job queue + sandboxed engine
- **Auth**: Bearer token (API key) via `Authorization` header

## Backend Integration

The CLI wraps the Activepieces REST API at `/api/v1/`.

**Key patterns:**
- Pagination: SeekPage (`{data: [], next: cursor|null}`)
- Updates: `POST /:id` (not PUT/PATCH)
- Flow operations: Discriminated union body with `type` field
- Auth: `Authorization: Bearer <API_KEY>`

## API Endpoint Map

| Resource | Endpoint | Operations |
|----------|----------|------------|
| Projects | `/v1/projects` | GET, POST, DELETE |
| Flows | `/v1/flows` | GET, POST, DELETE + operations |
| Flow Runs | `/v1/flow-runs` | GET + retry/cancel/archive |
| Connections | `/v1/app-connections` | GET, POST, DELETE |
| Pieces | `/v1/pieces` | GET |
| Triggers | `/v1/trigger-events`, `/v1/test-trigger` | GET, POST, DELETE |
| Tables | `/v1/tables`, `/v1/fields`, `/v1/records` | Full CRUD |
| Store | `/v1/store-entries` | GET, POST, DELETE |
| Folders | `/v1/folders` | Full CRUD |
| Platform | `/v1/platforms`, `/v1/api-keys` | GET, POST, DELETE |

## Real Software Dependency

The Activepieces server is a **hard dependency**. The CLI is a structured interface
TO the running Activepieces instance, not a replacement. If the server is not reachable,
commands fail with clear error messages and install instructions.
