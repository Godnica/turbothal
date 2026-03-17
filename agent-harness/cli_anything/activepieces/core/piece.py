"""Piece discovery command group."""

import click

from cli_anything.activepieces.utils.output import print_output


@click.group("piece")
def piece_group():
    """Discover and inspect available pieces (integrations)."""


@piece_group.command("list")
@click.option("--search", default=None, help="Search by name")
@click.option("--categories", default=None, help="Comma-separated categories")
@click.option("--include-hidden", is_flag=True, default=False)
@click.option("--sort-by", default=None)
@click.option("--order-by", type=click.Choice(["ASC", "DESC"]), default=None)
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def piece_list(ctx, search, categories, include_hidden, sort_by, order_by, limit, cursor):
    """List available pieces."""
    client = ctx.obj["client"]
    params = {"limit": limit}
    if search:
        params["searchQuery"] = search
    if categories:
        params["categories"] = categories.split(",")
    if include_hidden:
        params["includeHidden"] = "true"
    if sort_by:
        params["sortBy"] = sort_by
    if order_by:
        params["orderBy"] = order_by
    if cursor:
        params["cursor"] = cursor
    data = client.get("/pieces", params=params)
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["Name", "Display Name", "Version", "Categories"],
                 row_keys=["name", "displayName", "version", "categories"])


@piece_group.command("get")
@click.argument("name")
@click.option("--version", default=None)
@click.pass_context
def piece_get(ctx, name, version):
    """Get piece details."""
    client = ctx.obj["client"]
    params = {}
    if version:
        params["version"] = version
    data = client.get(f"/pieces/{name}", params=params)
    print_output(data, as_json=ctx.obj.get("json", False))


@piece_group.command("categories")
@click.pass_context
def piece_categories(ctx):
    """List piece categories."""
    client = ctx.obj["client"]
    data = client.get("/pieces/categories")
    print_output(data, as_json=ctx.obj.get("json", False))
