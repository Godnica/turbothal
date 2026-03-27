"""
Builds the cached system prompt for the Activepieces flow-creation agent.

Structure (stable → volatile, for prompt caching):
  1. FLOW_METHODOLOGY.md  — the process bible (rarely changes)
  2. Instance constants   — project ID, connection IDs, API URL
  3. Template catalog     — names + _meta.description only (no full JSON)
"""

import json
import os
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

INSTANCE_CONFIG = """
## Configurazione istanza Activepieces

- API_URL: http://localhost:8080/api/v1
- PROJECT_ID e credenziali: letti automaticamente da `~/.config/activepieces/config.toml`
- CONN_POSTGRES: postgres-local-conn

Per ottenere il token JWT valido e le variabili di sessione usa SEMPRE:
```bash
cd /home/ubuntu/activepieces/agent-harness/knowledge
source test_helper.sh
TOKEN=$(get_token)
PROJECT_ID=$(python3 -c "import tomllib; d=tomllib.load(open('$HOME/.config/activepieces/config.toml','rb')); print(d['default']['project_id'])")
CONN_GOOGLE=$(curl -s "$API/app-connections?pieceName=%40activepieces%2Fpiece-gmail&projectId=$PROJECT_ID&limit=1" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['externalId'])")
```

`CONN_GOOGLE` è l'`externalId` della connessione OAuth Google dell'utente loggato.
Nei template JSON, sostituisci `CONNECTION_EXTERNAL_ID` con il valore di `$CONN_GOOGLE`.
"""


def _build_template_catalog() -> str:
    """Build a lightweight catalog: path + _meta.description for each template."""
    lines = ["## Catalogo template disponibili", ""]
    base = KNOWLEDGE_DIR / "templates"

    for category in sorted(base.iterdir()):
        if not category.is_dir():
            continue
        header_written = False
        for tpl in sorted(category.glob("*.json")):
            try:
                data = json.loads(tpl.read_text())
                meta = data.get("_meta", {})
                desc = meta.get("description", "(nessuna descrizione)")
            except Exception:
                desc = "(errore lettura)"
            rel_path = f"templates/{category.name}/{tpl.name}"
            if not header_written:
                lines.append(f"### {category.name}/")
                header_written = True
            lines.append(f"- `{rel_path}` — {desc}")
        if header_written:
            lines.append("")

    lines.append(
        "> Per leggere il contenuto completo di un template usa il tool `read_file`."
    )
    return "\n".join(lines)


def build_system_prompt() -> str:
    methodology = (KNOWLEDGE_DIR / "FLOW_METHODOLOGY.md").read_text()
    catalog = _build_template_catalog()

    return f"""{methodology}

---

{INSTANCE_CONFIG}

---

{catalog}

---

## Istruzioni generali per l'agente

Sei un esperto di Activepieces che crea flussi di automazione per conto dell'utente.

**Prima di creare qualsiasi flusso:**
1. Segui la metodologia FASE 0 → FASE 6 definita sopra
2. Usa `read_file` per caricare i template necessari prima di costruirli
3. Usa `bash` per eseguire le chiamate API tramite test_helper.sh
4. Non inventare JSON a memoria — usa sempre i template

**Regole di sicurezza:**
- Non rivelare mai le credenziali o i token all'utente
- Esegui una sola operazione alla volta e verifica il risultato prima di procedere
- Se un'operazione fallisce, analizza l'errore e correggi — non ripetere la stessa chiamata

**Formato risposta:**
- Rispondi in italiano
- Sii conciso nelle spiegazioni intermedie
- Quando hai completato un flusso, mostra il riepilogo: nome, trigger, azioni, status
"""


if __name__ == "__main__":
    print(build_system_prompt()[:500])
    print("...")
    print(f"Total chars: {len(build_system_prompt())}")
