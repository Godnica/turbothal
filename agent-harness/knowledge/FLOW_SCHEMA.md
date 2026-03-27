# Activepieces Flow JSON Schema Reference

Documentazione completa dei campi JSON per creare flow via API.

## API Endpoint

```
POST http://localhost:8080/api/v1/flows/:flowId
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

Tutte le operazioni su un flow (trigger, azioni, stato) passano da questo endpoint
con un body `FlowOperationRequest` che ha un campo `type` discriminante.

---

## 1. Creare un Flow Vuoto

```
POST http://localhost:8080/api/v1/flows
```

```json
{
  "projectId": "<PROJECT_ID>",
  "displayName": "Nome del Flow"
}
```

**Risposta**: restituisce il flow con un trigger vuoto `"type": "EMPTY"`.

---

## 2. FlowOperationRequest — Tipi di Operazione

| type | Descrizione | Quando usarlo |
|------|-------------|---------------|
| `UPDATE_TRIGGER` | Imposta o modifica il trigger del flow | Per definire cosa avvia il flow |
| `ADD_ACTION` | Aggiunge uno step dopo un altro | Per aggiungere azioni alla catena |
| `UPDATE_ACTION` | Modifica uno step esistente | Per cambiare configurazione di uno step |
| `DELETE_ACTION` | Rimuove uno step | Per eliminare un'azione |
| `CHANGE_STATUS` | Abilita o disabilita il flow | Per attivare/disattivare |
| `LOCK_AND_PUBLISH` | Pubblica il flow (lo blocca in LOCKED) | Prima di abilitarlo |
| `IMPORT_FLOW` | Importa un flow da template JSON | Per ripristinare o copiare flow |
| `CHANGE_NAME` | Rinomina il flow | Per cambiare il displayName |
| `MOVE_ACTION` | Sposta uno step in un'altra posizione | Per riordinare la catena |
| `CHANGE_FOLDER` | Sposta il flow in un altro folder | Per organizzare |

---

## 3. UPDATE_TRIGGER

Imposta il trigger (l'evento che avvia il flow).

```json
{
  "type": "UPDATE_TRIGGER",
  "request": {
    "name": "trigger",
    "displayName": "<Nome visibile>",
    "valid": true,
    "type": "<TRIGGER_TYPE>",
    "settings": { ... }
  }
}
```

### Campi di request

| Campo | Tipo | Obbligatorio | Descrizione |
|-------|------|:---:|-------------|
| `name` | string | ✅ | Sempre `"trigger"` (identificatore interno) |
| `displayName` | string | ✅ | Nome visibile nell'UI |
| `valid` | boolean | ✅ | `true` se la configurazione è completa |
| `type` | string | ✅ | Tipo di trigger (vedi sotto) |
| `settings` | object | ✅ | Configurazione specifica per tipo |

### Tipi di trigger (`type`)

| Valore | Descrizione |
|--------|-------------|
| `EMPTY` | Nessun trigger selezionato (default alla creazione) |
| `PIECE_TRIGGER` | Trigger fornito da un piece (es. schedule, Gmail, webhook) |

### settings per PIECE_TRIGGER

| Campo | Tipo | Obbligatorio | Descrizione |
|-------|------|:---:|-------------|
| `pieceName` | string | ✅ | Nome npm del piece (es. `@activepieces/piece-schedule`) |
| `pieceVersion` | string | ✅ | Versione con tilde (es. `~0.1.17`) |
| `pieceType` | string | ✅ | `"OFFICIAL"` o `"CUSTOM"` |
| `packageType` | string | ✅ | `"REGISTRY"` (da npm) o `"ARCHIVE"` |
| `triggerName` | string | ✅ | Nome del trigger specifico nel piece |
| `propertySettings` | object | ✅ | Configurazione proprietà (può essere `{}`) |
| `input` | object | ✅ | Valori di input per le proprietà del trigger |
| `inputUiInfo` | object | ❌ | Metadati UI (può essere `{}`) |

> **⚠️ IMPORTANTE**: Se un trigger ha proprietà obbligatorie (required), devono essere incluse
> in `input` altrimenti il trigger sarà `valid: false` e il flow NON genererà run anche se abilitato.
> Esempio: `@activepieces/piece-webhook` richiede `"authType": "none"` (o `"basic"`, `"header"`).
> Per scoprire le proprietà richieste, controllare il sorgente del piece o il template in knowledge/templates/.

### Come trovare pieceName, triggerName e versione

```bash
# Cerca il piece
curl -s "http://localhost:8080/api/v1/pieces?searchQuery=schedule" \
  -H "Authorization: Bearer $TOKEN"

