"""Platform admin command group."""

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("platform")
def platform_group():
    """Platform administration (Enterprise)."""


@platform_group.command("get")
@click.argument("platform_id")
@click.pass_context
def platform_get(ctx, platform_id):
    """Get platform details."""
    client = ctx.obj["client"]
    data = client.get(f"/platforms/{platform_id}")
    print_output(data, as_json=ctx.obj.get("json", False))


@platform_group.command("update")
@click.argument("platform_id")
@click.option("--name", default=None, help="Platform name")
@click.pass_context
def platform_update(ctx, platform_id, name):
    """Update platform settings."""
    client = ctx.obj["client"]
    body = {}
    if name:
        body["name"] = name
    data = client.post(f"/platforms/{platform_id}", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Platform updated: {platform_id}")


@platform_group.group("api-key")
def api_key_group():
    """Manage platform API keys."""


@api_key_group.command("list")
@click.pass_context
def api_key_list(ctx):
    """List API keys."""
    client = ctx.obj["client"]
    data = client.get("/api-keys")
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Name", "Truncated Value", "Created"],
                 row_keys=["id", "displayName", "truncatedValue", "created"])


@api_key_group.command("create")
@click.option("--name", required=True, help="API key display name")
@click.pass_context
def api_key_create(ctx, name):
    """Create a new API key."""
    client = ctx.obj["client"]
    data = client.post("/api-keys", body={"displayName": name})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"API key created: {data.get('id', '')}")


@api_key_group.command("delete")
@click.argument("key_id")
@click.pass_context
def api_key_delete(ctx, key_id):
    """Delete an API key."""
    client = ctx.obj["client"]
    client.delete(f"/api-keys/{key_id}")
    print_success(f"API key deleted: {key_id}")
