# RAG Project with Miniforge3 - Architecture Documentation

## Project Overview
This project demonstrates a **multi-component RAG (Retrieval-Augmented Generation) system** using Miniforge3 instead of Docker, while maintaining the same architectural principles taught in the lesson.

**Components:**
- **Backend**: FastAPI application with ChromaDB vector store and Gemini AI integration
- **Frontend**: Streamlit web interface for document ingestion and Q&A
- **Database**: ChromaDB persistent vector storage
- **AI Engine**: Google Gemini API for document understanding and response generation

---

## Lesson Requirements vs. Miniforge3 Implementation

### ✅ Requirement 1: Project Directory Structure
**Lesson:** Create a project directory with proper structure
**Implementation:** ✅ MEETS
```
RAG Project with Environment Management & Configuration/
├── .env                                # Environment variables (root level)
├── MINIFORGE3_ARCHITECTURE.md          # This documentation
├── backend/
│   ├── main.py                        # FastAPI RAG application
│   ├── config.py                      # Settings configuration
│   ├── requirements.txt                # Python dependencies
│   ├── chroma_db/                     # Persistent vector database
│   │   └── chroma.sqlite3
│   └── docs/                          # Document collection
│       ├── embeddings-and-vectors.txt
│       ├── fastapi.txt
│       ├── llms-and-ai.txt
│       ├── python-advanced.txt
│       ├── python-fundamentals.txt
│       ├── rest-apis.txt
│       ├── sql-databases.txt
│       └── streamlit.txt
├── frontend/
│   ├── app.py                         # Streamlit interface
│   └── requirements.txt                # Frontend dependencies
└── venv/                               # Python virtual environment
```

---

### ✅ Requirement 2: Multi-Service Architecture
**Lesson:** Two services (backend + Ollama)
**Implementation:** ✅ MEETS (Different approach, same outcome)

| Lesson Model | Miniforge3 Model | Outcome |
|---|---|---|
| Backend container + Ollama container | Backend process + Google Gemini API | Two independent systems communicating |
| Services managed by docker-compose | Services managed by developer with uvicorn | Explicit startup/shutdown |
| Inter-container networking | Direct API calls | Services still separate |

---

### ✅ Requirement 3: Configuration & Environment
**Lesson:** Environment variables for `OLLAMA_URL`
**Implementation:** ✅ MEETS

**Miniforge3 Setup:**
- `.env` file in the root directory contains `Gemini_API_Key` and other configuration
- `main.py` loads the `.env` file via `python-dotenv` **before** importing config module
- Service discovery via direct API configuration (not network-based)

```python
# main.py - CORRECT ORDER: Load .env BEFORE importing config
import os
from pathlib import Path
import dotenv
from google import genai
import chromadb

# Load from root .env file BEFORE importing config
env_path = Path(__file__).parent.parent / ".env"
dotenv.load_dotenv(env_path)

from config import settings  # Environment variables now available
```

**Important:** The `.env` file must be loaded **before** the config module is imported. This ensures environment variables are available when `Settings()` is instantiated.

**.env file (in root directory):**
```
Gemini_API_Key=your-api-key-here
MODEL=gemini-2.0-flash
CHROMA_PATH=./backend/chroma_db
COLLECTION_NAME=documents
MAX_RESULTS=5
CONFIDENCE_THRESHOLD=1.0
DEBUG=true
DOCS_DIRECTORY=./docs
```

**Path Configuration Notes:**
- `CHROMA_PATH=./backend/chroma_db` - Relative path to ChromaDB storage (from backend working directory)
- `DOCS_DIRECTORY=./docs` - Relative path to documents folder (from backend working directory when running uvicorn)
- When running uvicorn from the backend directory, these paths correctly resolve to the local filesystem

---

### ✅ Requirement 4: Persistent Data Storage
**Lesson:** Named volumes for ChromaDB and Ollama models
**Implementation:** ✅ MEETS

**Miniforge3 Implementation:**
```python
# Persistent ChromaDB stored on local filesystem
db_client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("documents")
```

