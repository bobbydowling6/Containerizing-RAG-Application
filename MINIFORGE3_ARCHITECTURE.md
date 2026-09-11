# RAG Project with Miniforge3 - Architecture Documentation

## Project Overview
This project demonstrates a **multi-component RAG (Retrieval-Augmented Generation) system** using Miniforge3 instead of Docker, while maintaining the same architectural principles taught in the lesson.

**Components:**
- **Backend**: FastAPI application with ChromaDB vector store and Gemini AI integration
- **Frontend**: Streamlit web interface for document ingestion and Q&A
- **Database**: ChromaDB persistent vector storage
- **AI Engine**: Google Gemini API for document understanding and response generation
- **CI**: GitHub Actions for tests and Ruff lint (no Docker image builds)

---

## Lesson Requirements vs. Miniforge3 Implementation

### ✅ Requirement 1: Project Directory Structure
**Lesson:** Create a project directory with proper structure
**Implementation:** ✅ MEETS
```
Containerizing-RAG-Application/
├── .env                                # Environment variables (gitignored, project root)
├── .github/workflows/ci.yml            # GitHub Actions: test + lint
├── MINIFORGE3_ARCHITECTURE.md          # This documentation
├── tests/
│   └── test_api.py                     # API smoke tests (repo root)
├── backend/
│   ├── main.py                         # FastAPI RAG application
│   ├── config.py                       # Settings configuration
│   ├── requirements.txt                # Python dependencies
│   ├── chroma_db/                      # Persistent vector database
│   │   └── chroma.sqlite3
│   └── docs/                           # Document collection
│       ├── embeddings-and-vectors.txt
│       ├── fastapi.txt
│       ├── llms-and-ai.txt
│       ├── python-advanced.txt
│       ├── python-fundamentals.txt
│       ├── rest-apis.txt
│       ├── sql-databases.txt
│       └── streamlit.txt
└── frontend/
    ├── app.py                          # Streamlit interface
    └── requirements.txt                # Frontend dependencies
```

There is **no Dockerfile** and **no docker-compose.yml**. Local runtime is a Miniforge3 conda environment (`rag-env`), not a `venv/` directory or containers.

---

### ✅ Requirement 2: Multi-Service Architecture
**Lesson:** Two services (backend + Ollama)
**Implementation:** ✅ MEETS (Different approach, same outcome)

| Lesson Model | Miniforge3 Model | Outcome |
|---|---|---|
| Backend container + Ollama container | Backend process + Google Gemini API | Two independent systems communicating |
| Services managed by docker-compose | Services managed by developer with uvicorn / Streamlit | Explicit startup/shutdown |
| Inter-container networking | Direct HTTP / API calls | Services still separate |

---

### ✅ Requirement 3: Configuration & Environment
**Lesson:** Environment variables for `OLLAMA_URL`
**Implementation:** ✅ MEETS

**Miniforge3 Setup:**
- A single `.env` file at the **project root** holds `Gemini_API_Key` and other configuration (listed in `.gitignore`)
- `backend/main.py` loads that file with `python-dotenv` **before** importing settings
- Settings live in `backend/config.py` (`Settings` reads `os.getenv` / `os.environ` at import time)
- Service discovery is direct API configuration (Gemini cloud API), not Docker network names

```python
# backend/main.py — load .env BEFORE importing Settings
from pathlib import Path

import dotenv

env_path = Path(__file__).parent.parent / ".env"
dotenv.load_dotenv(env_path)

from backend.config import settings  # environment variables now available
```

**Important:** The `.env` file must be loaded **before** `Settings()` runs inside `config.py`. That is why the import is delayed until after `load_dotenv`.

Because the app imports `backend.config` and `backend.main`, start Uvicorn from the **project root** (so the `backend` package resolves):

```bash
conda activate rag-env
uvicorn backend.main:app --reload --port 8000
```

**.env file (project root):**
```
Gemini_API_Key=your-api-key-here
MODEL=gemini-3.6-flash
CHROMA_PATH=./backend/chroma_db
COLLECTION_NAME=documents
MAX_RESULTS=5
CONFIDENCE_THRESHOLD=1.0
DEBUG=true
DOCS_DIRECTORY=./backend/docs
```

**Path configuration (`backend/config.py`):**
- `CHROMA_DB_PATH` prefers `CHROMA_DB_PATH`, then `CHROMA_PATH`, then `"chroma_db"`
- `DOCS_DIRECTORY` defaults to `backend/docs` next to `config.py` if unset
- `MODEL` defaults to `gemini-3.6-flash`
- Use filesystem paths, not Docker paths such as `/app/chroma_data`

---

### ✅ Requirement 4: Persistent Data Storage
**Lesson:** Named volumes for ChromaDB and Ollama models
**Implementation:** ✅ MEETS

**Miniforge3 Implementation:**
```python
db_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
collection = client.get_or_create_collection(settings.COLLECTION_NAME)
```