# Ottieni dettagli con trigger disponibili
curl -s "http://localhost:8080/api/v1/pieces/@activepieces/piece-schedule" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 4. ADD_ACTION

Aggiunge uno step alla catena del flow.

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "<nome_step_precedente>",
    "stepLocationRelativeToParent": "AFTER",
    "action": {
      "name": "<nome_univoco_step>",
      "displayName": "<Nome visibile>",
      "valid": true,
      "type": "<ACTION_TYPE>",
      "settings": { ... }
    }
  }
}
```

### Campi di request

| Campo | Tipo | Obbligatorio | Descrizione |
|-------|------|:---:|-------------|
| `parentStep` | string | ✅ | Nome dello step dopo cui inserire (es. `"trigger"`, `"step_1"`) |
| `stepLocationRelativeToParent` | string | ✅ | Posizione relativa (vedi sotto) |
| `branchIndex` | number | ❌ | Indice del branch (solo per ROUTER, default: 0) |
| `action` | object | ✅ | Definizione dell'azione |

### stepLocationRelativeToParent

| Valore | Descrizione |
|--------|-------------|
| `AFTER` | Subito dopo il parent step |
| `INSIDE_LOOP` | Prima azione dentro un loop |
| `INSIDE_BRANCH` | Prima azione dentro un branch del router |

### Tipi di azione (`action.type`)

| Valore | Descrizione | Quando usarlo |
|--------|-------------|---------------|
| `PIECE` | Azione fornita da un piece | Per usare integrazioni (Slack, Gmail, HTTP, ecc.) |
| `CODE` | Esegue codice JavaScript/TypeScript | Per logica custom |
| `LOOP_ON_ITEMS` | Itera su una lista | Per ripetere azioni su ogni elemento |
| `ROUTER` | Branching condizionale | Per if/else e switch |

---

## 5. Struttura Action per tipo

### 5a. PIECE Action

```json
{
  "name": "step_1",
  "displayName": "Send Slack Message",
  "valid": true,
  "type": "PIECE",
  "settings": {
    "pieceName": "@activepieces/piece-slack",
    "pieceVersion": "~0.7.0",
    "pieceType": "OFFICIAL",
    "packageType": "REGISTRY",
    "actionName": "send_channel_message",
    "propertySettings": {},
    "input": {
      "channel": "general",
      "text": "Hello from Activepieces!"
    },
    "errorHandlingOptions": {
      "continueOnFailure": { "value": false },
      "retryOnFailure": { "value": false }
    }
  }
}
```

| Campo settings | Tipo | Descrizione |
|-------|------|-------------|
| `pieceName` | string | Nome npm del piece |
| `pieceVersion` | string | Versione con tilde |
| `pieceType` | string | `"OFFICIAL"` o `"CUSTOM"` |
| `packageType` | string | `"REGISTRY"` |
| `actionName` | string | Nome dell'azione nel piece |
| `propertySettings` | object | Config proprietà (`{}` se non servono impostazioni speciali) |
| `input` | object | Valori di input per le proprietà dell'azione |
| `errorHandlingOptions` | object | Gestione errori |

### 5b. CODE Action

```json
{
  "name": "step_1",
  "displayName": "Custom Logic",
  "valid": true,
  "type": "CODE",
  "settings": {
    "sourceCode": {
      "code": "export const code = async (inputs) => {\n  return { result: 'hello' };\n};",
      "packageJson": "{}"
    },
    "input": {},
    "errorHandlingOptions": {
      "continueOnFailure": { "value": false },
      "retryOnFailure": { "value": false }
    }
  }
}
```

| Campo settings | Tipo | Descrizione |
|-------|------|-------------|
| `sourceCode.code` | string | Codice JS/TS. Deve esportare `code` come async function |
| `sourceCode.packageJson` | string | Dipendenze npm come stringa JSON |
| `input` | object | Variabili passate alla funzione `inputs` |

### 5c. LOOP_ON_ITEMS Action

```json
{
  "name": "step_1",
  "displayName": "Loop Over Items",
  "valid": true,
  "type": "LOOP_ON_ITEMS",
  "settings": {
    "items": "{{trigger.output.items}}"
  }
}
```

Le azioni dentro il loop si aggiungono con `stepLocationRelativeToParent: "INSIDE_LOOP"`.

### 5d. ROUTER Action (branching)

```json
{
  "name": "step_1",
  "displayName": "Check Condition",
  "valid": true,
  "type": "ROUTER",
  "settings": {
    "branches": [
      {
        "branchName": "If True",
        "branchType": "CONDITION",
        "conditions": [[{
          "firstValue": "{{trigger.output.status}}",
          "operator": "TEXT_EXACTLY_MATCHES",
          "secondValue": "active",
          "caseSensitive": false
        }]]
      },
      {
        "branchName": "Otherwise",
        "branchType": "FALLBACK"
      }
    ],
    "executionType": "EXECUTE_FIRST_MATCH"
  }
}
```

Le azioni dentro un branch si aggiungono con `stepLocationRelativeToParent: "INSIDE_BRANCH"` e `branchIndex: 0` (o 1, 2...).

---

## 6. Riferimenti tra Step (Interpolazione)

I valori degli step precedenti si referenziano con la sintassi `{{step_name.property}}`.

> **⚠️ CRITICO**: `.output` è IMPLICITO nella sintassi di interpolazione!
> - ✅ `{{step_1.result}}` → accede a `step_1.output.result`
> - ❌ `{{step_1.output.result}}` → NON funziona (risolve a stringa vuota)

### Regole di interpolazione

| Output dello step | Sintassi corretta | Risultato |
|-------------------|-------------------|-----------|
| Primitivo (es. math-helper → `68`) | `{{step_1}}` | `68` |
| Oggetto con `.result` (es. date-helper → `{result: "20/03/2026"}`) | `{{step_1.result}}` | `20/03/2026` |
| Oggetto (es. trigger webhook → `{method, headers, body}`) | `{{trigger.body.question}}` | valore del campo |
| Connessione salvata | `{{connections['my-connection']}}` | token/credenziali |

### Esempi testati e funzionanti

```
# Date helper (ritorna {result: "20/03/2026 14:21"})
{{step_1.result}}  →  "20/03/2026 14:21"