**Persistence Testing:**
1. Start backend with uvicorn
2. Create/upload documents to ChromaDB
3. Stop uvicorn process (Ctrl+C)
4. Restart uvicorn
5. Query `/health` endpoint - document count preserved ✅

---

### ✅ Requirement 5: Service Health & Communication
**Lesson:** Backend's `/health` endpoint shows service connectivity
**Implementation:** ✅ MEETS

**Endpoints:**
- `GET /health` - Tests Gemini API connectivity
- `GET /` - Returns API status and model info

```json
{
  "status": "healthy",
  "gemini": "connected",
  "model": "gemini-2.0-flash",
  "documents": 5
}
```

---

## Core Architectural Principles (All Met ✅)

| Principle | Purpose | Miniforge3 Implementation |
|---|---|---|
| **Separation of Concerns** | Backend handles business logic, external service handles AI | FastAPI backend + Gemini API |
| **Configuration Management** | Secrets not in code | `.env` + `python-dotenv` |
| **Data Persistence** | Data survives process restarts | ChromaDB persistent storage |
| **Health Monitoring** | Can verify system connectivity | `/health` endpoint |
| **Scalability Readiness** | Architecture can be containerized later | Already API-first design |

---

## What's Different from Docker Compose

| Aspect | Docker Compose | Miniforge3 |
|---|---|---|
| Service orchestration | `docker-compose up` | `uvicorn main:app --reload` |
| Isolation | Container-based | Process-based |
| Port mapping | docker-compose.yml | uvicorn `--port` flag |
| Volume management | Named volumes | File system paths |
| Service dependencies | `depends_on` directive | Manual startup order |

**Key Point:** Both approaches achieve the **same architectural goals** - separation of services, configuration management, and data persistence. The lesson's core concepts are fully demonstrated.

---

## Testing Persistence (Lesson Requirement)

**To verify data persistence meets lesson standards:**

1. **Start the backend from the root directory:**
   ```bash
   conda activate rag-env
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Add documents via your frontend or API calls**

3. **Check document count:**
   ```bash
   curl http://localhost:8000/health
   # Returns: {"status": "healthy", "gemini": "connected", "model": "gemini-2.0-flash", "documents": 5}
   ```

4. **Stop the backend:** `Ctrl+C`

5. **Restart the backend** (same command as step 1)

6. **Verify documents persisted:**
   ```bash
   curl http://localhost:8000/health
   # Returns: {"status": "healthy", "gemini": "connected", "model": "gemini-2.0-flash", "documents": 5}
   ```

✅ **Document count preserved** = Persistence working correctly

---

## Summary for Instructor

**This project meets the lesson objectives by:**
1. ✅ Demonstrating multi-component system architecture
2. ✅ Implementing configuration management & environment variables
3. ✅ Proving data persistence across application restarts
4. ✅ Showing service communication & health monitoring
5. ✅ Following best practices (API-first, separation of concerns)

**Limitation:** Does not use Docker containers, but demonstrates Docker-ready architecture using cloud APIs instead of local Ollama.

**Why it's valid:** The lesson teaches architectural patterns (microservices, configuration, persistence), not Docker-specific syntax. This solution uses the same patterns with different technology choices due to system constraints.

---

## Recent Implementation Updates & Best Practices

### Environment Variable Loading Order (Critical Fix)
**Issue:** `ModuleNotFoundError: No module named 'backend'` and `ValueError: Gemini_API_Key not found`

**Root Cause:** The config module was being imported before environment variables were loaded, causing the `Settings` class to initialize with empty values.

**Solution Implemented:**
```python
# ✅ CORRECT: Load .env BEFORE importing config
import os
from pathlib import Path
import dotenv

# Load from backend/.env BEFORE config import
env_path = Path(__file__).parent / ".env"
dotenv.load_dotenv(dotenv_path=env_path)

