# Task: Template Testing — Obiettivo 20 template per connettore

**Obiettivo**: Creare e testare template JSON per ogni trigger/azione dei principali connettori.
**Dove salvarli**: `knowledge/templates/triggers/` e `knowledge/templates/actions/`
**Email mittente**: account Google autenticato via OAuth (determinato dalla connessione dell'utente loggato)
**Email ricevente**: da specificare nel flow

---

## Legenda

- ✅ Testato e funzionante (template salvato)
- 🔧 Da testare (non richiede account esterno)
- ⏳ In attesa account (Slack, Discord, ecc. — skip fino a che Simone non dà credenziali)
- ❌ Non disponibile nell'istanza

---

## 1. CORE — Trigger & Azioni built-in

### Trigger

| # | Piece | Trigger | Status | Template file |
|---|-------|---------|--------|---------------|
| 1 | piece-webhook | catch_webhook | ✅ | triggers/webhook_catch.json |
| 2 | piece-schedule | every_hour | ✅ | triggers/schedule_every_hour.json |
| 3 | piece-schedule | every_x_minutes | ✅ | triggers/schedule_every_x_minutes.json |
| 4 | piece-schedule | every_day | ✅ | triggers/schedule_every_day.json |
| 5 | piece-schedule | every_week | ✅ | triggers/schedule_every_week.json |
| 6 | piece-schedule | every_month | ✅ | triggers/schedule_every_month.json |
| 7 | piece-schedule | cron_expression | ✅ | triggers/schedule_cron_expression.json |
| 8 | piece-rss | new-item | ✅ | triggers/rss_new_item.json |

### Azioni

| # | Piece | Azione | Status | Template file |
|---|-------|--------|--------|---------------|
| 9 | CODE | code custom JS | ✅ | actions/code_basic.json |
| 10 | piece-http | send_request (GET) | ✅ | actions/http_get.json |
| 11 | piece-http | send_request (POST) | ✅ | actions/http_post.json |
| 12 | piece-store | put | ✅ | actions/store_put.json |
| 13 | piece-store | get | ✅ | actions/store_get.json |
| 14 | piece-store | append | ✅ | actions/store_append.json |
| 15 | piece-store | remove_value | ✅ | actions/store_remove.json |
| 16 | piece-store | add_to_list | ✅ | actions/store_add_to_list.json |
| 17 | piece-store | remove_from_list | ✅ | actions/store_remove_from_list.json |
| 18 | piece-delay | delayFor | ✅ | actions/delay_for.json |
| 19 | piece-delay | delay_until | ✅ | actions/delay_until.json |
| 20 | piece-webhook | return_response | ✅ | actions/webhook_return_response.json |

---

## 2. FLOW CONTROL — Loop, Router, Approval

| # | Piece | Tipo | Status | Template file |
|---|-------|------|--------|---------------|
| 21 | LOOP_ON_ITEMS | loop su lista | ✅ | actions/loop_basic.json |
| 22 | ROUTER | if/else (2 branch) | ✅ | actions/router_if_else.json |
| 23 | ROUTER | switch (3+ branch) | ✅ | actions/router_switch.json |
| 24 | piece-approval | wait_for_approval | ✅ | actions/approval_wait.json |
| 25 | piece-approval | create_approval_links | ✅ | actions/approval_create_links.json |

---

## 3. TEXT / DATA HELPERS

| # | Piece | Azione | Status | Template file |
|---|-------|--------|--------|---------------|
| 26 | piece-text-helper | concat | ✅ | actions/text_concat.json |
| 27 | piece-text-helper | replace | ✅ | actions/text_replace.json |
| 28 | piece-text-helper | split | ✅ | actions/text_split.json |
| 29 | piece-text-helper | find | ✅ | actions/text_find.json |
| 30 | piece-text-helper | markdown_to_html | ✅ | actions/text_md_to_html.json |
| 31 | piece-text-helper | html_to_markdown | ✅ | actions/text_html_to_md.json |
| 32 | piece-date-helper | get_current_date | ✅ | actions/date_get_current.json |
| 33 | piece-date-helper | format_date | ✅ | actions/date_format.json |
| 34 | piece-date-helper | date_difference | ✅ | actions/date_difference.json |
| 35 | piece-date-helper | add_subtract_date | ✅ | actions/date_add_subtract.json |
| 36 | piece-math-helper | addition_math | ✅ | actions/math_addition.json |
| 37 | piece-math-helper | multiplication_math | ✅ | actions/math_multiply.json |
| 38 | piece-math-helper | generateRandom_math | ✅ | actions/math_random.json |
| 39 | piece-data-mapper | advanced_mapping | ✅ | actions/data_mapper.json |
| 40 | piece-csv | convert_csv_to_json | ✅ | actions/csv_to_json.json |
| 41 | piece-csv | convert_json_to_csv | ✅ | actions/json_to_csv.json |
| 42 | piece-json | convert_json_to_text | ✅ | actions/json_to_text.json |
| 43 | piece-json | convert_text_to_json | ✅ | actions/text_to_json.json |
| 44 | piece-xml | convert-json-to-xml | ✅ | actions/json_to_xml.json |

---

## 4. EMAIL — Gmail, SMTP, IMAP

**Mittente**: account Google autenticato via OAuth
**Ricevente**: da specificare nel flow

### Trigger

| # | Piece | Trigger | Status | Template file |
|---|-------|---------|--------|---------------|
| 45 | piece-gmail | gmail_new_email_received | ✅ | triggers/gmail_new_email.json |
| 46 | piece-gmail | new_labeled_email | ✅ | triggers/gmail_new_labeled_email.json |
| 47 | piece-gmail | new_attachment | ✅ | triggers/gmail_new_attachment.json |
| 48 | piece-gmail | new_label | ✅ | triggers/gmail_new_label.json |
| 49 | piece-imap | new_email | 🔧 Serve config IMAP | |

### Azioni

| # | Piece | Azione | Status | Template file |
|---|-------|--------|--------|---------------|
| 50 | piece-gmail | send_email | ✅ | actions/gmail_send_email.json |
| 51 | piece-gmail | reply_to_email | ✅ | actions/gmail_reply_to_email.json |
| 52 | piece-gmail | gmail_get_mail | ✅ | actions/gmail_get_mail.json |
| 53 | piece-gmail | gmail_search_mail | ✅ | actions/gmail_search_mail.json |
| 54 | piece-gmail | create_draft_reply | ✅ | actions/gmail_create_draft_reply.json |
| 55 | piece-smtp | send-email | 🔧 Serve config SMTP | |
| 56 | piece-imap | mark_email_read | 🔧 Serve config IMAP | |
| 57 | piece-imap | move_email | 🔧 Serve config IMAP | |
| 58 | piece-sendgrid | send_email | ⏳ Serve API key SendGrid | |
| 59 | piece-mailchimp | add_member_to_list | ⏳ Serve account Mailchimp | |

---

## 5. GOOGLE WORKSPACE — Sheets, Drive, Calendar, Contacts

**OAuth Google configurato** — Connection ID: recuperato dinamicamente via API (`/app-connections?pieceName=@activepieces/piece-gmail`)

### Google Sheets (v0.14.6) — 21 azioni ✅ + 4 trigger ✅

| # | Tipo | Nome | Status | Template |
|---|------|------|--------|----------|
| 59 | action | insert_row | ✅ | actions/gsheets_insert_row.json |
| 60 | action | insert-multiple-rows | ✅ | actions/gsheets_insert_multiple_rows.json |
| 61 | action | update_row | ✅ | actions/gsheets_update_row.json |
| 62 | action | update-multiple-rows | ✅ | actions/gsheets_update_multiple_rows.json |
| 63 | action | delete_row | ✅ | actions/gsheets_delete_row.json |
| 64 | action | find_rows | ✅ | actions/gsheets_find_rows.json |
| 65 | action | create-spreadsheet | ✅ | actions/gsheets_create_spreadsheet.json |
| 66 | action | create-worksheet | ✅ | actions/gsheets_create_worksheet.json |
| 67 | action | clear_sheet | ✅ | actions/gsheets_clear_sheet.json |
| 68 | action | delete-worksheet | ✅ | actions/gsheets_delete_worksheet.json |
| 69 | action | rename-worksheet | ✅ | actions/gsheets_rename_worksheet.json |
| 70 | action | format-row | ✅ | actions/gsheets_format_row.json |
| 71 | action | find_row_by_num | ✅ | actions/gsheets_find_row_by_num.json |
| 72 | action | get_next_rows | ✅ | actions/gsheets_get_next_rows.json |
| 73 | action | get-many-rows | ✅ | actions/gsheets_get_many_rows.json |
| 74 | action | find_spreadsheets | ✅ | actions/gsheets_find_spreadsheets.json |
| 75 | action | find-worksheet | ✅ | actions/gsheets_find_worksheet.json |
| 76 | action | copy-worksheet | ✅ | actions/gsheets_copy_worksheet.json |
| 77 | action | create-column | ✅ | actions/gsheets_create_column.json |
| 78 | action | export_sheet | ✅ | actions/gsheets_export_sheet.json |
| 79 | action | custom_api_call | ✅ | actions/gsheets_custom_api_call.json |
| 80-83 | trigger | new_row/updated_row/new_spreadsheet/new_worksheet | ✅ | triggers/gsheets_*.json |

### Google Drive (v0.7.1) — 16 azioni ✅ + 2 trigger ✅

| # | Tipo | Nome | Status | Template |
|---|------|------|--------|----------|
| 84-99 | action | create_folder/file, upload, read, get, list, search, duplicate, pdf, permissions, move, delete, trash, custom | ✅ | actions/gdrive_*.json |
| 100-101 | trigger | new_file, new_folder | ✅ | triggers/gdrive_*.json |

### Google Calendar (v0.9.0) — 9 azioni ✅ + 7 trigger ✅

| # | Tipo | Nome | Status | Template |
|---|------|------|--------|----------|
| 102-110 | action | add_attendees, quick_event, create_event, get_events, update, delete, busy_free, get_by_id, custom | ✅ | actions/gcal_*.json |
| 111-117 | trigger | new/updated/cancelled/starts_in/ends/search/new_calendar | ✅ | triggers/gcal_*.json |

### Google Contacts (v0.4.4) — 4 azioni ✅ + 1 trigger ✅

| # | Tipo | Nome | Status | Template |
|---|------|------|--------|----------|
| 118-121 | action | add_contact, update_contact, search_contact, custom | ✅ | actions/gcontacts_*.json |
| 122 | trigger | new_or_updated_contact | ✅ | triggers/gcontacts_*.json |

---

## 6. AI — OpenAI, Claude

| # | Piece | Azione | Status | Template file |
|---|-------|--------|--------|---------------|
| 75-82 | piece-openai / piece-claude | vari | ⏳ Serve API keys | |

---

## 7. MESSAGING — Slack, Discord, Telegram

| # | Piece | Tipo | Status | Template file |
|---|-------|------|--------|---------------|
| 83-92 | Slack/Discord/Telegram | vari | ⏳ Serve account/bot | |

---

## 8. PROJECT MANAGEMENT — GitHub, Linear, Notion, Todoist, Trello

| # | Piece | Tipo | Status | Template file |
|---|-------|------|--------|---------------|
| 93-95 | piece-github | trigger push/PR/issues | 🔧 Serve OAuth GitHub | |
| 96-106 | Linear/Notion/Todoist/Trello | vari | ⏳ Serve account | |

---

## 9-12. CRM, Database, Storage, Support

| Categoria | Status |
|-----------|--------|
| CRM (Stripe, Shopify, HubSpot) | ⏳ Serve account |
| Database (PostgreSQL) | ✅ 2 template (run_query + new_row trigger) — Connection ID: postgres-local-conn |
| File Storage (S3, Dropbox, SFTP) | ⏳ Serve account |
| Support (Zendesk, Intercom) | ⏳ Serve account |

---

## Riepilogo Aggiornato

| Categoria | Totale | ✅ Testati | 🔧 Testabili | ⏳ Serve account |
|-----------|--------|-----------|-------------|-----------------|
| Core | 20 | **20** | 0 | 0 |
| Flow Control | 5 | **5** | 0 | 0 |
| Text/Data | 19 | **19** | 0 | 0 |
| Email | 15 | **9** | 4 | 2 |
| Google Workspace | 64 | **64** | 0 | 0 |
| AI | 8 | 0 | 0 | 8 |
| Messaging | 10 | 0 | 0 | 10 |
| Project Mgmt | 14 | 0 | 3 | 11 |
| CRM & Commerce | 8 | 0 | 0 | 8 |
| Database | 4 | **2** | 0 | 2 |
| File Storage | 3 | 0 | 0 | 3 |
| Customer Support | 3 | 0 | 0 | 3 |
| **TOTALE** | **175** | **119** | **9** | **47** |

---

## Note Importanti Scoperte

1. **authType per webhook**: Il trigger `catch_webhook` richiede `"authType": "none"` nell'input, altrimenti `valid: false`
2. **store_scope per Store**: Tutte le azioni Store richiedono `"store_scope": "COLLECTION"` (o `"PROJECT"`)
3. **Nomi campi diversi**: `delimiter` non `separator` (text split), `expression` non `searchValue` (text find), `cronExpression` non `cron_expression` (schedule cron)
4. **run_on_weekends per every_day**: Campo required mancante nelle prime versioni
5. **DYNAMIC fields**: `return_response` ha `fields` come DYNAMIC che contiene `body`, `status`, `headers`
6. **markdown_to_html**: Richiede 7 campi required (`flavor`, `headerLevelStart`, `tables`, `noHeaderId`, `simpleLineBreaks`, `openLinksInNewWindow`)
7. **Worker socket timeout**: Se i worker perdono la connessione socket con l'app, i flow rimangono bloccati in ENABLING. Risolvere con `docker compose restart` o `docker compose down && up`
8. **Interpolazione — `.output` è IMPLICITO**:
   - ✅ `{{step_1.result}}` → accede a `step_1.output.result`
   - ❌ `{{step_1.output.result}}` → risolve a stringa vuota!
   - Per primitivi (math-helper → `68`): usare `{{step_X}}` direttamente
   - Per oggetti con `.result` (date-helper): usare `{{step_X.result}}`
9. **Flow testato end-to-end "Daily Digest Generator"**: Webhook → Date (get_current_date) → Math (random) → Text (concat con `{{step_1.result}}` e `{{step_2}}`) → Store (put). Funziona completamente con status SUCCEEDED

10. **Docker networking per OAuth**: Con `AP_FRONTEND_URL=http://localhost:8080` nel .env (per OAuth browser), i worker non potevano raggiungere l'app. Fix: override `AP_FRONTEND_URL=http://app:80` nel docker-compose.yml per ENTRAMBI i container app e worker. Il frontend usa `window.location.origin` per le API calls, non AP_FRONTEND_URL.
11. **Connessione OAuth condivisa**: Tutti i Google pieces (Gmail, Sheets, Drive, Calendar, Contacts) usano la stessa connessione CLOUD_OAUTH2. Non servono scopes aggiuntivi.
12. **custom_api_call**: In tutti i Google pieces, il campo `url` è di tipo DYNAMIC e deve essere `{"url": "https://..."}` (un dict), non una stringa semplice.
13. **PostgreSQL connection**: Tipo CUSTOM_AUTH con campi host/port/user/password/database/enable_ssl. L'host Docker interno è "postgres".

## Prossimi Step

**Fase 2 — COMPLETATA** ✅:
- ~~Gmail/Google (OAuth) → 73 template~~ FATTO
- ~~PostgreSQL (già in Docker) → 2 template~~ FATTO

**Fase 3 — Con account/API keys** (quando Simone fornisce):
- GitHub (OAuth) → ~3 template
- AI (OpenAI, Claude) → ~8 template
- Messaging (Slack, Discord, Telegram) → ~10 template
- CRM/Commerce → ~8 template
- Resto → ~14 template
