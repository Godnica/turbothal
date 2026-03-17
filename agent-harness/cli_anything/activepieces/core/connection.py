"""App connection command group."""

import json as json_mod

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("connection")
def connection_group():
    """Manage app connections (integrations)."""


@connection_group.command("list")
@click.option("--piece-name", default=None, help="Filter by piece name")
@click.option("--status", type=click.Choice(["ACTIVE", "ERROR", "MISSING"]), default=None)
@click.option("--display-name", default=None)
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def connection_list(ctx, piece_name, status, display_name, limit, cursor):
    """List app connections."""
    client = ctx.obj["client"]
    params = {"limit": limit}
    if piece_name:
        params["pieceName"] = piece_name
    if status:
        params["status"] = status
    if display_name:
        params["displayName"] = display_name
    if cursor:
        params["cursor"] = cursor
    data = client.get("/app-connections", params=params)
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Name", "Piece", "Status", "Updated"],
                 row_keys=["id", "displayName", "pieceName", "status", "updated"])


@connection_group.command("upsert")
@click.option("--piece-name", required=True)
@click.option("--display-name", required=True)
@click.option("--type", "conn_type", required=True, help="Connection type (e.g., SECRET_TEXT, OAUTH2)")
@click.option("--value", required=True, help="Connection value as JSON")
@click.option("--external-id", default=None)
@click.pass_context
def connection_upsert(ctx, piece_name, display_name, conn_type, value, external_id):
    """Create or update a connection."""
    client = ctx.obj["client"]
    body = {
        "pieceName": piece_name,
        "displayName": display_name,
        "type": conn_type,
        "value": json_mod.loads(value),
    }
    if external_id:
        body["externalId"] = external_id
    data = client.post("/app-connections", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Connection upserted: {data.get('id', '')}")


@connection_group.command("update")
@click.argument("connection_id")
@click.option("--display-name", required=True)
@click.pass_context
def connection_update(ctx, connection_id, display_name):
    """Update a connection's display name."""
    client = ctx.obj["client"]
    data = client.post(f"/app-connections/{connection_id}", body={"displayName": display_name})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Connection updated: {connection_id}")


@connection_group.command("delete")
@click.argument("connection_id")
@click.pass_context
def connection_delete(ctx, connection_id):
    """Delete a connection."""
    client = ctx.obj["client"]
    client.delete(f"/app-connections/{connection_id}")
    print_success(f"Connection deleted: {connection_id}")
