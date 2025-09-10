Nice — below is a complete, agent-ready plan your contractor can follow to **build a Streamlit FAQ chatbot** that uses **Gemini 2.5 Flash Lite** for embeddings & generation, a **RAG** pipeline over PDFs, **FAISS** as the vector DB, and **chat-memory that persists until the user refreshes** (handled in Streamlit). I give architecture, exact files to produce, sample code templates, deployment notes (Railway primary; Vercel as frontend-only alternative), configuration, testing, and acceptance criteria. The agent can implement this straight away.

# 1 — Project summary (one line)

Build a Streamlit-based chat UI + FastAPI backend that: ingests company PDFs into FAISS, uses Gemini 2.5 Flash Lite for embeddings & response generation within a RAG flow, keeps chat memory in Streamlit session state (cleared on refresh), and is deployable to Railway (backend + Streamlit) with optional frontend-only deployment to Vercel (Next.js) calling the Railway API.

# 2 — High-level architecture

* **Streamlit frontend**

  * chat UI, file upload modal (optional), memory stored in `st.session_state` (cleared on browser refresh), calls backend endpoints for querying and ingestion.
* **FastAPI backend**

  * endpoints: `/ingest` (ingest PDFs), `/query` (RAG + generate), `/health`, `/rebuild-index` (admin).
  * Responsible for vector store management (FAISS) and calling Gemini for embeddings + generation.
* **Vector DB**: FAISS index stored on disk in backend container; index persisted by saving to file (e.g., `faiss.index`) and metadata stored in Postgres or a simple JSON/SQLite file.
* **Storage**: PDFs can be uploaded and stored on disk or cloud bucket (S3-compatible); index persists to disk.
* **Deployment**: Railway preferred (runs long-lived Python process). Optionally, Vercel hosts a Next.js frontend that calls the Railway API. Dockerize both backend and Streamlit for consistent deployment.
* **Secrets**: Gemini API key stored in Railway environment variables.

# 3 — Key non-functional requirements

* Chat memory persists only until user refreshes (no persistent per-user DB required).
* Ingested PDFs must be chunked (overlap) and embedded.
* RAG retrieval: top-K (configurable, default K=5).
* Response latency target: ≤5s (depends on Gemini response time).
* Index persistence and graceful reloading on startup.

# 4 — Tech stack & libs

* Python 3.11+
* FastAPI + Uvicorn/Gunicorn
* Streamlit (latest)
* FAISS (faiss-cpu)
* PyPDF2 or pdfminer.six for PDF text extraction
* sentencepiece or tokenizer library if needed (optional)
* requests / HTTP client for Gemini SDK (or the official provider SDK) — implement as provider SDK wrapper
* pydantic for typed request/response
* python-dotenv for local env during dev
* Docker, docker-compose
* Optional: Redis (if you later want ephemeral server-side sessions), Postgres/SQLite for metadata
* CI: GitHub Actions (optional)

# 5 — Repo layout (single repo recommended)

```
rag-gemini-streamlit/
├─ backend/
│  ├─ app/
│  │  ├─ main.py                # FastAPI app
│  │  ├─ api.py                 # endpoints: /ingest, /query...
│  │  ├─ rag.py                 # retrieval + generation pipeline
│  │  ├─ embeddings_provider.py # wrapper for Gemini embeddings
│  │  ├─ generator_provider.py  # wrapper for Gemini generation
│  │  ├─ faiss_store.py         # FAISS index helper (save/load/add/query)
│  │  ├─ pdf_ingest.py          # pdf extraction + chunking
│  │  └─ config.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/
│  ├─ streamlit_app.py         # Streamlit chat UI
│  ├─ Dockerfile
│  └─ requirements.txt
├─ docker-compose.yml
├─ Procfile
├─ README.md
└─ infra/
   └─ railway.toml (optional)
```

# 6 — Endpoints & behavior (detailed)

**POST /ingest**

* Body: `multipart/form-data` files\[] or `{"s3_url":"..."}`
* Action: extract text → chunk (e.g., 1000–1500 char chunks with 200 char overlap) → call Gemini embeddings → upsert vectors into FAISS along with metadata `{source, page, chunk_id, text}`. Save FAISS index to disk.
* Return: `{status, indexed_chunks}`.

**POST /query**

