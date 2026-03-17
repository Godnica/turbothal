"""Folder command group."""

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("folder")
def folder_group():
    """Manage folders for organizing flows."""


@folder_group.command("list")
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def folder_list(ctx, limit, cursor):
    """List folders."""
    client = ctx.obj["client"]
    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    data = client.get("/folders", params=params)
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Name", "Created"],
                 row_keys=["id", "displayName", "created"])


@folder_group.command("get")
@click.argument("folder_id")
@click.pass_context
def folder_get(ctx, folder_id):
    """Get folder details."""
    client = ctx.obj["client"]
    data = client.get(f"/folders/{folder_id}")
    print_output(data, as_json=ctx.obj.get("json", False))


@folder_group.command("create")
@click.option("--name", required=True, help="Folder display name")
@click.pass_context
def folder_create(ctx, name):
    """Create a folder."""
    client = ctx.obj["client"]
    data = client.post("/folders", body={"displayName": name})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Folder created: {data.get('id', '')}")


@folder_group.command("update")
@click.argument("folder_id")
@click.option("--name", required=True, help="New display name")
@click.pass_context
def folder_update(ctx, folder_id, name):
    """Update a folder."""
    client = ctx.obj["client"]
    data = client.post(f"/folders/{folder_id}", body={"displayName": name})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Folder updated: {folder_id}")


@folder_group.command("delete")
@click.argument("folder_id")
@click.pass_context
def folder_delete(ctx, folder_id):
    """Delete a folder."""
    client = ctx.obj["client"]
    client.delete(f"/folders/{folder_id}")
    print_success(f"Folder deleted: {folder_id}")
