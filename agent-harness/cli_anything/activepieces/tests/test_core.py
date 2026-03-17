"""Unit tests for cli-anything-activepieces (synthetic data, no server required)."""

import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from cli_anything.activepieces.utils.api_client import ActivepiecesClient, ActivepiecesError
from cli_anything.activepieces.utils.config import (
    init_config, resolve_config, list_profiles,
    create_profile, delete_profile, set_config_value, get_profile,
    CONFIG_FILE, CONFIG_DIR,
)
from cli_anything.activepieces.utils.output import format_json, format_table, print_output
from cli_anything.activepieces.utils.activepieces_backend import check_health, find_activepieces
from cli_anything.activepieces.core.session import Session
from cli_anything.activepieces.activepieces_cli import cli


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Redirect config to temp dir."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    cfg_file = cfg_dir / "config.toml"
    monkeypatch.setattr("cli_anything.activepieces.utils.config.CONFIG_DIR", cfg_dir)
    monkeypatch.setattr("cli_anything.activepieces.utils.config.CONFIG_FILE", cfg_file)
    return cfg_file


@pytest.fixture
def mock_client():
    """Create a mock ActivepiecesClient."""
    client = MagicMock(spec=ActivepiecesClient)
    return client


def invoke_cli(runner, args, mock_response=None, mock_client=None):
    """Helper to invoke CLI with mocked API client."""
    def fake_cli_setup(ctx, api_url, api_key, project_id, profile, use_json):
        ctx.ensure_object(dict)
        ctx.obj["config"] = {"api_url": "http://test", "api_key": "sk-test", "project_id": ""}
        ctx.obj["json"] = use_json
        c = mock_client or MagicMock(spec=ActivepiecesClient)
        if mock_response is not None:
            c.get.return_value = mock_response
            c.post.return_value = mock_response
            c.delete.return_value = {}
        ctx.obj["client"] = c

    with patch.object(cli, "invoke", side_effect=None):
        pass

    return runner.invoke(cli, args, catch_exceptions=False)


# ============================================================
# utils/config.py tests
# ============================================================

class TestConfig:
    def test_init_config_creates_file(self, tmp_config):
        init_config("http://localhost:3000", "sk-123", "proj-1")
        assert tmp_config.exists()
        content = tmp_config.read_text()
        assert "http://localhost:3000" in content
        assert "sk-123" in content

    def test_resolve_config_cli_flags_highest_priority(self, tmp_config):
        init_config("http://file", "file-key")
        cfg = resolve_config(cli_api_url="http://cli", cli_api_key="cli-key")
        assert cfg["api_url"] == "http://cli"
        assert cfg["api_key"] == "cli-key"

    def test_resolve_config_env_vars_over_file(self, tmp_config, monkeypatch):
        init_config("http://file", "file-key")
        monkeypatch.setenv("AP_API_URL", "http://env")
        monkeypatch.setenv("AP_API_KEY", "env-key")
        cfg = resolve_config()
        assert cfg["api_url"] == "http://env"
        assert cfg["api_key"] == "env-key"

    def test_resolve_config_defaults(self, tmp_config):
        cfg = resolve_config()
        assert cfg["api_url"] == "http://localhost:3000"
        assert cfg["api_key"] == ""

    def test_create_and_list_profiles(self, tmp_config):
        create_profile("staging", "http://staging", "sk-stg")
        create_profile("prod", "http://prod", "sk-prd")
        profiles = list_profiles()
        assert "staging" in profiles
        assert "prod" in profiles

    def test_get_profile(self, tmp_config):
        create_profile("dev", "http://dev", "sk-dev", "proj-dev")
        prof = get_profile("dev")
        assert prof["api_url"] == "http://dev"
        assert prof["project_id"] == "proj-dev"

    def test_get_profile_nonexistent_returns_default(self, tmp_config):
        init_config("http://default", "default-key")
        prof = get_profile("nonexistent")
        assert prof["api_url"] == "http://default"

    def test_delete_profile(self, tmp_config):
        create_profile("temp", "http://temp", "sk-temp")
        assert delete_profile("temp")
        assert "temp" not in list_profiles()

    def test_delete_nonexistent_profile(self, tmp_config):
        assert not delete_profile("nope")

    def test_set_config_value_default(self, tmp_config):
        init_config("http://x", "sk-x")
        set_config_value("api_url", "http://updated")
        cfg = resolve_config()
        assert cfg["api_url"] == "http://updated"

    def test_set_config_value_profile(self, tmp_config):
        create_profile("test", "http://old", "sk-old")
        set_config_value("api_url", "http://new", profile="test")
        prof = get_profile("test")
        assert prof["api_url"] == "http://new"