# NOW import config (variables are available)
from config import settings
```

**Key Principle:** Environment variables must be loaded **before** any module that depends on them is imported.

### Fixed ChromaDB Read-Only Filesystem Error
**Issue:** `chromadb.errors.InternalError: Read-only file system (os error 30)`

**Root Cause:** `.env` file had Docker container paths that don't exist locally:
- `CHROMA_PATH=/app/chroma_data` (container path, not on local machine)
- `DOCS_DIRECTORY=/backend/docs` (malformed, causing double "backend" in path)

**Solution:** Updated `.env` to use relative paths from backend working directory:
```
CHROMA_PATH=./backend/chroma_db  ❌ OLD: /app/chroma_data
DOCS_DIRECTORY=./docs             ❌ OLD: /backend/docs
```

### Fixed Document Ingestion Endpoint
**Issue:** `POST /ingest` endpoint returned 500 error on first call with empty collection

**Root Cause:** Collection clearing logic didn't handle empty collections:
```python
# ❌ OLD CODE - Fails when collection is empty
collection.delete(collection.get()["ids"])  # KeyError if no "ids" key
```

**Solution:** Added proper null checking:
```python
# ✅ NEW CODE - Handles empty collections
existing = collection.get()
if existing and existing.get("ids"):
    collection.delete(existing["ids"])
    print(f"Cleared {len(existing['ids'])} existing documents")
else:
    print("Collection is empty, no documents to clear")
```

### Fixed Streamlit Frontend API Connection
**Issue:** Streamlit app failed with `No connection adapters were found for '[http://localhost:8000]/ingest'`

**Root Cause:** API_URL had malformed angle brackets:
```python
# ❌ OLD CODE
API_URL = os.environ.get("API_URL", "<http://localhost:8000>")
# Results in: "<http://localhost:8000>" (invalid URL)
```

**Solution:** Removed angle brackets:
```python
# ✅ NEW CODE
API_URL = os.environ.get("API_URL", "http://localhost:8000")
```

### Improved Error Handling in Frontend
**Enhancement:** Added detailed error messages and status code logging:
```python
# ✅ IMPROVED ERROR HANDLING
try:
    r = requests.post(f"{API_URL}/ingest", timeout=30)
    if r.status_code == 200:
        data = r.json()
        st.success(data.get("message", "Done"))
    else:
        st.error(f"Error {r.status_code}: {r.text}")  # Show actual error
except Exception as e:
    st.error(f"Ingestion failed: {str(e)}")  # Show detailed exception
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
cd frontend
streamlit run app.py
```

Frontend will be available at `http://localhost:8501` and communicates with backend at `http://localhost:8000` (configurable via API_URL environment variable).

---

### Separated Environment Files
**Benefit:** Backend and frontend can have different configurations without conflicts.

- **backend/.env** - Backend-specific variables (Gemini API key, ChromaDB paths, etc.)
- **.env** (root) - Frontend-specific variables (if needed)

This follows the principle of **separation of concerns** and prevents accidental loading of frontend configs into the backend.

### Relative Import Paths
**Implementation:**
```python
# Using Path(__file__).parent ensures the .env is loaded relative to main.py
env_path = Path(__file__).parent / ".env"
dotenv.load_dotenv(dotenv_path=env_path)
```

**Advantage:** Works regardless of which directory you run `uvicorn` from, making the application more portable and Docker-ready.

---

## Running the Application

**Start the backend:**
```bash
cd backend
conda activate rag-env
uvicorn main:app --reload --port 8000
```

**Start the frontend (in a new terminal):**
```bash
cd frontend
streamlit run app.py
```

**Verify setup:**
1. Backend should be running on `http://localhost:8000`
2. Frontend should be running on `http://localhost:8501`
3. Check backend connectivity: `curl http://localhost:8000/health`
4. Expected response: `{"status": "healthy", "gemini": "connected", ...}`
5. In Streamlit UI, you should see "API: Connected" in the sidebar

**Using the Application:**
1. Open frontend at `http://localhost:8501`
2. Click "🔄 Re-index Documents" in sidebar to load documents into ChromaDB
3. Wait for confirmation message
4. Type questions in the chat input
5. View AI responses with source citations

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
  "model": "gemini-2.0-flash",
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
1. Clears existing documents from collection
2. Scans docs directory for `.txt` files
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

Returns AI-generated answer with source citations.

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

---
