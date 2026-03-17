"""Config command group for cli-anything-activepieces."""

import click

from cli_anything.activepieces.utils.config import (
    init_config, resolve_config, list_profiles,
    create_profile, delete_profile, set_config_value, CONFIG_FILE,
)
from cli_anything.activepieces.utils.output import print_success, print_error


@click.group("config")
def config_group():
    """Manage CLI configuration (API URL, API key, profiles)."""


@config_group.command("init")
@click.option("--api-url", prompt="Activepieces API URL", default="http://localhost:3000")
@click.option("--api-key", prompt="API Key", hide_input=True)
@click.option("--project-id", default="", help="Default project ID")
def config_init(api_url, api_key, project_id):
    """Interactive setup — write config file."""
    init_config(api_url, api_key, project_id)
    print_success(f"Config saved to {CONFIG_FILE}")


@config_group.command("show")
@click.option("--profile", default=None, help="Show a specific profile")
@click.pass_context
def config_show(ctx, profile):
    """Display current resolved configuration."""
    cfg = resolve_config(profile=profile)
    masked_key = cfg["api_key"][:8] + "..." if len(cfg["api_key"]) > 8 else "***"
    click.echo(f"api_url:    {cfg['api_url']}")
    click.echo(f"api_key:    {masked_key}")
    click.echo(f"project_id: {cfg['project_id'] or '(not set)'}")
    click.echo(f"config:     {CONFIG_FILE}")


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--profile", default=None, help="Set in a specific profile")
def config_set(key, value, profile):
    """Set a configuration value."""
    set_config_value(key, value, profile)
    print_success(f"Set {key} = {value}")


@config_group.group("profile")
def profile_group():
    """Manage configuration profiles."""


@profile_group.command("list")
def profile_list():
    """List all profiles."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles configured.")
        return
    for p in profiles:
        click.echo(f"  - {p}")


@profile_group.command("create")
@click.argument("name")
@click.option("--api-url", required=True)
@click.option("--api-key", required=True)
@click.option("--project-id", default="")
def profile_create(name, api_url, api_key, project_id):
    """Create a new profile."""
    create_profile(name, api_url, api_key, project_id)
    print_success(f"Profile '{name}' created")


@profile_group.command("delete")
@click.argument("name")
def profile_delete(name):
    """Delete a profile."""
    if delete_profile(name):
        print_success(f"Profile '{name}' deleted")
    else:
        print_error(f"Profile '{name}' not found")