# ============================================================
# utils/api_client.py tests
# ============================================================

class TestApiClient:
    def test_client_base_url(self):
        c = ActivepiecesClient("http://localhost:3000", "sk-test")
        assert c.base_url == "http://localhost:3000/api/v1"

    def test_client_base_url_trailing_slash(self):
        c = ActivepiecesClient("http://localhost:3000/", "sk-test")
        assert c.base_url == "http://localhost:3000/api/v1"

    def test_headers_include_auth(self):
        c = ActivepiecesClient("http://test", "sk-abc")
        h = c._headers()
        assert h["Authorization"] == "Bearer sk-abc"
        assert h["Content-Type"] == "application/json"

    def test_headers_no_auth_when_empty(self):
        c = ActivepiecesClient("http://test", "")
        h = c._headers()
        assert "Authorization" not in h

    def test_get_calls_request(self):
        c = ActivepiecesClient("http://test", "sk-test")
        with patch.object(c, "_request", return_value={"data": []}) as m:
            result = c.get("/flows", params={"limit": 10})
            m.assert_called_once_with("GET", "/flows", params={"limit": 10})
            assert result == {"data": []}

    def test_post_calls_request(self):
        c = ActivepiecesClient("http://test", "sk-test")
        with patch.object(c, "_request", return_value={"id": "123"}) as m:
            result = c.post("/flows", body={"name": "test"})
            m.assert_called_once_with("POST", "/flows", params=None, body={"name": "test"})
            assert result["id"] == "123"

    def test_delete_calls_request(self):
        c = ActivepiecesClient("http://test", "sk-test")
        with patch.object(c, "_request", return_value={}) as m:
            c.delete("/flows/123")
            m.assert_called_once_with("DELETE", "/flows/123", params=None)

    def test_paginate_single_page(self):
        c = ActivepiecesClient("http://test", "sk-test")
        with patch.object(c, "get", return_value={"data": [{"id": "1"}, {"id": "2"}], "next": None}):
            items = list(c.paginate("/flows"))
            assert len(items) == 2

    def test_paginate_multiple_pages(self):
        c = ActivepiecesClient("http://test", "sk-test")
        pages = [
            {"data": [{"id": "1"}], "next": "cursor1"},
            {"data": [{"id": "2"}], "next": None},
        ]
        with patch.object(c, "get", side_effect=pages):
            items = list(c.paginate("/flows"))
            assert len(items) == 2
            assert items[0]["id"] == "1"
            assert items[1]["id"] == "2"

    def test_paginate_with_limit(self):
        c = ActivepiecesClient("http://test", "sk-test")
        with patch.object(c, "get", return_value={"data": [{"id": "1"}, {"id": "2"}, {"id": "3"}], "next": "c"}):
            items = list(c.paginate("/flows", limit=2))
            assert len(items) == 2

    def test_paginate_empty(self):
        c = ActivepiecesClient("http://test", "sk-test")
        with patch.object(c, "get", return_value={"data": [], "next": None}):
            items = list(c.paginate("/flows"))
            assert len(items) == 0

    def test_activepieces_error(self):
        err = ActivepiecesError(404, "ENTITY_NOT_FOUND", "Flow not found")
        assert err.status == 404
        assert err.code == "ENTITY_NOT_FOUND"
        assert "Flow not found" in str(err)


# ============================================================
# utils/output.py tests
# ============================================================

class TestOutput:
    def test_format_json(self):
        result = format_json({"key": "value"})
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_format_table_basic(self):
        headers = ["ID", "Name"]
        rows = [["1", "Alice"], ["2", "Bob"]]
        result = format_table(headers, rows)
        assert "ID" in result
        assert "Alice" in result
        assert "Bob" in result

    def test_format_table_empty(self):
        result = format_table(["ID"], [])
        assert result == "(no results)"

    def test_format_table_truncation(self):
        headers = ["Value"]
        rows = [["x" * 100]]
        result = format_table(headers, rows, max_col_width=10)
        assert len(result.split("\n")[2].strip()) <= 10

    def test_print_output_json(self, capsys):
        print_output({"id": "123"}, as_json=True)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["id"] == "123"

    def test_print_output_seek_page(self, capsys):
        print_output(
            {"data": [{"id": "1", "name": "A"}]},
            as_json=False,
            headers=["ID", "Name"],
            row_keys=["id", "name"],
        )
        out = capsys.readouterr().out
        assert "1" in out
        assert "A" in out

    def test_print_output_empty_list(self, capsys):
        print_output([], as_json=False)
        out = capsys.readouterr().out
        assert "no results" in out


