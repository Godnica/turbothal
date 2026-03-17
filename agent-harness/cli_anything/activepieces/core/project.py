"""Project command group."""

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("project")
def project_group():
    """Manage Activepieces projects."""


@project_group.command("list")
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def project_list(ctx, limit, cursor):
    """List projects."""
    client = ctx.obj["client"]
    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    data = client.get("/projects", params=params)
    as_json = ctx.obj.get("json", False)
    print_output(data, as_json=as_json,
                 headers=["ID", "Name", "Created"],
                 row_keys=["id", "displayName", "created"])


@project_group.command("get")
@click.argument("project_id")
@click.pass_context
def project_get(ctx, project_id):
    """Get project details."""
    client = ctx.obj["client"]
    data = client.get(f"/projects/{project_id}")
    print_output(data, as_json=ctx.obj.get("json", False))


@project_group.command("create")
@click.option("--name", required=True, help="Project display name")
@click.option("--external-id", default=None)
@click.pass_context
def project_create(ctx, name, external_id):
    """Create a new project (Enterprise only)."""
    client = ctx.obj["client"]
    body = {"displayName": name}
    if external_id:
        body["externalId"] = external_id
    data = client.post("/projects", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Project created: {data.get('id', '')}")


@project_group.command("update")
@click.argument("project_id")
@click.option("--name", required=True, help="New display name")
@click.pass_context
def project_update(ctx, project_id, name):
    """Update a project."""
    client = ctx.obj["client"]
    data = client.post(f"/projects/{project_id}", body={"displayName": name})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Project updated: {project_id}")


@project_group.command("delete")
@click.argument("project_id")
@click.pass_context
def project_delete(ctx, project_id):
    """Delete a project (Enterprise only)."""
    client = ctx.obj["client"]
    client.delete(f"/projects/{project_id}")
    print_success(f"Project deleted: {project_id}")
