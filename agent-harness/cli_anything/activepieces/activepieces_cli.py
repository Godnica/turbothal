"""Main CLI entry point for cli-anything-activepieces."""

from __future__ import annotations

import shlex
import sys

import click

from cli_anything.activepieces.utils.api_client import ActivepiecesClient, ActivepiecesError
from cli_anything.activepieces.utils.config import resolve_config
from cli_anything.activepieces.utils.output import print_error
from cli_anything.activepieces.core.config_cmd import config_group
from cli_anything.activepieces.core.project import project_group
from cli_anything.activepieces.core.flow import flow_group
from cli_anything.activepieces.core.run import run_group
from cli_anything.activepieces.core.connection import connection_group
from cli_anything.activepieces.core.piece import piece_group
from cli_anything.activepieces.core.trigger import trigger_group
from cli_anything.activepieces.core.table import table_group
from cli_anything.activepieces.core.store import store_group
from cli_anything.activepieces.core.folder import folder_group
from cli_anything.activepieces.core.platform import platform_group


@click.group(invoke_without_command=True)
@click.option("--api-url", envvar="AP_API_URL", default=None, help="Activepieces API URL")
@click.option("--api-key", envvar="AP_API_KEY", default=None, help="API key")
@click.option("--project-id", envvar="AP_PROJECT_ID", default=None, help="Project ID")
@click.option("--profile", default=None, help="Config profile name")
@click.option("--json", "use_json", is_flag=True, default=False, help="JSON output mode")
@click.version_option("1.0.0", prog_name="cli-anything-activepieces")
@click.pass_context
def cli(ctx, api_url, api_key, project_id, profile, use_json):
    """CLI-Anything Activepieces — Control Activepieces from the command line.

    Run without a subcommand to enter interactive REPL mode.
    """
    ctx.ensure_object(dict)
    cfg = resolve_config(api_url, api_key, project_id, profile)
    ctx.obj["config"] = cfg
    ctx.obj["json"] = use_json
    ctx.obj["client"] = ActivepiecesClient(
        api_url=cfg["api_url"],
        api_key=cfg["api_key"],
        project_id=cfg["project_id"] or None,
    )

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# Register command groups
cli.add_command(config_group)
cli.add_command(project_group)
cli.add_command(flow_group)
cli.add_command(run_group)
cli.add_command(connection_group)
cli.add_command(piece_group)
cli.add_command(trigger_group)
cli.add_command(table_group)
cli.add_command(store_group)
cli.add_command(folder_group)
cli.add_command(platform_group)


@cli.command(hidden=True)
@click.pass_context
def repl(ctx):
    """Interactive REPL mode."""
    try:
        from cli_anything.activepieces.utils.repl_skin import ReplSkin
    except ImportError:
        ReplSkin = None

    if ReplSkin:
        skin = ReplSkin("activepieces", version="1.0.0")
        skin.print_banner()
    else:
        click.echo("cli-anything-activepieces v1.0.0")
        click.echo("Type 'help' for commands, 'exit' to quit.\n")

    commands = {name: cmd.get_short_help_str() for name, cmd in cli.commands.items() if name != "repl"}

    if ReplSkin:
        skin.help(commands)
        pt_session = skin.create_prompt_session()

    while True:
        try:
            if ReplSkin:
                line = skin.get_input(pt_session, project_name=ctx.obj["config"].get("project_id", "")[:8] or None)
            else:
                line = input("activepieces> ").strip()
        except (EOFError, KeyboardInterrupt):
            if ReplSkin:
                skin.print_goodbye()
            else:
                click.echo("\nGoodbye!")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            if ReplSkin:
                skin.print_goodbye()
            else:
                click.echo("Goodbye!")
            break
        if line.lower() == "help":
            if ReplSkin:
                skin.help(commands)
            else:
                for name, desc in commands.items():
                    click.echo(f"  {name:15s} {desc}")
            continue

        try:
            args = shlex.split(line)
        except ValueError as e:
            print_error(f"Parse error: {e}")
            continue

        # Propagate global flags
        if ctx.obj.get("json"):
            args = ["--json"] + args

        try:
            cli.main(args=args, standalone_mode=False, **{"parent": ctx})
        except SystemExit:
            pass
        except ActivepiecesError as e:
            print_error(str(e))
        except click.ClickException as e:
            e.show()
        except Exception as e:
            print_error(f"Error: {e}")


def main():
    """Entry point for console_scripts."""
    try:
        cli(standalone_mode=True)
    except ActivepiecesError as e:
        print_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