# ============================================================
# utils/activepieces_backend.py tests
# ============================================================

class TestBackend:
    def test_check_health_failure(self):
        with pytest.raises(RuntimeError, match="Cannot reach Activepieces"):
            check_health("http://localhost:99999")

    def test_find_activepieces_failure(self):
        with pytest.raises(RuntimeError):
            find_activepieces("http://localhost:99999")


# ============================================================
# core/session.py tests
# ============================================================

class TestSession:
    def test_session_init(self):
        s = Session(project_id="proj-1")
        assert s.project_id == "proj-1"
        assert not s.output_json

    def test_session_history(self):
        s = Session()
        s.push_history("flow list")
        s.push_history("flow get x")
        assert len(s.history) == 2

    def test_session_prompt_context(self):
        s = Session(project_id="abcdef1234567890")
        assert "[abcdef12]" in s.get_prompt_context()

    def test_session_prompt_context_empty(self):
        s = Session()
        assert s.get_prompt_context() == ""


# ============================================================
# CLI command tests (Click runner with mocked client)
# ============================================================

class TestConfigCLI:
    def test_config_init(self, runner, tmp_config):
        result = runner.invoke(cli, ["config", "init", "--api-url", "http://test", "--api-key", "sk-x"], input="\n")
        assert result.exit_code == 0

    def test_config_show(self, runner, tmp_config):
        init_config("http://test", "sk-testkey123")
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "http://test" in result.output

    def test_config_set(self, runner, tmp_config):
        init_config("http://old", "sk-old")
        result = runner.invoke(cli, ["config", "set", "api_url", "http://new"])
        assert result.exit_code == 0

    def test_profile_create_list_delete(self, runner, tmp_config):
        result = runner.invoke(cli, ["config", "profile", "create", "dev",
                                     "--api-url", "http://dev", "--api-key", "sk-dev"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["config", "profile", "list"])
        assert "dev" in result.output

        result = runner.invoke(cli, ["config", "profile", "delete", "dev"])
        assert result.exit_code == 0


class _MockedCLIBase:
    """Base for CLI tests with mocked API client."""

    def _invoke(self, runner, args, mock_response):
        """Invoke CLI command with mocked HTTP response."""
        client = MagicMock(spec=ActivepiecesClient)
        client.get.return_value = mock_response
        client.post.return_value = mock_response
        client.delete.return_value = {}

        def patched_resolve(*a, **kw):
            return {"api_url": "http://test", "api_key": "sk-test", "project_id": ""}

        with patch("cli_anything.activepieces.activepieces_cli.resolve_config", patched_resolve), \
             patch("cli_anything.activepieces.activepieces_cli.ActivepiecesClient", return_value=client):
            return runner.invoke(cli, args, catch_exceptions=False), client


class TestProjectCLI(_MockedCLIBase):
    def test_project_list(self, runner):
        result, client = self._invoke(runner, ["--json", "project", "list"], {
            "data": [{"id": "p1", "displayName": "My Project", "created": "2024-01-01"}]
        })
        assert result.exit_code == 0
        assert "p1" in result.output

    def test_project_get(self, runner):
        result, client = self._invoke(runner, ["--json", "project", "get", "p1"], {
            "id": "p1", "displayName": "My Project"
        })
        assert result.exit_code == 0
        assert "My Project" in result.output

    def test_project_create(self, runner):
        result, client = self._invoke(runner, ["--json", "project", "create", "--name", "New"], {
            "id": "p2", "displayName": "New"
        })
        assert result.exit_code == 0
        client.post.assert_called_once()

    def test_project_update(self, runner):
        result, client = self._invoke(runner, ["--json", "project", "update", "p1", "--name", "Renamed"], {
            "id": "p1", "displayName": "Renamed"
        })
        assert result.exit_code == 0

    def test_project_delete(self, runner):
        result, client = self._invoke(runner, ["project", "delete", "p1"], {})
        assert result.exit_code == 0
        client.delete.assert_called_once()


class TestFlowCLI(_MockedCLIBase):
    def test_flow_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "flow", "list"], {
            "data": [{"id": "f1", "version": {"displayName": "Test"}, "status": "ENABLED", "updated": "2024-01-01"}]
        })
        assert result.exit_code == 0
        assert "f1" in result.output

    def test_flow_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "flow", "get", "f1"], {
            "id": "f1", "version": {"displayName": "My Flow"}
        })
        assert result.exit_code == 0

    def test_flow_create(self, runner):
        result, client = self._invoke(runner, ["--json", "flow", "create", "--name", "Test"], {
            "id": "f2", "version": {"displayName": "Test"}
        })
        assert result.exit_code == 0
        client.post.assert_called_once()

    def test_flow_delete(self, runner):
        result, client = self._invoke(runner, ["flow", "delete", "f1"], {})
        assert result.exit_code == 0

    def test_flow_enable(self, runner):
        result, client = self._invoke(runner, ["--json", "flow", "enable", "f1"], {
            "id": "f1", "status": "ENABLED"
        })
        assert result.exit_code == 0
        call_body = client.post.call_args[1].get("body") or client.post.call_args[0][1] if len(client.post.call_args[0]) > 1 else None
        # Verify the call was made
        client.post.assert_called_once()

    def test_flow_disable(self, runner):
        result, _ = self._invoke(runner, ["--json", "flow", "disable", "f1"], {
            "id": "f1", "status": "DISABLED"
        })
        assert result.exit_code == 0

    def test_flow_publish(self, runner):
        result, _ = self._invoke(runner, ["--json", "flow", "publish", "f1"], {"id": "f1"})
        assert result.exit_code == 0

    def test_flow_count(self, runner):
        result, _ = self._invoke(runner, ["--json", "flow", "count"], 42)
        assert result.exit_code == 0

    def test_flow_export(self, runner, tmp_path):
        out = str(tmp_path / "flow.json")
        result, _ = self._invoke(runner, ["flow", "export", "f1", "-o", out], {
            "template": {"steps": []}
        })
        assert result.exit_code == 0
        assert os.path.exists(out)

    def test_flow_import(self, runner, tmp_path):
        tpl = tmp_path / "tpl.json"
        tpl.write_text('{"steps": []}')
        result, client = self._invoke(runner, ["--json", "flow", "import", "f1", "--file", str(tpl)], {"id": "f1"})
        assert result.exit_code == 0