* Body: `{ "question": "...", "top_k": 5, "session_id": "<optional>" }`
* Action: 1) create embedding for user query with Gemini → 2) search FAISS top\_k → 3) build RAG prompt (include top\_k chunks as context) → 4) call Gemini generation to produce answer → 5) return `{answer, sources:[{source,score}], raw_generation}`.
* Note: backend is stateless for chat memory; the frontend will send the conversation history if you want longer context.

**GET /health**

* returns basic status including FAISS loaded or not.

**POST /rebuild-index** (admin)

* re-run ingestion from stored PDFs.

# 7 — Important implementation details & sample code snippets

> These are templates — the agent should replace `CALL_GEMINI_*` placeholders with the official SDK or proper HTTP calls for Gemini 2.5 Flash Lite.

### 7.1 PDF ingestion & chunking (python pseudocode)

```python
# backend/app/pdf_ingest.py
from typing import List
from PyPDF2 import PdfReader

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)

def chunk_text(text: str, chunk_size=1200, overlap=200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks
```

### 7.2 Embedding wrapper (placeholder)

```python
# backend/app/embeddings_provider.py
def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Replace body with calls to Gemini 2.5 Flash Lite embeddings API.
    For now, raise NotImplementedError or call provider SDK.
    """
    # Example pseudocode:
    # client = GeminiClient(api_key=GEMINI_KEY, model="gemini-2.5-flash-lite")
    # embeddings = client.embed(texts)
    raise NotImplementedError("Wire this to Gemini embeddings")
```

### 7.3 FAISS helper (save/load/query)

```python
# backend/app/faiss_store.py
import faiss, numpy as np, os, json

class FaissStore:
    def __init__(self, dim, index_file="faiss.index", meta_file="meta.json"):
        self.dim = dim
        self.index_file = index_file
        self.meta_file = meta_file
        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
            with open(meta_file, "r") as f:
                self.meta = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(dim)  # or IndexFlatL2 + normalize
            self.meta = []

    def add(self, embeddings: list[list[float]], metas: list[dict]):
        arr = np.array(embeddings).astype("float32")
        self.index.add(arr)
        self.meta.extend(metas)
        self.save()

    def query(self, emb: list[float], k=5):
        arr = np.array([emb]).astype("float32")
        scores, ids = self.index.search(arr, k)
        results = []
        for idx, score in zip(ids[0], scores[0]):
            if idx < len(self.meta):
                results.append({"meta": self.meta[idx], "score": float(score)})
        return results

    def save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "w") as f:
            json.dump(self.meta, f)
```

### 7.4 RAG orchestration (backend)

* Generate query embedding.
* Retrieve top-K chunks from FAISS.
* Compose prompt:

  * System instruction: teaching assistant for company docs.
  * Context: top K chunks with source references.
  * User message: include user question and optionally last few user/assistant messages (if frontend sends them).
* Call Gemini generate with the constructed prompt, set `max_tokens`, `temperature`, and safety settings.

### 7.5 Streamlit memory behavior (frontend)

* Use `st.session_state["history"]` to store message pairs. This is automatic until user refreshes the page (satisfies your requirement).
* When sending query to backend, include the last N messages if you want the backend to condition generation on them (optional).

```python
# frontend/streamlit_app.py (excerpt)
import streamlit as st
import requests

st.set_page_config(page_title="RAG Gemini Chat")
if "history" not in st.session_state:
    st.session_state["history"] = []

question = st.text_input("Ask about company docs")
if st.button("Send"):
    st.session_state["history"].append({"role":"user","text":question})
    # Option A: simply call backend with question
    resp = requests.post(API_URL+"/query", json={"question": question, "top_k": 5})
    data = resp.json()
    st.session_state["history"].append({"role":"assistant","text": data["answer"]})
for msg in st.session_state["history"]:
    st.write(f"**{msg['role']}**: {msg['text']}")
```

# 8 — Deployment config examples

### 8.1 Backend Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

### 8.2 Frontend Dockerfile (Streamlit)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/streamlit_app.py .
ENV STREAMLIT_SERVER_HEADLESS=true
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 8.3 docker-compose (local dev)

```yaml
version: "3.8"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
  streamlit:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
```

### 8.4 Procfile (Railway)

```
web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000}
streamlit: streamlit run frontend/streamlit_app.py --server.port=${PORT:-8501}
```

(You may opt to run both in single container or deploy backend + streamlit as separate services on Railway.)

# 9 — Deployment recommended approach

