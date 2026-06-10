# Git MCP Server for AI Agents

A Model Context Protocol (MCP) server that provides Git operations for AI agents.

## Descrizione

Questo progetto implementa un server MCP che espone operazioni Git tramite un'API JSON strutturata, progettato per essere utilizzato da agenti AI che necessitano di interagire con repository Git in modo programmato e sicuro.

## Architettura

- **FastAPI**: framework web per l'esposizione delle API
- **GitPython**: wrapper per le operazioni Git
- **Struttura modulare**: separazione tra server, wrapper Git e modelli di risposta
- **Configurazione tramite variabili d'ambiente**: percorso del repository, host e porta

## Installazione

### Da PyPI (quando pubblicato)
```bash
pip install git-mcp-server
```

### Installazione per sviluppo
```bash
# Clona il repository
git clone <repository-url>
cd git-mcp-server-per-agenti-ai

# Installa in modalità sviluppo
pip install -e .
```

## Uso

### Avvio del server
Il server può essere avviato in due modi:

1. Utilizzando il comando installato:
```bash
git-mcp-server
```

2. Utilizzando uvicorn direttamente (per sviluppo):
```bash
uvicorn git_mcp_server.main:app --host localhost --port 8080
```

### Configurazione
Imposta le variabili d'ambiente per la configurazione:
- `GIT_MCP_SERVER_REPO_PATH`: Percorso del repository Git da gestire (default: directory corrente)
- `GIT_MCP_SERVER_HOST`: Host su cui bindare il server (default: localhost)
- `GIT_MCP_SERVER_PORT`: Porta su cui bindare il server (default: 8080)

Esempio:
```bash
export GIT_MCP_SERVER_REPO_PATH=/path/to/your/repo
export GIT_MCP_SERVER_HOST=0.0.0.0
export GIT_MCP_SERVER_PORT=8080
git-mcp-server
```

## API Endpoints

### POST `/git/command`

Esegue un comando Git e restituisce dati strutturati in JSON.

#### Corpo della richiesta
```json
{
  "command": "status|diff|log",
  "args": {
    // Argomenti opzionali specifici al comando
    // Per diff: {"staged": true, "file": "path/to/file"}
    // Per log: {"n": 10, "since": "2026-01-01", "author": "Name <email>", "file": "path/to/file"}
  }
}
```

#### Corpo della risposta
```json
{
  "success": true,
  "output": { ... }, // Dati strutturati a seconda del comando
  "error": null
}
```

Se `success` è false, `output` sarà null e `error` conterrà un messaggio di errore.

#### Dettagli dei comandi

- **status**: Restituisce informazioni sullo stato del repository
  - Chiavi di output: `branch`, `staged` (lista), `unstaged` (lista), `untracked` (lista)
  
- **diff**: Restituisce informazioni sulle differenze
  - Argomenti: `staged` (booleano), `file` (stringa percorso)
  - Chiave di output: `diff` (stringa)

- **log**: Restituisce la cronologia dei commit
  - Argomenti: `n` (int, default 10), `since` (stringa data), `author` (stringa), `file` (stringa percorso)
  - Chiave di output: `commits` (lista di oggetti commit)

### Esempio di utilizzo con curl

```bash
# Ottieni lo status
curl -X POST http://localhost:8080/git/command \
  -H "Content-Type: application/json" \
  -d '{"command": "status"}'

# Ottieni il diff staged
curl -X POST http://localhost:8080/git/command \
  -H "Content-Type: application/json" \
  -d '{"command": "diff", "args": {"staged": true}}'

# Ottieni gli ultimi 5 commit
curl -X POST http://localhost:8080/git/command \
  -H "Content-Type: application/json" \
  -d '{"command": "log", "args": {"n": 5}}'
```

## Test

È incluso uno script di test per validare gli endpoint API:
```bash
python test_api.py
```
Assicurati che il server sia in esecuzione prima di eseguire i test.

## Stato

✅ COMPLETATO — 2026-06-10
- Struttura progetto creata
- Setup FastAPI e schema JSON completato
- Wrapper GitPython per operazioni implementato
- Script di test e README dettagliato scritto
- Tutte le funzionalità previste operative

## Note importanti

### Benchmark GPU
Se questo server viene utilizzato insieme a workflow AI dipendenti dalla GPU (come l'inferenza LLM), si noti che:
- I test di benchmark della GPU richiedono accesso esclusivo alla GPU
- Tali benchmark dovrebbero essere eseguiti manualmente quando la GPU non è utilizzata da altri processi
- Il server MCP stesso non esegue operazioni GPU; fornisce solo funzionalità Git

### Privacy e distribuzione pubblica
Quando si pubblica questo codice pubblicamente:
- Non includere percorsi assoluti locali nel codice o nella documentazione
- Utilizzare variabili d'ambiente per configurazioni sensibili
- Fornire un file `.env.example` con valori placeholder generici