class TestRunCLI(_MockedCLIBase):
    def test_run_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "run", "list"], {
            "data": [{"id": "r1", "flowId": "f1", "status": "SUCCEEDED", "duration": 5, "created": "2024-01-01"}]
        })
        assert result.exit_code == 0

    def test_run_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "run", "get", "r1"], {"id": "r1", "status": "SUCCEEDED"})
        assert result.exit_code == 0

    def test_run_retry(self, runner):
        result, client = self._invoke(runner, ["--json", "run", "retry", "r1"], {"id": "r1"})
        assert result.exit_code == 0

    def test_run_cancel(self, runner):
        result, client = self._invoke(runner, ["run", "cancel", "--ids", "r1,r2"], {})
        assert result.exit_code == 0

    def test_run_bulk_retry(self, runner):
        result, _ = self._invoke(runner, ["--json", "run", "bulk-retry", "--ids", "r1,r2"], {})
        assert result.exit_code == 0


class TestConnectionCLI(_MockedCLIBase):
    def test_connection_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "connection", "list"], {
            "data": [{"id": "c1", "displayName": "Gmail", "pieceName": "@ap/google-mail", "status": "ACTIVE", "updated": "2024-01-01"}]
        })
        assert result.exit_code == 0

    def test_connection_upsert(self, runner):
        result, client = self._invoke(runner, [
            "--json", "connection", "upsert",
            "--piece-name", "@ap/google-mail",
            "--display-name", "Gmail",
            "--type", "SECRET_TEXT",
            "--value", '{"secret": "abc"}'
        ], {"id": "c2"})
        assert result.exit_code == 0

    def test_connection_update(self, runner):
        result, _ = self._invoke(runner, ["--json", "connection", "update", "c1", "--display-name", "New Name"], {"id": "c1"})
        assert result.exit_code == 0

    def test_connection_delete(self, runner):
        result, client = self._invoke(runner, ["connection", "delete", "c1"], {})
        assert result.exit_code == 0


