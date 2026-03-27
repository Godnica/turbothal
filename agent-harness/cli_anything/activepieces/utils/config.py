"""Configuration management for cli-anything-activepieces."""

import os
import tomllib
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "activepieces"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def _save_config(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    default = data.get("default", {})
    if default:
        lines.append("[default]")
        for k, v in default.items():
            lines.append(f'{k} = "{v}"')
        lines.append("")
    profiles = data.get("profiles", {})
    for name, prof in profiles.items():
        lines.append(f"[profiles.{name}]")
        for k, v in prof.items():
            lines.append(f'{k} = "{v}"')
        lines.append("")
    CONFIG_FILE.write_text("\n".join(lines) + "\n")


def get_profile(name: str | None = None) -> dict:
    cfg = _load_config()
    if name and name in cfg.get("profiles", {}):
        return cfg["profiles"][name]
    return cfg.get("default", {})


def list_profiles() -> list[str]:
    cfg = _load_config()
    return list(cfg.get("profiles", {}).keys())


def resolve_config(cli_api_url=None, cli_api_key=None, cli_project_id=None, profile=None) -> dict:
    """Resolve config from CLI flags > env vars > config file."""
    file_cfg = get_profile(profile)
    return {
        "api_url": (
            cli_api_url
            or os.environ.get("AP_API_URL")
            or file_cfg.get("api_url", "http://localhost:3000")
        ),
        "api_key": (
            cli_api_key
            or os.environ.get("AP_API_KEY")
            or file_cfg.get("api_key", "")
        ),
        "project_id": (
            cli_project_id
            or os.environ.get("AP_PROJECT_ID")
            or file_cfg.get("project_id", "")
        ),
        "email": os.environ.get("AP_EMAIL") or file_cfg.get("email", ""),
        "password": os.environ.get("AP_PASSWORD") or file_cfg.get("password", ""),
    }


def init_config(api_url: str, api_key: str, project_id: str = "", email: str = "", password: str = "") -> None:
    cfg = _load_config()
    cfg.setdefault("default", {})
    cfg["default"]["api_url"] = api_url
    cfg["default"]["api_key"] = api_key
    if project_id:
        cfg["default"]["project_id"] = project_id
    if email:
        cfg["default"]["email"] = email
    if password:
        cfg["default"]["password"] = password
    _save_config(cfg)


def set_config_value(key: str, value: str, profile: str | None = None) -> None:
    cfg = _load_config()
    if profile:
        cfg.setdefault("profiles", {}).setdefault(profile, {})[key] = value
    else:
        cfg.setdefault("default", {})[key] = value
    _save_config(cfg)


def create_profile(name: str, api_url: str, api_key: str, project_id: str = "") -> None:
    cfg = _load_config()
    cfg.setdefault("profiles", {})[name] = {
        "api_url": api_url,
        "api_key": api_key,
    }
    if project_id:
        cfg["profiles"][name]["project_id"] = project_id
    _save_config(cfg)


def delete_profile(name: str) -> bool:
    cfg = _load_config()
    if name in cfg.get("profiles", {}):
        del cfg["profiles"][name]
        _save_config(cfg)
        return True
    return False
