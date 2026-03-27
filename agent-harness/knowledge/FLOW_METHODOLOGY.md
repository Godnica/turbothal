# FLOW_METHODOLOGY.md — Come creare un flusso su Activepieces

> **Questo è il documento di partenza ogni volta che devo creare un flusso.**
> Segui i passaggi in ordine. Consulta gli altri file solo quando serve il dettaglio.
> - Schema API e regole interpolazione → `FLOW_SCHEMA.md`
> - JSON pronti dei singoli step → `templates/`
> - Script per chiamate API → `test_helper.sh`

---

## FASE 0 — Setup (sempre, prima di tutto)

```bash
cd /home/ubuntu/activepieces/agent-harness/knowledge
source test_helper.sh
TOKEN=$(get_token)
```

> ⚠️ **ERRORE FREQUENTE #1**: Usare il JWT da `~/.config/activepieces/config.toml` con curl → dà 401.
> Il token salvato scade e non funziona direttamente con curl. Usare SEMPRE `get_token()`.

Variabili da avere sempre pronte:
```bash
API="http://localhost:8080/api/v1"
PROJECT_ID="ctxq6E1nbcME4wTgkD5Qe"
CONN_GOOGLE="IHIrEa1Ae8cwPTxl8HT5V"   # OAuth Google (Gmail, Sheets, Drive, Calendar, Contacts)
CONN_POSTGRES="postgres-local-conn"    # PostgreSQL locale
```

---

## FASE 1 — Analizza la richiesta prima di scrivere codice

Prima di fare qualsiasi chiamata API, rispondi a queste domande:

1. **Qual è il trigger?** (cosa avvia il flusso?)
   - Evento esterno (email, nuovo record DB) → PIECE_TRIGGER
   - Orario fisso → schedule
   - Chiamata manuale/HTTP → webhook

2. **Quali azioni servono in sequenza?**
   - Elenca ogni step in ordine logico
   - Identifica se ci sono branch (if/else) o loop

3. **Quali pezzi sono necessari?**
   - Controlla se esiste già un template in `templates/`
   - Se non esiste, cerca la versione del piece: `curl -s "$API/pieces?searchQuery=NOME" -H "Authorization: Bearer $TOKEN"`

4. **Ci sono dati da passare tra step?**
   - Identifica già ora i campi di interpolazione che userai
   - Controlla la struttura di output del trigger (vedi §11 di `FLOW_SCHEMA.md` per Gmail)

> ⚠️ **ERRORE FREQUENTE #2**: Iniziare a costruire il flusso senza conoscere la struttura dell'output del trigger.
> Risultato: campi di interpolazione sbagliati scoperti solo a runtime.
> **Fix**: prima di costruire, leggi il `_meta.notes` del template trigger corrispondente.

---

## FASE 2 — Crea il flow vuoto

```bash
FLOW_ID=$(create_flow "Nome del Flow")
echo "Flow ID: $FLOW_ID"
```

Verifica che l'ID sia valido (non vuoto, non un messaggio di errore).

---

## FASE 3 — Imposta il trigger

Usa il template da `templates/triggers/`. **Non inventare il JSON a memoria.**

```bash
# Leggi il template
cat templates/triggers/NOME_TRIGGER.json

# Sostituisci i placeholder e invia
flow_op "$FLOW_ID" '{ ... JSON del template con valori reali ... }'
```

Verifica il risultato:
```bash
# Controlla che il trigger sia stato impostato correttamente
curl -s "$API/flows/$FLOW_ID" -H "Authorization: Bearer $(get_token)" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); t=d['version']['trigger']; print('type:', t['type'], '| valid:', t.get('valid'))"
```

> ⚠️ **ERRORE FREQUENTE #3**: Usare una `pieceVersion` sbagliata (es. `~0.5.0` per webhook invece di `~0.1.31`).
> Il trigger risulta `type: EMPTY, valid: false` e il flow non gira mai.
> **Fix**: usa SEMPRE le versioni da `FLOW_SCHEMA.md §13` o cerca con l'API pieces.

> ⚠️ **ERRORE FREQUENTE #4**: Dimenticare `"authType": "none"` nel trigger webhook.
> Il trigger risulta `valid: false`.
> **Fix**: il template `webhook_catch.json` lo include già, usarlo sempre.

---

## FASE 4 — Aggiungi le azioni in sequenza

Per ogni step, in ordine:

1. Prendi il JSON da `templates/actions/NOME_AZIONE.json`
2. Sostituisci: `step_N` con il nome corretto, `CONNECTION_EXTERNAL_ID` con l'ID connessione, valori di input
3. Imposta `parentStep` correttamente (lo step precedente)
4. Invia con `flow_op`

```bash
flow_op "$FLOW_ID" '{ "type": "ADD_ACTION", "request": { ... } }'
```

**Per step dentro un ROUTER:**
```bash
# Branch 0 (primo branch / condizione)
flow_op "$FLOW_ID" '{ "type": "ADD_ACTION", "request": { "parentStep": "step_ROUTER", "stepLocationRelativeToParent": "INSIDE_BRANCH", "branchIndex": 0, "action": { ... } } }'

# Branch 1 (fallback / otherwise)
flow_op "$FLOW_ID" '{ "type": "ADD_ACTION", "request": { "parentStep": "step_ROUTER", "stepLocationRelativeToParent": "INSIDE_BRANCH", "branchIndex": 1, "action": { ... } } }'
```