class TestPieceCLI(_MockedCLIBase):
    def test_piece_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "piece", "list"], {
            "data": [{"name": "@ap/gmail", "displayName": "Gmail", "version": "1.0", "categories": ["communication"]}]
        })
        assert result.exit_code == 0

    def test_piece_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "piece", "get", "@ap/gmail"], {
            "name": "@ap/gmail", "displayName": "Gmail"
        })
        assert result.exit_code == 0

    def test_piece_categories(self, runner):
        result, _ = self._invoke(runner, ["--json", "piece", "categories"], ["communication", "productivity"])
        assert result.exit_code == 0


class TestTriggerCLI(_MockedCLIBase):
    def test_trigger_events_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "trigger", "events", "list", "--flow-id", "f1"], {
            "data": [{"id": "te1", "flowId": "f1", "created": "2024-01-01"}]
        })
        assert result.exit_code == 0

    def test_trigger_events_save(self, runner):
        result, _ = self._invoke(runner, ["--json", "trigger", "events", "save", "--flow-id", "f1", "--data", '{"key": "val"}'], {})
        assert result.exit_code == 0

    def test_trigger_test(self, runner):
        result, _ = self._invoke(runner, ["--json", "trigger", "test", "--flow-id", "f1", "--flow-version-id", "fv1"], {})
        assert result.exit_code == 0

    def test_trigger_test_cancel(self, runner):
        result, client = self._invoke(runner, ["trigger", "test-cancel", "--flow-id", "f1"], {})
        assert result.exit_code == 0


class TestTableCLI(_MockedCLIBase):
    def test_table_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "list"], {
            "data": [{"id": "t1", "name": "Users", "created": "2024-01-01"}]
        })
        assert result.exit_code == 0

    def test_table_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "get", "t1"], {"id": "t1", "name": "Users"})
        assert result.exit_code == 0

    def test_table_create(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "create", "--name", "Orders"], {"id": "t2", "name": "Orders"})
        assert result.exit_code == 0

    def test_table_update(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "update", "t1", "--name", "Customers"], {"id": "t1"})
        assert result.exit_code == 0

    def test_table_delete(self, runner):
        result, client = self._invoke(runner, ["table", "delete", "t1"], {})
        assert result.exit_code == 0

    def test_table_export(self, runner, tmp_path):
        out = str(tmp_path / "export.json")
        result, _ = self._invoke(runner, ["table", "export", "t1", "-o", out], {"rows": []})
        assert result.exit_code == 0
        assert os.path.exists(out)

    # Field tests
    def test_field_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "field", "list", "--table-id", "t1"], {
            "data": [{"id": "fld1", "name": "Email", "type": "TEXT"}]
        })
        assert result.exit_code == 0

    def test_field_create(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "field", "create", "--table-id", "t1", "--name", "Age", "--type", "NUMBER"], {
            "id": "fld2"
        })
        assert result.exit_code == 0

    def test_field_update(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "field", "update", "fld1", "--name", "Full Name"], {"id": "fld1"})
        assert result.exit_code == 0

    def test_field_delete(self, runner):
        result, client = self._invoke(runner, ["table", "field", "delete", "fld1"], {})
        assert result.exit_code == 0

    # Record tests
    def test_record_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "record", "list", "--table-id", "t1"], {
            "data": [{"id": "rec1", "cells": {}}]
        })
        assert result.exit_code == 0

    def test_record_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "record", "get", "rec1"], {"id": "rec1"})
        assert result.exit_code == 0

    def test_record_create(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "record", "create",
                                          "--table-id", "t1", "--cells", '{"fld1": "Alice"}'], {"id": "rec2"})
        assert result.exit_code == 0

    def test_record_update(self, runner):
        result, _ = self._invoke(runner, ["--json", "table", "record", "update", "rec1",
                                          "--table-id", "t1", "--cells", '{"fld1": "Bob"}'], {"id": "rec1"})
        assert result.exit_code == 0

    def test_record_delete(self, runner):
        result, client = self._invoke(runner, ["table", "record", "delete", "--ids", "rec1,rec2"], {})
        assert result.exit_code == 0


