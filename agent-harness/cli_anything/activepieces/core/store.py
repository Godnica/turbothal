"""Key-value store command group."""

import json as json_mod

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("store")
def store_group():
    """Key-value store operations (requires engine token)."""


@store_group.command("get")
@click.argument("key")
@click.pass_context
def store_get(ctx, key):
    """Get a store entry by key."""
    client = ctx.obj["client"]
    data = client.get("/store-entries", params={"key": key})
    print_output(data, as_json=ctx.obj.get("json", False))


@store_group.command("put")
@click.argument("key")
@click.argument("value")
@click.pass_context
def store_put(ctx, key, value):
    """Set a store entry."""
    client = ctx.obj["client"]
    try:
        parsed = json_mod.loads(value)
    except json_mod.JSONDecodeError:
        parsed = value
    data = client.post("/store-entries", body={"key": key, "value": parsed})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Store entry set: {key}")


@store_group.command("delete")
@click.argument("key")
@click.pass_context
def store_delete(ctx, key):
    """Delete a store entry."""
    client = ctx.obj["client"]
    client.delete("/store-entries", params={"key": key})
    print_success(f"Store entry deleted: {key}")