**Per step dentro un LOOP:**
```bash
flow_op "$FLOW_ID" '{ "type": "ADD_ACTION", "request": { "parentStep": "step_LOOP", "stepLocationRelativeToParent": "INSIDE_LOOP", "action": { ... } } }'
```

> ⚠️ **ERRORE FREQUENTE #5**: Usare `reply_to_email` di Gmail quando il trigger è `gmail_new_email_received`.
> Fallisce perché `reply_to_email` richiede il Gmail API message ID (esadecimale) non disponibile nell'output del trigger.
> **Fix**: usare `send_email` con `in_reply_to: "{{trigger.message.messageId}}"`.
> Template pronto: `actions/gmail_send_email_as_reply.json`

> ⚠️ **ERRORE FREQUENTE #6**: Usare `{{trigger.body_plain}}` o `{{trigger.id}}` con il trigger Gmail.
> L'output del trigger Gmail è annidato sotto `trigger.message.*`.
> **Fix**: `{{trigger.message.text}}` per il corpo, `{{trigger.message.messageId}}` per l'ID.

---

## FASE 5 — Pubblica e abilita

```bash
STATUS=$(publish_and_enable "$FLOW_ID")
echo "Status: $STATUS"
```

Il risultato atteso è `ENABLED NONE`. Se è `DISABLED ENABLING` aspetta qualche secondo e ricontrolla:

```bash
sleep 5
curl -s "$API/flows/$FLOW_ID" -H "Authorization: Bearer $(get_token)" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'])"
```

> ⚠️ **ERRORE FREQUENTE #7**: Il flow rimane bloccato in `ENABLING`.
> Causa: worker con socket timeout disconnesso dall'app.
> **Fix**: `docker compose restart` nella cartella di Activepieces.

---

## FASE 6 — Verifica e test

### Test trigger manuale (per trigger PIECE_TRIGGER):
```bash
VERSION_ID=$(curl -s "$API/flows/$FLOW_ID" -H "Authorization: Bearer $(get_token)" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['version']['id'])")

curl -s -X POST "$API/test-trigger" \
  -H "Authorization: Bearer $(get_token)" \
  -H "Content-Type: application/json" \
  -d "{\"flowId\":\"$FLOW_ID\",\"flowVersionId\":\"$VERSION_ID\",\"projectId\":\"$PROJECT_ID\",\"testStrategy\":\"TEST_FUNCTION\"}"
```

### Test trigger webhook (per flow con webhook trigger):
```bash
curl -s -X POST "$API/webhooks/$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{"chiave": "valore"}'
```

### Controlla i run:
```bash
sleep 5
curl -s "$API/flow-runs?projectId=$PROJECT_ID&flowId=$FLOW_ID&limit=3" \
  -H "Authorization: Bearer $(get_token)" | \
  python3 -c "
import sys,json
runs=json.load(sys.stdin).get('data',[])
for r in runs:
    print(r['status'], r['startTime'][:19])
    for name,s in r.get('steps',{}).items():
        status = s.get('status','?')
        err = s.get('errorMessage','')[:80] if status=='FAILED' else ''
        print(f'  {name}: {status}', err)
"
```

> ⚠️ **ERRORE FREQUENTE #9**: Usare `"label": "INBOX"` come stringa nel trigger Gmail.
> La prop `label` si aspetta un oggetto `{id, name}` (da dropdown API). Passando una stringa, la query Gmail diventa `label:undefined` → nessun risultato, trigger mai attivo.
> **Fix**: lasciare `"label": ""` (stringa vuota) per non filtrare per label, oppure omettere il campo.

> ⚠️ **ERRORE FREQUENTE #8**: Il run mostra `environment: TESTING` — è un run manuale di test, non da trigger reale.
> I run di test hanno `trigger.output = {}` quindi i campi interpolati saranno vuoti.
> **Fix**: per testare il flusso reale aspettare un trigger vero, oppure usare il webhook test per flow con webhook trigger.

---

## Checklist rapida

```
[ ] get_token() fatto
[ ] Trigger: template corretto + versione piece verificata
[ ] Ogni action: template da templates/ + placeholder sostituiti
[ ] Interpolazioni: campi esistenti nell'output del trigger/step precedente
[ ] INSIDE_BRANCH con branchIndex corretto per ROUTER
[ ] publish_and_enable → status ENABLED
[ ] Almeno un run SUCCEEDED verificato
```

---

## Mappa dei template disponibili per categoria

| Cosa vuoi fare | Template da usare |
|----------------|-------------------|
| Avvia su orario | `triggers/schedule_*.json` |
| Avvia su webhook HTTP | `triggers/webhook_catch.json` |
| Avvia su nuova email Gmail | `triggers/gmail_new_email_from_sender.json` |
| Avvia su nuovo record Postgres | `triggers/postgres_new_row.json` |
| Invia email Gmail | `actions/gmail_send_email.json` |
| Rispondi a email ricevuta | `actions/gmail_send_email_as_reply.json` ← NON gmail_reply_to_email |
| If/else | `actions/router_if_else.json` |
| Switch (3+ branch) | `actions/router_switch.json` |
| Loop su lista | `actions/loop_basic.json` |
| Codice JS custom | `actions/code_basic.json` |
| Chiamata HTTP | `actions/http_get.json` / `actions/http_post.json` |
| Google Sheets | `actions/gsheets_*.json` |
| Google Drive | `actions/gdrive_*.json` |
| Google Calendar | `actions/gcal_*.json` |
| Store (chiave-valore) | `actions/store_*.json` |
