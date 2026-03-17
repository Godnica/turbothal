"""Trigger command group."""

import json as json_mod

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("trigger")
def trigger_group():
    """Manage triggers and trigger events."""


@trigger_group.group("events")
def trigger_events():
    """Manage trigger events."""


@trigger_events.command("list")
@click.option("--flow-id", required=True)
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.pass_context
def events_list(ctx, flow_id, limit, cursor):
    """List trigger events for a flow."""
    client = ctx.obj["client"]
    params = {"flowId": flow_id, "limit": limit}
    if cursor:
        params["cursor"] = cursor
    data = client.get("/trigger-events", params=params)
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Flow ID", "Created"],
                 row_keys=["id", "flowId", "created"])


@trigger_events.command("save")
@click.option("--flow-id", required=True)
@click.option("--data", required=True, help="Event data as JSON")
@click.pass_context
def events_save(ctx, flow_id, data):
    """Save a trigger event."""
    client = ctx.obj["client"]
    body = {"flowId": flow_id, "data": json_mod.loads(data)}
    result = client.post("/trigger-events", body=body)
    print_output(result, as_json=ctx.obj.get("json", False))
    print_success("Trigger event saved")


@trigger_group.command("test")
@click.option("--flow-id", required=True)
@click.option("--flow-version-id", required=True)
@click.option("--strategy", type=click.Choice(["SIMULATE", "TEST_FUNCTION", "WEBHOOK"]), default="TEST_FUNCTION")
@click.pass_context
def trigger_test(ctx, flow_id, flow_version_id, strategy):
    """Test a trigger."""
    client = ctx.obj["client"]
    body = {
        "flowId": flow_id,
        "flowVersionId": flow_version_id,
        "testStrategy": strategy,
    }
    data = client.post("/test-trigger", body=body)
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success("Trigger test initiated")


@trigger_group.command("test-cancel")
@click.option("--flow-id", required=True)
@click.pass_context
def trigger_test_cancel(ctx, flow_id):
    """Cancel a trigger test."""
    client = ctx.obj["client"]
    client.delete("/test-trigger", params={"flowId": flow_id})
    print_success(f"Trigger test cancelled for flow: {flow_id}")
