"""Flow command group."""

import json as json_mod

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("flow")
def flow_group():
    """Manage automation flows."""


@flow_group.command("list")
@click.option("--status", type=click.Choice(["ENABLED", "DISABLED"]), default=None)
@click.option("--name", default=None, help="Filter by name")
@click.option("--folder-id", default=None)
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def flow_list(ctx, status, name, folder_id, limit, cursor):
    """List flows."""
    client = ctx.obj["client"]
    params = {"limit": limit}
    if status:
        params["status"] = status
    if name:
        params["name"] = name
    if folder_id:
        params["folderId"] = folder_id
    if cursor:
        params["cursor"] = cursor
    data = client.get("/flows", params=params)
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Name", "Status", "Updated"],
                 row_keys=["id", "version.displayName", "status", "updated"])


@flow_group.command("get")
@click.argument("flow_id")
@click.option("--version-id", default=None)
@click.pass_context
def flow_get(ctx, flow_id, version_id):
    """Get flow details."""
    client = ctx.obj["client"]
    params = {}
    if version_id:
        params["versionId"] = version_id
    data = client.get(f"/flows/{flow_id}", params=params)
    print_output(data, as_json=ctx.obj.get("json", False))


@flow_group.command("create")
@click.option("--name", required=True, help="Flow display name")
@click.option("--folder-id", default=None)
@click.pass_context
def flow_create(ctx, name, folder_id):
    """Create a new flow."""
    client = ctx.obj["client"]
    body = {"displayName": name}
    if folder_id:
        body["folderId"] = folder_id
    data = client.post("/flows", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Flow created: {data.get('id', '')}")


@flow_group.command("delete")
@click.argument("flow_id")
@click.pass_context
def flow_delete(ctx, flow_id):
    """Delete a flow."""
    client = ctx.obj["client"]
    client.delete(f"/flows/{flow_id}")
    print_success(f"Flow deleted: {flow_id}")


@flow_group.command("enable")
@click.argument("flow_id")
@click.pass_context
def flow_enable(ctx, flow_id):
    """Enable a flow."""
    client = ctx.obj["client"]
    body = {"type": "CHANGE_STATUS", "request": {"status": "ENABLED"}}
    data = client.post(f"/flows/{flow_id}", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Flow enabled: {flow_id}")


@flow_group.command("disable")
@click.argument("flow_id")
@click.pass_context
def flow_disable(ctx, flow_id):
    """Disable a flow."""
    client = ctx.obj["client"]
    body = {"type": "CHANGE_STATUS", "request": {"status": "DISABLED"}}
    data = client.post(f"/flows/{flow_id}", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Flow disabled: {flow_id}")


@flow_group.command("publish")
@click.argument("flow_id")
@click.pass_context
def flow_publish(ctx, flow_id):
    """Lock and publish a flow."""
    client = ctx.obj["client"]
    body = {"type": "LOCK_AND_PUBLISH", "request": {}}
    data = client.post(f"/flows/{flow_id}", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Flow published: {flow_id}")


@flow_group.command("export")
@click.argument("flow_id")
@click.option("-o", "--output", "output_file", default=None, help="Output file path")
@click.pass_context
def flow_export(ctx, flow_id, output_file):
    """Export a flow as a JSON template."""
    client = ctx.obj["client"]
    data = client.get(f"/flows/{flow_id}/template")
    content = json_mod.dumps(data, indent=2)
    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        print_success(f"Flow exported to {output_file}")
    else:
        print(content)


@flow_group.command("import")
@click.argument("flow_id")
@click.option("--file", "import_file", required=True, help="JSON template file")
@click.pass_context
def flow_import(ctx, flow_id, import_file):
    """Import a flow from a JSON template."""
    client = ctx.obj["client"]
    with open(import_file) as f:
        template = json_mod.load(f)
    body = {"type": "IMPORT_FLOW", "request": template}
    data = client.post(f"/flows/{flow_id}", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Flow imported: {flow_id}")


@flow_group.command("count")
@click.option("--folder-id", default=None)
@click.pass_context
def flow_count(ctx, folder_id):
    """Count flows."""
    client = ctx.obj["client"]
    params = {}
    if folder_id:
        params["folderId"] = folder_id
    data = client.get("/flows/count", params=params)
    if ctx.obj.get("json", False):
        print_output(data, as_json=True)
    else:
        click.echo(f"Total flows: {data}")