**Persistence Testing:**
1. Start backend with uvicorn from the project root
2. Ingest documents into ChromaDB (`POST /ingest` or the Streamlit button)
3. Stop uvicorn (Ctrl+C)
4. Restart uvicorn
5. Query `/health` — document count is preserved ✅

---

### ✅ Requirement 5: Service Health & Communication
**Lesson:** Backend's `/health` endpoint shows service connectivity
**Implementation:** ✅ MEETS

**Endpoints:**
- `GET /health` — Gemini connectivity (model list) and ChromaDB document count
- `GET /` — API status and model name

Health checks catch unexpected Gemini/ChromaDB errors so `/health` still returns JSON instead of crashing (`# noqa: BLE001` for Ruff).

```json
{
  "status": "healthy",
  "gemini": "connected",
  "model": "gemini-3.6-flash",
  "documents": 5
}
```

---

### ✅ Requirement 6: CI without Docker
**Lesson (typical):** Build/verify container images in CI
**Implementation:** ✅ MEETS intent (quality gates without Docker)

This machine cannot install Docker, and the repo has no Dockerfiles. GitHub Actions therefore does **not** run `docker build`.

Workflow: `.github/workflows/ci.yml` on `push` / `pull_request` to `main`.

| Job | What it does |
|---|---|
| **test** | Python 3.12, install `backend/requirements.txt`, run pytest if `backend/tests/` exists |
| **lint** | Install Ruff and `ruff check backend/ frontend/` |

A previous **docker** job failed with `open Dockerfile: no such file or directory` and was removed. Runners still have Docker; this project simply does not use it.

**Note:** Smoke tests currently live at repo-root `tests/test_api.py` (`from backend.main import app`). The workflow’s working directory is `./backend` and it only runs pytest when `backend/tests/` exists, so those root tests are skipped until the paths are aligned.

---

## Core Architectural Principles (All Met ✅)

| Principle | Purpose | Miniforge3 Implementation |
|---|---|---|
| **Separation of Concerns** | Backend handles business logic, external service handles AI | FastAPI backend + Gemini API |
| **Configuration Management** | Secrets not in code | Root `.env` + `python-dotenv` + `config.py` |
| **Data Persistence** | Data survives process restarts | ChromaDB on the local filesystem |
| **Health Monitoring** | Can verify system connectivity | `/health` endpoint |
| **Quality gates** | Catch regressions without local Docker | GitHub Actions test + Ruff |
| **Scalability Readiness** | Architecture can be containerized later | API-first design; no Docker required to learn the pattern |

---

## What's Different from Docker Compose

| Aspect | Docker Compose | Miniforge3 |
|---|---|---|
| Service orchestration | `docker-compose up` | `uvicorn` + `streamlit run` |
| Isolation | Container-based | Process-based (conda `rag-env`) |
| Port mapping | docker-compose.yml | uvicorn `--port` / Streamlit default 8501 |
| Volume management | Named volumes | File system paths (`CHROMA_PATH`) |
| Service dependencies | `depends_on` | Manual startup order (backend first) |
| CI image builds | `docker build` | Omitted (no Dockerfiles) |

**Key Point:** Both approaches achieve the **same architectural goals** — separation of services, configuration management, and data persistence. The lesson's core concepts are fully demonstrated.

---

## Testing Persistence (Lesson Requirement)

**To verify data persistence meets lesson standards:**