class TestStoreCLI(_MockedCLIBase):
    def test_store_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "store", "get", "my_key"], {"key": "my_key", "value": "hello"})
        assert result.exit_code == 0

    def test_store_put(self, runner):
        result, _ = self._invoke(runner, ["--json", "store", "put", "my_key", '"hello"'], {"key": "my_key"})
        assert result.exit_code == 0

    def test_store_delete(self, runner):
        result, client = self._invoke(runner, ["store", "delete", "my_key"], {})
        assert result.exit_code == 0


class TestFolderCLI(_MockedCLIBase):
    def test_folder_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "folder", "list"], {
            "data": [{"id": "fol1", "displayName": "Production", "created": "2024-01-01"}]
        })
        assert result.exit_code == 0

    def test_folder_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "folder", "get", "fol1"], {"id": "fol1"})
        assert result.exit_code == 0

    def test_folder_create(self, runner):
        result, _ = self._invoke(runner, ["--json", "folder", "create", "--name", "Dev"], {"id": "fol2"})
        assert result.exit_code == 0

    def test_folder_update(self, runner):
        result, _ = self._invoke(runner, ["--json", "folder", "update", "fol1", "--name", "Staging"], {"id": "fol1"})
        assert result.exit_code == 0

    def test_folder_delete(self, runner):
        result, client = self._invoke(runner, ["folder", "delete", "fol1"], {})
        assert result.exit_code == 0


class TestPlatformCLI(_MockedCLIBase):
    def test_platform_get(self, runner):
        result, _ = self._invoke(runner, ["--json", "platform", "get", "plt1"], {"id": "plt1", "name": "My Platform"})
        assert result.exit_code == 0

    def test_platform_update(self, runner):
        result, _ = self._invoke(runner, ["--json", "platform", "update", "plt1", "--name", "Updated"], {"id": "plt1"})
        assert result.exit_code == 0

    def test_api_key_list(self, runner):
        result, _ = self._invoke(runner, ["--json", "platform", "api-key", "list"], {
            "data": [{"id": "ak1", "displayName": "Main", "truncatedValue": "sk-...", "created": "2024-01-01"}]
        })
        assert result.exit_code == 0

    def test_api_key_create(self, runner):
        result, _ = self._invoke(runner, ["--json", "platform", "api-key", "create", "--name", "CI Key"], {"id": "ak2"})
        assert result.exit_code == 0

    def test_api_key_delete(self, runner):
        result, client = self._invoke(runner, ["platform", "api-key", "delete", "ak1"], {})
        assert result.exit_code == 0


# ============================================================
# CLI subprocess tests
# ============================================================

class TestCLISubprocess:
    """Test the installed CLI command via subprocess."""

    @staticmethod
    def _resolve_cli(name):
        import shutil
        force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
        path = shutil.which(name)
        if path:
            print(f"[_resolve_cli] Using installed command: {path}")
            return [path]
        if force:
            raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
        module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
        print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
        return [sys.executable, "-m", module]

    CLI_BASE = None

    @pytest.fixture(autouse=True)
    def _setup_cli(self):
        self.CLI_BASE = self._resolve_cli("cli-anything-activepieces")

    def _run(self, args, check=True):
        import subprocess
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True, text=True,
            check=check,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "CLI-Anything Activepieces" in result.stdout

    def test_version(self):
        result = self._run(["--version"])
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_flow_help(self):
        result = self._run(["flow", "--help"])
        assert result.returncode == 0
        assert "list" in result.stdout

    def test_project_help(self):
        result = self._run(["project", "--help"])
        assert result.returncode == 0

    def test_config_help(self):
        result = self._run(["config", "--help"])
        assert result.returncode == 0
        assert "init" in result.stdout

    def test_connection_help(self):
        result = self._run(["connection", "--help"])
        assert result.returncode == 0

    def test_table_help(self):
        result = self._run(["table", "--help"])
        assert result.returncode == 0
        assert "field" in result.stdout
        assert "record" in result.stdout

    def test_piece_help(self):
        result = self._run(["piece", "--help"])
        assert result.returncode == 0

    def test_trigger_help(self):
        result = self._run(["trigger", "--help"])
        assert result.returncode == 0

    def test_platform_help(self):
        result = self._run(["platform", "--help"])
        assert result.returncode == 0
