"""Flow run command group."""

import click

from cli_anything.activepieces.utils.output import print_output, print_success


@click.group("run")
def run_group():
    """Manage flow runs (executions)."""


@run_group.command("list")
@click.option("--flow-id", default=None, help="Filter by flow ID")
@click.option("--status", type=click.Choice([
    "RUNNING", "SUCCEEDED", "FAILED", "PAUSED", "STOPPED", "TIMEOUT", "INTERNAL_ERROR",
]), default=None)
@click.option("--limit", type=int, default=10)
@click.option("--cursor", default=None)
@click.option("--created-after", default=None, help="ISO date filter")
@click.option("--created-before", default=None, help="ISO date filter")
@click.pass_context
def run_list(ctx, flow_id, status, limit, cursor, created_after, created_before):
    """List flow runs."""
    client = ctx.obj["client"]
    params = {"limit": limit}
    if flow_id:
        params["flowId"] = flow_id
    if status:
        params["status"] = [status]
    if cursor:
        params["cursor"] = cursor
    if created_after:
        params["createdAfter"] = created_after
    if created_before:
        params["createdBefore"] = created_before
    data = client.get("/flow-runs", params=params)
    print_output(data, as_json=ctx.obj.get("json", False),
                 headers=["ID", "Flow ID", "Status", "Duration(s)", "Created"],
                 row_keys=["id", "flowId", "status", "duration", "created"])


@run_group.command("get")
@click.argument("run_id")
@click.pass_context
def run_get(ctx, run_id):
    """Get flow run details."""
    client = ctx.obj["client"]
    data = client.get(f"/flow-runs/{run_id}")
    print_output(data, as_json=ctx.obj.get("json", False))


@run_group.command("retry")
@click.argument("run_id")
@click.option("--strategy", type=click.Choice(["FROM_FAILED_STEP", "RESTART"]), default="FROM_FAILED_STEP")
@click.pass_context
def run_retry(ctx, run_id, strategy):
    """Retry a failed flow run."""
    client = ctx.obj["client"]
    data = client.post(f"/flow-runs/{run_id}/retry", body={"strategy": strategy})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Run retry initiated: {run_id}")


@run_group.command("cancel")
@click.option("--ids", required=True, help="Comma-separated run IDs")
@click.pass_context
def run_cancel(ctx, ids):
    """Cancel running flow runs."""
    client = ctx.obj["client"]
    run_ids = [i.strip() for i in ids.split(",")]
    data = client.post("/flow-runs/cancel", body={"flowRunIds": run_ids})
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Cancelled {len(run_ids)} run(s)")


@run_group.command("bulk-retry")
@click.option("--ids", required=True, help="Comma-separated run IDs")
@click.option("--strategy", type=click.Choice(["FROM_FAILED_STEP", "RESTART"]), default="FROM_FAILED_STEP")
@click.pass_context
def run_bulk_retry(ctx, ids, strategy):
    """Bulk retry multiple flow runs."""
    client = ctx.obj["client"]
    run_ids = [i.strip() for i in ids.split(",")]
    data = client.post("/flow-runs/retry", body={
        "flowRunIds": run_ids,
        "strategy": strategy,
    })
    print_output(data, as_json=ctx.obj.get("json", False))
    print_success(f"Bulk retry initiated for {len(run_ids)} run(s)")