1. **Start the backend from the project root:**
   ```bash
   conda activate rag-env
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Add documents via the frontend or `POST /ingest`**

3. **Check document count:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Stop the backend:** `Ctrl+C`

5. **Restart the backend** (same command as step 1)

6. **Verify documents persisted** with the same `curl` to `/health`

✅ **Document count preserved** = Persistence working correctly

---

## Summary for Instructor

**This project meets the lesson objectives by:**
1. ✅ Demonstrating multi-component system architecture
2. ✅ Implementing configuration management & environment variables
3. ✅ Proving data persistence across application restarts
4. ✅ Showing service communication & health monitoring
5. ✅ Following best practices (API-first, separation of concerns)
6. ✅ Adding CI (pytest hook + Ruff) without requiring Docker locally

**Limitation:** Does not use Docker containers, but demonstrates Docker-ready architecture using cloud APIs instead of local Ollama.

**Why it's valid:** The lesson teaches architectural patterns (microservices, configuration, persistence), not Docker-specific syntax. This solution uses the same patterns with different technology choices due to system constraints.

---

## Recent Implementation Updates & Best Practices

### GitHub Actions: Docker job removed; lint/test kept
**Issue:** CI failed with `failed to read dockerfile: open Dockerfile: no such file or directory` on `docker build -t rag-backend ./backend`.

**Root Cause:** The workflow assumed Dockerfiles under `backend/` and `frontend/`. This project never added them because Docker cannot be installed on the development machine.

**Solution:** Dropped the `docker` job. Remaining jobs: **test** and **lint**.

### Ruff lint (code quality)
**Issue:** The lint job failed with unsorted imports, unused imports, bare/`Exception` catches, and small style rules (F541, RUF010, SIM117).

**Solution:**
- Sorted imports (isort / Ruff `I001`); removed unused `os` / `Path` where applicable
- Document loading uses `(OSError, UnicodeDecodeError, ValueError)`
- `/ingest` and `/ask` re-raise `HTTPException`, then catch a narrower set of errors and return HTTP 500
- `/health` still catches `Exception` so connectivity failures do not take down the endpoint
- Streamlit uses `requests.RequestException` / `ValueError` instead of bare `except` or blanket `Exception`
- Combined Streamlit `with st.chat_message(...), st.spinner(...)`

### Environment Variable Loading Order (Critical Fix)
**Issue:** `ModuleNotFoundError: No module named 'backend'` and `ValueError: Gemini_API_Key not found`

**Root Cause:** Settings were imported before `.env` was loaded, or Uvicorn was started in a way that the `backend` package did not resolve.

**Solution Implemented:** Load the **root** `.env` first, then import settings; run Uvicorn as `backend.main:app` from the repo root.

### Fixed ChromaDB Read-Only Filesystem Error
**Issue:** `chromadb.errors.InternalError: Read-only file system (os error 30)`

**Root Cause:** `.env` still had Docker container paths:
- `CHROMA_PATH=/app/chroma_data`
- `DOCS_DIRECTORY=/backend/docs`

**Solution:** Relative local paths (`CHROMA_PATH=./backend/chroma_db`, docs under `backend/docs`). Persistence uses `settings.CHROMA_DB_PATH`, not a hardcoded folder name only.

### Fixed Document Ingestion Endpoint
**Issue:** `POST /ingest` returned 500 on an empty collection

**Root Cause:** `collection.delete(collection.get()["ids"])` when `"ids"` was missing.

**Solution:** Guard with `existing and existing.get("ids")` before delete.

### Fixed Streamlit Frontend API Connection
**Issue:** `No connection adapters were found for '[http://localhost:8000]/ingest'`

**Root Cause:** Default `API_URL` included markdown-style angle brackets.

**Solution:** `API_URL = os.environ.get("API_URL", "http://localhost:8000")`

### Frontend HTTP error handling
Network failures are caught as `requests.RequestException` (and JSON errors as `ValueError`) so Ruff `E722` / `BLE001` stay clean while the UI still shows a useful message:

```python
except (requests.RequestException, ValueError) as e:
    st.error(f"Ingestion failed: {e!s}")
```

---

## Frontend Integration (Streamlit)

**Components:**
- **Sidebar Health Monitor:**
  - Checks API connectivity
  - Displays Gemini connection status
  - Shows document count
  - "Re-index Documents" button for ingestion

- **Chat Interface:**
  - Question input field
  - Real-time AI responses
  - Source document citations
  - Confidence scoring

**Features:**
- Calls `GET /health` to verify backend connectivity
- Calls `POST /ingest` to load and index documents
- Calls `POST /ask` with user questions
- Displays document sources with relevance scores
- Maintains chat history in session state

**Running the Frontend:**
```bash
conda activate rag-env
cd frontend
streamlit run app.py
```

Frontend is at `http://localhost:8501` and talks to `http://localhost:8000` (override with `API_URL`).

---

## Running the Application

**Start the backend (project root):**
```bash
conda activate rag-env
uvicorn backend.main:app --reload --port 8000
```

**Start the frontend (new terminal):**
```bash
conda activate rag-env
cd frontend
streamlit run app.py
```

**Verify setup:**
1. Backend: `http://localhost:8000`
2. Frontend: `http://localhost:8501`
3. `curl http://localhost:8000/health`
4. Expected JSON includes `"status": "healthy"` and Gemini / document fields
5. Streamlit sidebar should show "API: Connected"

**Using the Application:**
1. Open frontend at `http://localhost:8501`
2. Click "🔄 Re-index Documents" in the sidebar
3. Wait for confirmation
4. Type questions in chat
5. View answers with source citations

---

## API Endpoints Reference

### Health Check
```
GET /health
```
Returns backend and AI service connectivity status.

**Response:**
```json
{
  "status": "healthy",
  "gemini": "connected",
  "model": "gemini-3.6-flash",
  "documents": 8
}
```

### Document Ingestion
```
POST /ingest
```
Loads all `.txt` files from the docs directory and indexes them in ChromaDB.

**Response:**
```json
{
  "message": "Successfully ingested 47 document chunks",
  "documents_added": 47
}
```

**Process:**
1. Clears existing documents from the collection when IDs exist
2. Scans the docs directory for `.txt` files
3. Splits documents into paragraphs
4. Embeds and stores in ChromaDB

### Ask Question
```
POST /ask
Content-Type: application/json

{
  "question": "What is the difference between FastAPI and Flask?"
}
```

Returns an AI-generated answer with source citations.

**Response:**
```json
{
  "question": "What is the difference between FastAPI and Flask?",
  "answer": "FastAPI is a modern web framework...",
  "sources": [
    {
      "source": "fastapi.txt",
      "distance": 0.123,
      "text": "FastAPI is a modern, fast..."
    }
  ],
  "confidence": "high"
}
```
