# Task: Template Testing — Obiettivo 20 template per connettore

**Obiettivo**: Creare e testare template JSON per ogni trigger/azione dei principali connettori.
**Dove salvarli**: `knowledge/templates/triggers/` e `knowledge/templates/actions/`
**Email mittente**: simonemiticonicastri@gmail.com
**Email ricevente**: nicastrisimo@gmail.com

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

**Mittente**: simonemiticonicastri@gmail.com
**Ricevente**: nicastrisimo@gmail.com

### Trigger

| # | Piece | Trigger | Status | Template file |
|---|-------|---------|--------|---------------|
| 45 | piece-gmail | gmail_new_email_received | 🔧 Serve OAuth Google | |
| 46 | piece-gmail | new_labeled_email | 🔧 Serve OAuth Google | |
| 47 | piece-gmail | new_attachment | 🔧 Serve OAuth Google | |
| 48 | piece-imap | new_email | 🔧 Serve config IMAP | |

### Azioni

| # | Piece | Azione | Status | Template file |
|---|-------|--------|--------|---------------|
| 49 | piece-gmail | send_email | 🔧 Serve OAuth Google | |
| 50 | piece-gmail | reply_to_email | 🔧 Serve OAuth Google | |
| 51 | piece-gmail | gmail_get_mail | 🔧 Serve OAuth Google | |
| 52 | piece-gmail | gmail_search_mail | 🔧 Serve OAuth Google | |
| 53 | piece-gmail | create_draft_reply | 🔧 Serve OAuth Google | |
| 54 | piece-smtp | send-email | 🔧 Serve config SMTP | |
| 55 | piece-imap | mark_email_read | 🔧 Serve config IMAP | |
| 56 | piece-imap | move_email | 🔧 Serve config IMAP | |
| 57 | piece-sendgrid | send_email | ⏳ Serve API key SendGrid | |
| 58 | piece-mailchimp | add_member_to_list | ⏳ Serve account Mailchimp | |

---

## 5. GOOGLE WORKSPACE — Sheets, Drive, Calendar, Contacts

**Nota**: Richiede OAuth Google — testabile con l'account di Simone.

| # | Piece | Tipo | Status | Template file |
|---|-------|------|--------|---------------|
| 59-74 | Google Sheets/Drive/Calendar/Contacts | vari | 🔧 Serve OAuth Google | |

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
| Database (PostgreSQL) | 🔧 Già in Docker |
| File Storage (S3, Dropbox, SFTP) | ⏳ Serve account |
| Support (Zendesk, Intercom) | ⏳ Serve account |

---

## Riepilogo Aggiornato

| Categoria | Totale | ✅ Testati | 🔧 Testabili | ⏳ Serve account |
|-----------|--------|-----------|-------------|-----------------|
| Core | 20 | **20** | 0 | 0 |
| Flow Control | 5 | **5** | 0 | 0 |
| Text/Data | 19 | **19** | 0 | 0 |
| Email | 14 | 0 | 12 | 2 |
| Google Workspace | 16 | 0 | 16 | 0 |
| AI | 8 | 0 | 0 | 8 |
| Messaging | 10 | 0 | 0 | 10 |
| Project Mgmt | 14 | 0 | 3 | 11 |
| CRM & Commerce | 8 | 0 | 0 | 8 |
| Database | 4 | 0 | 2 | 2 |
| File Storage | 3 | 0 | 0 | 3 |
| Customer Support | 3 | 0 | 0 | 3 |
| **TOTALE** | **124** | **44** | **33** | **47** |

---

## Note Importanti Scoperte

1. **authType per webhook**: Il trigger `catch_webhook` richiede `"authType": "none"` nell'input, altrimenti `valid: false`
2. **store_scope per Store**: Tutte le azioni Store richiedono `"store_scope": "COLLECTION"` (o `"PROJECT"`)
3. **Nomi campi diversi**: `delimiter` non `separator` (text split), `expression` non `searchValue` (text find), `cronExpression` non `cron_expression` (schedule cron)
4. **run_on_weekends per every_day**: Campo required mancante nelle prime versioni
5. **DYNAMIC fields**: `return_response` ha `fields` come DYNAMIC che contiene `body`, `status`, `headers`
6. **markdown_to_html**: Richiede 7 campi required (`flavor`, `headerLevelStart`, `tables`, `noHeaderId`, `simpleLineBreaks`, `openLinksInNewWindow`)
7. **Worker socket timeout**: Se i worker perdono la connessione socket con l'app, i flow rimangono bloccati in ENABLING. Risolvere con `docker compose restart` o `docker compose down && up`

## Prossimi Step

**Fase 2 — Con OAuth/account** (quando Simone fornisce):
- Gmail/Google (OAuth) → 28 template
- GitHub (OAuth) → 3 template
- PostgreSQL (già in Docker) → 2 template

**Fase 3 — Con API keys/account esterni**:
- AI (OpenAI, Claude) → 8 template
- Messaging (Slack, Discord, Telegram) → 10 template
- CRM/Commerce → 8 template
- Resto → 14 template
