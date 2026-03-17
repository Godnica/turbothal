# TEST.md — cli-anything-activepieces

## Test Inventory Plan

- `test_core.py`: ~80 unit tests planned
- `test_full_e2e.py`: ~30 E2E tests planned (requires running Activepieces server)

## Unit Test Plan

### utils/config.py
- Test init_config writes TOML file correctly
- Test resolve_config priority: CLI flags > env vars > file
- Test profile CRUD (create, list, delete)
- Test get_profile with non-existent profile falls back to default
- Test set_config_value for default and named profiles
- Edge cases: empty config, missing file, invalid keys

### utils/api_client.py
- Test ActivepiecesClient initialization (base_url construction)
- Test _headers includes Authorization
- Test get/post/delete methods (mocked HTTP)
- Test error handling (ActivepiecesError with status codes)
- Test paginate auto-follows cursor
- Edge cases: empty responses, missing fields, timeout

### utils/output.py
- Test format_json output
- Test format_table with various data
- Test print_output with dict, list, and SeekPage format
- Edge cases: empty data, long strings, missing keys

### utils/activepieces_backend.py
- Test check_health success
- Test check_health failure (server down)
- Test find_activepieces returns URL on success

### core/config_cmd.py (Click commands)
- Test config init creates file
- Test config show displays values
- Test config set modifies values
- Test profile create/list/delete

### core/project.py
- Test project list (mocked API response)
- Test project get
- Test project create
- Test project update
- Test project delete

### core/flow.py
- Test flow list with filters
- Test flow get / get with version
- Test flow create / delete
- Test flow enable / disable / publish
- Test flow export / import
- Test flow count

### core/run.py
- Test run list with filters
- Test run get
- Test run retry
- Test run cancel
- Test run bulk-retry

### core/connection.py
- Test connection list
- Test connection upsert
- Test connection update / delete

### core/piece.py
- Test piece list with search
- Test piece get
- Test piece categories

### core/trigger.py
- Test trigger events list / save
- Test trigger test / test-cancel

### core/table.py
- Test table list / get / create / update / delete / export
- Test field list / create / update / delete
- Test record list / get / create / update / delete

### core/store.py
- Test store get / put / delete

### core/folder.py
- Test folder list / get / create / update / delete

### core/platform.py
- Test platform get / update
- Test api-key list / create / delete

## E2E Test Plan

Requires a running Activepieces instance (AP_API_URL + AP_API_KEY set).

### Workflows to test:
1. **Full project lifecycle**: list → get → update
2. **Flow CRUD workflow**: create → get → enable → disable → export → delete
3. **Folder organization**: create folder → create flow in folder → list flows by folder → delete
4. **Connection management**: upsert → list → update → delete
5. **Table workflow**: create table → add field → add record → list records → export → delete
6. **Piece discovery**: list → search → get details
7. **CLI subprocess tests**: Run cli-anything-activepieces via subprocess for --help, --json, project list

## Realistic Workflow Scenarios

### Scenario 1: Automation Setup
- Create project
- List pieces to find integrations
- Create flow
- Enable flow
- Check run status

### Scenario 2: Data Management
- Create table
- Add text and number fields
- Insert records
- Query records
- Export table

### Scenario 3: Maintenance
- List all flows with status ENABLED
- Get run history for a specific flow
- Retry failed runs
- Archive old runs

---

## Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0

