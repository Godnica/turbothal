"""Table command group (tables, fields, records)."""

import json as json_mod

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("table")
def table_group():
    """Manage tables, fields, and records."""


# --- Table CRUD ---

@table_group.command("list")
@click.option("--name", default=None)
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def table_list(ctx, name, limit, cursor):
    """List tables."""
    client = ctx.obj["client"]
    params = {"limit": limit}
    if name:
        params["name"] = name
    if cursor:
        params["cursor"] = cursor
    data = client.get("/tables", params=params)
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Name", "Created"],
                 row_keys=["id", "name", "created"])


@table_group.command("get")
@click.argument("table_id")
@click.pass_context
def table_get(ctx, table_id):
    """Get table details."""
    client = ctx.obj["client"]
    data = client.get(f"/tables/{table_id}")
    print_output(data, as_json=ctx.obj.get("json", False))


@table_group.command("create")
@click.option("--name", required=True)
@click.pass_context
def table_create(ctx, name):
    """Create a new table."""
    client = ctx.obj["client"]
    data = client.post("/tables", body={"name": name})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Table created: {data.get('id', '')}")


@table_group.command("update")
@click.argument("table_id")
@click.option("--name", required=True)
@click.pass_context
def table_update(ctx, table_id, name):
    """Update a table."""
    client = ctx.obj["client"]
    data = client.post(f"/tables/{table_id}", body={"name": name})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Table updated: {table_id}")


@table_group.command("delete")
@click.argument("table_id")
@click.pass_context
def table_delete(ctx, table_id):
    """Delete a table."""
    client = ctx.obj["client"]
    client.delete(f"/tables/{table_id}")
    print_success(f"Table deleted: {table_id}")


@table_group.command("export")
@click.argument("table_id")
@click.option("-o", "--output", "output_file", default=None)
@click.pass_context
def table_export(ctx, table_id, output_file):
    """Export table data."""
    client = ctx.obj["client"]
    data = client.get(f"/tables/{table_id}/export")
    content = json_mod.dumps(data, indent=2)
    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        print_success(f"Table exported to {output_file}")
    else:
        print(content)


# --- Field subcommands ---

@table_group.group("field")
def field_group():
    """Manage table fields (columns)."""


@field_group.command("list")
@click.option("--table-id", required=True)
@click.pass_context
def field_list(ctx, table_id):
    """List fields for a table."""
    client = ctx.obj["client"]
    data = client.get("/fields", params={"tableId": table_id})
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Name", "Type"],
                 row_keys=["id", "name", "type"])


@field_group.command("create")
@click.option("--table-id", required=True)
@click.option("--name", required=True)
@click.option("--type", "field_type", required=True, help="Field type (TEXT, NUMBER, DATE, etc.)")
@click.pass_context
def field_create(ctx, table_id, name, field_type):
    """Create a field in a table."""
    client = ctx.obj["client"]
    data = client.post("/fields", body={
        "tableId": table_id,
        "name": name,
        "type": field_type,
    })
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Field created: {data.get('id', '')}")


@field_group.command("update")
@click.argument("field_id")
@click.option("--name", default=None)
@click.pass_context
def field_update(ctx, field_id, name):
    """Update a field."""
    client = ctx.obj["client"]
    body = {}
    if name:
        body["name"] = name
    data = client.post(f"/fields/{field_id}", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Field updated: {field_id}")


@field_group.command("delete")
@click.argument("field_id")
@click.pass_context
def field_delete(ctx, field_id):
    """Delete a field."""
    client = ctx.obj["client"]
    client.delete(f"/fields/{field_id}")
    print_success(f"Field deleted: {field_id}")


# --- Record subcommands ---

@table_group.group("record")
def record_group():
    """Manage table records (rows)."""


@record_group.command("list")
@click.option("--table-id", required=True)
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def record_list(ctx, table_id, limit, cursor):
    """List records in a table."""
    client = ctx.obj["client"]
    params = {"tableId": table_id, "limit": limit}
    if cursor:
        params["cursor"] = cursor
    data = client.get("/records", params=params)
    print_output(data, as_json=ctx.obj.get("json", False))


@record_group.command("get")
@click.argument("record_id")
@click.pass_context
def record_get(ctx, record_id):
    """Get a record."""
    client = ctx.obj["client"]
    data = client.get(f"/records/{record_id}")
    print_output(data, as_json=ctx.obj.get("json", False))


@record_group.command("create")
@click.option("--table-id", required=True)
@click.option("--cells", required=True, help="Cell data as JSON")
@click.pass_context
def record_create(ctx, table_id, cells):
    """Create a record in a table."""
    client = ctx.obj["client"]
    data = client.post("/records", body={
        "tableId": table_id,
        "cells": json_mod.loads(cells),
    })
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Record created: {data.get('id', '')}")


@record_group.command("update")
@click.argument("record_id")
@click.option("--table-id", required=True)
@click.option("--cells", required=True, help="Updated cell data as JSON")
@click.pass_context
def record_update(ctx, record_id, table_id, cells):
    """Update a record."""
    client = ctx.obj["client"]
    data = client.post(f"/records/{record_id}", body={
        "tableId": table_id,
        "cells": json_mod.loads(cells),
    })
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Record updated: {record_id}")


@record_group.command("delete")
@click.option("--ids", required=True, help="Comma-separated record IDs")
@click.pass_context
def record_delete(ctx, ids):
    """Delete records."""
    client = ctx.obj["client"]
    record_ids = [i.strip() for i in ids.split(",")]
    client.delete("/records", params={"ids": ",".join(record_ids)})
    print_success(f"Deleted {len(record_ids)} record(s)")