* **Railway**: Deploy backend + streamlit together on Railway. Option A: run a single container that launches both processes (supervisor) — simpler but less modular. Option B (preferred): create two Railway services: one for backend, one for Streamlit. Configure env vars in Railway for keys.
* **Vercel**: Not ideal for Streamlit (serverless). If you want Vercel, use Vercel for a Next.js frontend only; Streamlit stays in Railway. Next.js can provide nicer UI. Keep Streamlit for internal usage or rapid prototyping.
* **Alternative**: Hugging Face Spaces is Streamlit-friendly (but check Gemini access from there).

# 10 — Security & governance

* Keep Gemini API key in Railway secrets — never in repo.
* Sanitize user-uploaded PDFs before ingestion (scan for macros or malware if necessary).
* Rate-limit endpoint and apply request size limits.
* Add logging but avoid storing PII in logs. If the data is sensitive, ensure encryption-at-rest for stored PDFs and consider role-based access.

# 11 — Testing & QA

* Unit tests for: PDF chunking, FAISS add/query, embedding wrapper (mocked), RAG prompt builder.
* Integration test: ingest a sample PDF and run a query expecting a known snippet in answer.
* Load test: simulate multiple queries to estimate Gemini costs & latency.

# 12 — Monitoring & observability

* Basic logs to stdout (Railway collects logs).
* Add Sentry for exception monitoring (optional).
* Periodic health checks to ensure FAISS loaded and Gemini key valid.

# 13 — Cost & limits notes (for the agent to pass on)

* Gemini usage costs (embeddings + generation) will dominate. Agent should add usage controls (max tokens, batching embeddings for ingestion).
* FAISS is cheap (compute & storage). Storage of large PDF corpora may require object storage.

# 14 — Deliverables for acceptance (what you give the agent)

1. Git repo (complete) with the structure above.
2. Working ingestion endpoint plus script to ingest a set of sample PDFs.
3. Streamlit UI that can: upload a PDF, ask questions, show sources returned from RAG, and preserve memory until refresh.
4. Dockerfiles + docker-compose for local dev.
5. Railway deployment config & steps (or deployed Railway project URL).
6. README with run & deploy steps and environment variables list.
7. Basic unit/integration tests and instructions to run them.
8. Simple cost/latency estimation doc for monthly usage assumptions.

# 15 — Acceptance tests (what you, as owner, will check)

* Ingest three sample company PDFs via `/ingest`. Confirm FAISS index file created.
* Query a question that the PDFs contain; answer includes content from PDFs and `sources` list present.
* Memory: Chat multiple turns; confirm UI shows prior messages while session is active; refresh page → history cleared.
* Deploy: both backend and streamlit are reachable on Railway (or backend reachable if streamlit is client-side on Vercel).
* Index persistence: restart backend → FAISS index reloaded and queries still work.

# 16 — Implementation timeline estimate for the agent (guideline for planning)

* Dev environment & skeleton: 1–2 days
* PDF ingestion + FAISS store + embeddings integration: 2–3 days
* RAG + Gemini generation integration: 1–2 days (plus provider SDK wiring)
* Streamlit UI + memory: 1 day
* Docker + deploy to Railway: 1 day
* Tests, docs, QA: 1–2 days
  (Agent should provide specific dates in their plan — this is only a guideline.)

# 17 — Example checklist the agent can tick (quick)

* [ ] Build FastAPI endpoints: /ingest, /query, /health
* [ ] Implement PDF text extraction & chunking
* [ ] Wire Gemini embeddings + generation (Gemini 2.5 Flash Lite)
* [ ] Implement FAISS persistence & metadata store
* [ ] Build Streamlit chat UI with session\_state memory
* [ ] Dockerize & add docker-compose
* [ ] Deploy to Railway (backend + streamlit)
* [ ] Provide README, tests, and acceptance demo

# 18 — Helpful tips for the agent (implementation gotchas)

* Batch embeddings during ingestion to reduce API calls.
* Normalize embeddings if using inner product similarity.
* Keep chunk size tuned: too small → loss of context; too large → fewer chunks but expensive embeddings. Start with 1000–1500 tokens (or characters) with 10–20% overlap.
* If documents are large, track `source_page` in metadata to show to user.

---

If you want, I can:

* produce the **exact ready-to-run code** for backend FastAPI + FAISS + placeholder Gemini calls and a Streamlit UI (complete files: `main.py`, `faiss_store.py`, `streamlit_app.py`, Dockerfiles).
* or produce a **detailed Railway deployment script** and `railway.toml`.

Which one do you want me to generate next? (I can output the full code files right now.)