cli_anything/activepieces/tests/test_core.py::TestConfig::test_init_config_creates_file PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_resolve_config_cli_flags_highest_priority PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_resolve_config_env_vars_over_file PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_resolve_config_defaults PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_create_and_list_profiles PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_get_profile PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_get_profile_nonexistent_returns_default PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_delete_profile PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_delete_nonexistent_profile PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_set_config_value_default PASSED
cli_anything/activepieces/tests/test_core.py::TestConfig::test_set_config_value_profile PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_client_base_url PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_client_base_url_trailing_slash PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_headers_include_auth PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_headers_no_auth_when_empty PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_get_calls_request PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_post_calls_request PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_delete_calls_request PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_paginate_single_page PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_paginate_multiple_pages PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_paginate_with_limit PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_paginate_empty PASSED
cli_anything/activepieces/tests/test_core.py::TestApiClient::test_activepieces_error PASSED
cli_anything/activepieces/tests/test_core.py::TestOutput::test_format_json PASSED
cli_anything/activepieces/tests/test_core.py::TestOutput::test_format_table_basic PASSED
cli_anything/activepieces/tests/test_core.py::TestOutput::test_format_table_empty PASSED
cli_anything/activepieces/tests/test_core.py::TestOutput::test_format_table_truncation PASSED
cli_anything/activepieces/tests/test_core.py::TestOutput::test_print_output_json PASSED
cli_anything/activepieces/tests/test_core.py::TestOutput::test_print_output_seek_page PASSED
cli_anything/activepieces/tests/test_core.py::TestOutput::test_print_output_empty_list PASSED
cli_anything/activepieces/tests/test_core.py::TestBackend::test_check_health_failure PASSED
cli_anything/activepieces/tests/test_core.py::TestBackend::test_find_activepieces_failure PASSED
cli_anything/activepieces/tests/test_core.py::TestSession::test_session_init PASSED
cli_anything/activepieces/tests/test_core.py::TestSession::test_session_history PASSED
cli_anything/activepieces/tests/test_core.py::TestSession::test_session_prompt_context PASSED
cli_anything/activepieces/tests/test_core.py::TestSession::test_session_prompt_context_empty PASSED
cli_anything/activepieces/tests/test_core.py::TestConfigCLI::test_config_init PASSED
cli_anything/activepieces/tests/test_core.py::TestConfigCLI::test_config_show PASSED
cli_anything/activepieces/tests/test_core.py::TestConfigCLI::test_config_set PASSED
cli_anything/activepieces/tests/test_core.py::TestConfigCLI::test_profile_create_list_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestProjectCLI::test_project_list PASSED
cli_anything/activepieces/tests/test_core.py::TestProjectCLI::test_project_get PASSED
cli_anything/activepieces/tests/test_core.py::TestProjectCLI::test_project_create PASSED
cli_anything/activepieces/tests/test_core.py::TestProjectCLI::test_project_update PASSED
cli_anything/activepieces/tests/test_core.py::TestProjectCLI::test_project_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_list PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_get PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_create PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_enable PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_disable PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_publish PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_count PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_export PASSED
cli_anything/activepieces/tests/test_core.py::TestFlowCLI::test_flow_import PASSED
cli_anything/activepieces/tests/test_core.py::TestRunCLI::test_run_list PASSED
cli_anything/activepieces/tests/test_core.py::TestRunCLI::test_run_get PASSED
cli_anything/activepieces/tests/test_core.py::TestRunCLI::test_run_retry PASSED
cli_anything/activepieces/tests/test_core.py::TestRunCLI::test_run_cancel PASSED
cli_anything/activepieces/tests/test_core.py::TestRunCLI::test_run_bulk_retry PASSED
cli_anything/activepieces/tests/test_core.py::TestConnectionCLI::test_connection_list PASSED
cli_anything/activepieces/tests/test_core.py::TestConnectionCLI::test_connection_upsert PASSED
cli_anything/activepieces/tests/test_core.py::TestConnectionCLI::test_connection_update PASSED
cli_anything/activepieces/tests/test_core.py::TestConnectionCLI::test_connection_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestPieceCLI::test_piece_list PASSED
cli_anything/activepieces/tests/test_core.py::TestPieceCLI::test_piece_get PASSED
cli_anything/activepieces/tests/test_core.py::TestPieceCLI::test_piece_categories PASSED
cli_anything/activepieces/tests/test_core.py::TestTriggerCLI::test_trigger_events_list PASSED
cli_anything/activepieces/tests/test_core.py::TestTriggerCLI::test_trigger_events_save PASSED
cli_anything/activepieces/tests/test_core.py::TestTriggerCLI::test_trigger_test PASSED
cli_anything/activepieces/tests/test_core.py::TestTriggerCLI::test_trigger_test_cancel PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_table_list PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_table_get PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_table_create PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_table_update PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_table_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_table_export PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_field_list PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_field_create PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_field_update PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_field_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_record_list PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_record_get PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_record_create PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_record_update PASSED
cli_anything/activepieces/tests/test_core.py::TestTableCLI::test_record_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestStoreCLI::test_store_get PASSED
cli_anything/activepieces/tests/test_core.py::TestStoreCLI::test_store_put PASSED
cli_anything/activepieces/tests/test_core.py::TestStoreCLI::test_store_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestFolderCLI::test_folder_list PASSED
cli_anything/activepieces/tests/test_core.py::TestFolderCLI::test_folder_get PASSED
cli_anything/activepieces/tests/test_core.py::TestFolderCLI::test_folder_create PASSED
cli_anything/activepieces/tests/test_core.py::TestFolderCLI::test_folder_update PASSED
cli_anything/activepieces/tests/test_core.py::TestFolderCLI::test_folder_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestPlatformCLI::test_platform_get PASSED
cli_anything/activepieces/tests/test_core.py::TestPlatformCLI::test_platform_update PASSED
cli_anything/activepieces/tests/test_core.py::TestPlatformCLI::test_api_key_list PASSED
cli_anything/activepieces/tests/test_core.py::TestPlatformCLI::test_api_key_create PASSED
cli_anything/activepieces/tests/test_core.py::TestPlatformCLI::test_api_key_delete PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_version PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_flow_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_project_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_config_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_connection_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_table_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_piece_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_trigger_help PASSED
cli_anything/activepieces/tests/test_core.py::TestCLISubprocess::test_platform_help PASSED

============================= 109 passed in 2.00s ==============================
```

### Summary

| Category | Tests | Status |
|----------|-------|--------|
| Config (utils) | 11 | All passed |
| API Client | 12 | All passed |
| Output formatting | 7 | All passed |
| Backend discovery | 2 | All passed |
| Session | 4 | All passed |
| Config CLI | 4 | All passed |
| Project CLI | 5 | All passed |
| Flow CLI | 10 | All passed |
| Run CLI | 5 | All passed |
| Connection CLI | 4 | All passed |
| Piece CLI | 3 | All passed |
| Trigger CLI | 4 | All passed |
| Table/Field/Record CLI | 17 | All passed |
| Store CLI | 3 | All passed |
| Folder CLI | 5 | All passed |
| Platform CLI | 5 | All passed |
| CLI Subprocess | 10 | All passed |
| **TOTAL** | **109** | **100% pass rate** |