# Math helper (ritorna 68 come primitivo)
{{step_2}}  →  68

# Concatenazione in text-helper concat
texts: ["Digest del ", "{{step_1.result}}", " — Numero: ", "{{step_2}}"]
→ "Digest del 20/03/2026 14:21 — Numero: 68"
```

### Errori comuni

| Errore | Causa | Soluzione |
|--------|-------|-----------|
| `[object Object]` nel testo | Usato `{{step_X}}` su oggetto | Accedere alla proprietà: `{{step_X.result}}` |
| Stringa vuota | Usato `{{step_X.output.result}}` | Rimuovere `.output`: `{{step_X.result}}` |
| `undefined` in CODE input | Interpolazione di oggetti nested in input CODE | Rendere il codice autosufficiente, senza dipendere da interpolazione complessa |
| Stringa vuota per `{{trigger.id}}` con Gmail trigger | Il trigger Gmail NON ha `.id` al livello radice | Usare `{{trigger.message.messageId}}` (vedi §11) |

> **Nota**: L'interpolazione funziona meglio con valori primitivi (stringhe, numeri).
> Per passare oggetti complessi a un CODE step, è meglio rendere il codice autosufficiente
> anziché passare valori interpolati come input.

---

## 7. Operazioni di Stato

### Pubblicare (LOCK_AND_PUBLISH)

```json
{
  "type": "LOCK_AND_PUBLISH",
  "request": {}
}
```

### Abilitare/Disabilitare (CHANGE_STATUS)

```json
{
  "type": "CHANGE_STATUS",
  "request": {
    "status": "ENABLED"
  }
}
```

Valori: `"ENABLED"` o `"DISABLED"`.

### Flusso completo per attivare un flow

1. `POST /flows` — crea il flow
2. `UPDATE_TRIGGER` — imposta il trigger
3. `ADD_ACTION` — aggiungi azioni (ripeti per ogni step)
4. `LOCK_AND_PUBLISH` — pubblica
5. `CHANGE_STATUS: ENABLED` — attiva

---

## 8. Naming Convention degli Step

| Step | Nome |
|------|------|
| Trigger | `trigger` (sempre) |
| Prima azione | `step_1` |
| Seconda azione | `step_2` |
| N-esima azione | `step_N` |

I nomi devono essere univoci nel flow.

---

## 9. propertySettings

Configura come ogni proprietà di un piece viene gestita:

```json
{
  "propertySettings": {
    "nome_proprietà": {
      "type": "MANUAL"
    }
  }
}
```

| type | Significato |
|------|-------------|
| `MANUAL` | Valore inserito manualmente |
| `DYNAMIC` | Valore risolto dinamicamente |

Per la maggior parte dei casi, `{}` vuoto funziona.

---

## 10. errorHandlingOptions

```json
{
  "errorHandlingOptions": {
    "continueOnFailure": { "value": false },
    "retryOnFailure": { "value": false }
  }
}
```

| Campo | Descrizione |
|-------|-------------|
| `continueOnFailure` | Se `true`, il flow continua anche se lo step fallisce |
| `retryOnFailure` | Se `true`, lo step viene ritentato automaticamente |

---

## 11. Output del Trigger Gmail (`gmail_new_email_received`)

> **⚠️ CRITICO**: L'output del trigger Gmail è annidato sotto `trigger.message.*`, NON al livello radice.

Il trigger usa `mailparser` internamente e restituisce:

```json
{
  "message": {
    "subject": "Come stai oggi?",
    "text": "Ciao, sto bene grazie!",
    "html": "<p>Ciao, sto bene grazie!</p>",
    "messageId": "<abc123@mail.gmail.com>",
    "from": {
      "text": "Silvio Revelli <silviorevelli@gmail.com>",
      "value": [{ "address": "silviorevelli@gmail.com", "name": "Silvio Revelli" }]
    },
    "to": { ... },
    "date": "2026-03-27T10:00:00.000Z",
    "attachments": []
  },
  "thread": { ... }
}
```

### Campi di interpolazione testati

| Campo | Sintassi corretta | Note |
|-------|-------------------|------|
| Corpo testo | `{{trigger.message.text}}` | Testo plain dell'email |
| Oggetto | `{{trigger.message.subject}}` | Oggetto dell'email |
| Message-ID RFC 2822 | `{{trigger.message.messageId}}` | Per `in_reply_to` in send_email |
| Mittente (full) | `{{trigger.message.from.text}}` | Es. "Nome <email@gmail.com>" |
| Indirizzo mittente | `{{trigger.message.from.value.0.address}}` | Solo l'indirizzo email |

> **Nota mittente in send_email**: il campo `from` va lasciato `""`. Gmail usa automaticamente l'email dell'account Google autenticato via OAuth (`{{connections['CONNECTION_EXTERNAL_ID']}}`). Non hardcodare mai un indirizzo email nel campo `from`.

### Come fare reply a un'email Gmail

**NON usare `reply_to_email`** se il trigger è `gmail_new_email_received` — richiede il Gmail API message ID (esadecimale) che non è accessibile direttamente dall'output del trigger.

**✅ Usare `send_email` con `in_reply_to`:**

```json
{
  "actionName": "send_email",
  "input": {
    "receiver": ["mittente@gmail.com"],
    "subject": "Re: {{trigger.message.subject}}",
    "body_type": "plain_text",
    "body": "La mia risposta",
    "in_reply_to": "{{trigger.message.messageId}}"
  }
}
```

Il campo `in_reply_to` imposta gli header `In-Reply-To` e `References` e recupera il thread ID corretto via `Rfc822msgid:` search.

---

## 12. Pattern Auth per API calls (test_helper.sh)

Il JWT salvato in `~/.config/activepieces/config.toml` **non funziona con curl diretto** (401 Unauthorized). Usare sempre `get_token()` da `test_helper.sh` che esegue un fresh sign-in:

```bash
source agent-harness/knowledge/test_helper.sh
TOKEN=$(get_token)
curl -s "$API/flows" -H "Authorization: Bearer $TOKEN"
```

Le credenziali si trovano in `~/.config/activepieces/config.toml` o in `test_helper.sh`.
Project ID: `ctxq6E1nbcME4wTgkD5Qe`

---

## 13. Versioni piece verificate (2026-03-27)

| Piece | Versione installata | pieceVersion da usare |
|-------|--------------------|-----------------------|
| `@activepieces/piece-webhook` | 0.1.32 | `~0.1.31` |
| `@activepieces/piece-gmail` | 0.11.6 | `~0.11.6` |
| `@activepieces/piece-schedule` | 0.1.17 | `~0.1.17` |

Per scoprire la versione installata:
```bash
curl -s "$API/pieces?searchQuery=<nome>" -H "Authorization: Bearer $TOKEN"
```
