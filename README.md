# LegalBot Backend — FastAPI Server

Multi-agent AI backend for **KitaHack hackathon** — helps tenants understand, analyse, and act on tenancy agreements using Malaysian legal statutes.

Covers modules **4.0 Simplify Legalese**, **5.0 ToS Gotcha Analyzer**, and the full **D3/D4 RAG pipeline** (PDF ingestion → vector search → grounded Q&A).

---

## Architecture

```
Frontend
   │
   ▼ REST API (port 8000)
FastAPI Server
   ├── POST /api/v1/simplify          — 4.0 Simplify Legalese (LLM)
   ├── POST /api/v1/gotcha            — 5.0 ToS Gotcha Analyzer (rules + LLM)
   ├── POST /api/v1/analyze           — Runs both in parallel
   ├── POST /api/v1/analyze-agreement — Deep agreement analysis
   ├── POST /api/v1/generate-draft    — Draft letter/response generator
   ├── POST /api/v1/upload            — Upload agreement PDF
   ├── POST /api/v1/rag/ask           — Legacy RAG Q&A (vector search only)
   ├── POST /api/v1/chat/ask          — Chatbot RAG Q&A (grounded, with citations)
   ├── POST /api/v1/d3/sources/{id}/ingest/file  — Ingest PDF into pipeline
   ├── GET  /api/v1/d3/documents/{doc_id}         — Poll ingestion status
   ├── POST /api/v1/rag/sources       — Register a legal source
   └── POST /d4/retrieve              — Raw vector similarity search
          │
          ▼
   AlloyDB (pgvector)
   ├── chunks          — Chunked legal text (D3 output)
   ├── chunk_vectors   — 768-d embeddings, HNSW index (D4)
   └── qa_pairs / qa_citations — Chat session history
```

---

## Project Structure

```
legalbot-backend/
├── app/
│   ├── main.py                  # FastAPI app, CORS, router mounts
│   ├── config.py                # Settings from .env (AlloyDB, GCS, Gemini)
│   ├── agents/
│   │   ├── simplify_agent.py    # 4.0 — Simplify Legalese
│   │   └── gotcha_agent.py      # 5.0 — ToS Gotcha Analyzer
│   ├── routers/
│   │   ├── simplify.py          # POST /api/v1/simplify
│   │   ├── gotcha.py            # POST /api/v1/gotcha
│   │   ├── analyze.py           # POST /api/v1/analyze
│   │   ├── analyze_agreement.py # POST /api/v1/analyze-agreement
│   │   ├── generate_draft.py    # POST /api/v1/generate-draft
│   │   ├── agreement_processing.py  # upload / brief / detail / export
│   │   ├── rag.py               # /api/v1/rag/* (sources + legacy ask)
│   │   └── d3.py                # /api/v1/d3/* (ingest + poll)
│   ├── rag_chatbot/
│   │   ├── router.py            # POST /api/v1/chat/ask
│   │   ├── service.py           # Grounded answer generation
│   │   ├── repository.py        # qa_pairs / qa_citations persistence
│   │   └── prompts.py           # Gemini prompt templates
│   ├── d4_vector_index/
│   │   ├── router.py            # POST /d4/embed, POST /d4/retrieve
│   │   ├── repository.py        # Async SQLAlchemy + pgvector queries
│   │   ├── service.py           # Embedding validation + retrieval logic
│   │   └── embeddings.py        # Google text-embedding-004 (768-d)
│   ├── services/
│   │   ├── ingest_service.py    # D3 pipeline orchestration
│   │   ├── extract_service.py   # PDF → text extraction
│   │   ├── chunk_service.py     # Agentic chunking (LLM-assisted)
│   │   ├── embed_service.py     # Batch embedding + D4 upsert
│   │   ├── rag_service.py       # Legacy RAG retrieval
│   │   └── gcs.py               # Google Cloud Storage upload
│   └── db/
│       ├── alloydb.py           # Sync pg8000 connection pool
│       └── schema.sql           # AlloyDB schema (5 tables, HNSW index)
├── docs/
│   ├── README-pipeline-testing.md   # Guide for ingesting + testing new docs
│   ├── test_sra_pipeline.py         # End-to-end test: Specific Relief Act
│   ├── test_sma_pipeline.py         # End-to-end test: Strata Management Act
│   └── test_distress_act_pipeline.py # End-to-end test: Distress Act 1951
├── requirements.txt
└── .env                         # git-ignored — copy from .env.example
```

---

## Quickstart

### 1. Clone and set up environment

```bash
cd legalbot-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Fill in: LLM_API_KEY, ALLOYDB_*, GCS_*, GOOGLE_APPLICATION_CREDENTIALS
```

### 3. Run the server

```bash
uvicorn app.main:app --port 8000 --workers 2
```

Server: **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**

> Use `--workers 2` (not `--reload`) for production testing. `--reload` with a
> killed process can leave the AlloyDB asyncpg pool in a broken state.

---

## Ingested Legal Documents

| Act | Chunks | Vectors | doc_id (prefix) |
|-----|--------|---------|-----------------|
| Contracts Act 1950 (Act 136) | 183 | 183 | `529be3a2` |
| Strata Management Act 2013 (Act 757) | 133 | 133 | `955ac54a` |
| Specific Relief Act 1950 (Act 137) | 54 | 54 | `3aeafa86` |
| Distress Act 1951 (Act 255) | 19 | 19 | `9069f252` |

All vectors use **Google `text-embedding-004`** (768 dimensions) and are indexed with **HNSW** (`m=16, ef_construction=64`) on AlloyDB.

> To ingest a new document, see [docs/README-pipeline-testing.md](docs/README-pipeline-testing.md).

---

## Key API Endpoints

### `GET /`
Health check.
```json
{ "status": "ok", "service": "LegalBot API", "version": "0.1.0" }
```

---

### `POST /api/v1/chat/ask` — Grounded RAG Chatbot *(primary)*

Answers legal questions grounded against the ingested statute corpus.
Returns confidence level, citations, and follow-up questions.

```json
// Request
{
  "question": "What goods are exempt from distress under the Distress Act?",
  "session_id": "my-session",
  "jurisdiction": "MY",
  "top_k": 5
}

// Response
{
  "answer": "Under Malaysian law, certain goods are exempt...",
  "confidence": "high",
  "citations": [
    {
      "chunk_id": "...",
      "section_title": "Exemptions from Seizable Property",
      "page_start": 7, "page_end": 9,
      "score": 0.82
    }
  ],
  "follow_up_questions": [],
  "qa_id": "259ad181-..."
}
```

Confidence levels: `high` | `low` | `none`

---

### `POST /api/v1/rag/ask` — Legacy RAG Q&A

Simpler vector-search Q&A without session persistence.

```json
// Request
{ "question": "...", "jurisdiction": "MY", "top_k": 5 }

// Response
{ "answer": "...", "citations": [...] }
```

---

### `POST /api/v1/d3/sources/{source_id}/ingest/file` — Ingest PDF

Upload a PDF to the D3 pipeline (extract → chunk → embed).

```bash
curl -X POST http://localhost:8000/api/v1/d3/sources/{source_id}/ingest/file \
  -F "file=@MyAct.pdf"
# Returns: { "doc_id": "...", "status": "pending" }
```

Poll status with `GET /api/v1/d3/documents/{doc_id}` until `status=ready`.

---

### `POST /api/v1/simplify` — 4.0 Simplify Legalese

```json
// Request
{
  "text": "Full agreement text...",
  "sections": [{ "title": "Deposit", "content": "...", "clause_spans": ["..."] }]
}

// Response
{
  "plain_summary": "This agreement covers...",
  "rights": ["Right to quiet enjoyment", "..."],
  "obligations": ["Pay rent on time", "..."]
}
```

---

### `POST /api/v1/gotcha` — 5.0 ToS Gotcha Analyzer

```json
// Response
{
  "red_flags": [
    {
      "clause": "...tenant shall forfeit all deposits...",
      "severity": "critical",
      "risk_score": 0.95,
      "explanation": "Forfeiture clauses can unfairly strip tenants...",
      "suggestion": "Negotiate specific conditions for deposit deductions."
    }
  ],
  "overall_risk_score": 0.84
}
```

Severity levels: `low` | `medium` | `high` | `critical`

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `sources` | Registered legal documents (metadata) |
| `legal_documents` | Ingested document records (status, page count) |
| `chunks` | Chunked text segments from D3 pipeline |
| `chunk_vectors` | 768-d embeddings + HNSW index |
| `qa_pairs` / `qa_citations` | Chat session Q&A history |

Vector index: **HNSW** `(m=16, ef_construction=64)` — updates automatically on insert, no rebuild needed.

---

## Running Tests

```bash
# Specific Relief Act 1950
python docs/test_sra_pipeline.py

# Strata Management Act 2013
python docs/test_sma_pipeline.py

# Distress Act 1951
python docs/test_distress_act_pipeline.py
```

Each test script covers: server health → ingest → pipeline polling → AlloyDB state → D4 retrieval → chatbot Q&A → DB persistence.

---

## Integration Notes

| Direction | Module | Notes |
|-----------|--------|-------|
| **Upstream (3.0)** | Text Processing → this server | Send `CleanedTextInput` to `/api/v1/analyze` |
| **Downstream (7.0)** | Template Generator | Consume `red_flags` + `plain_summary` from `/api/v1/analyze` |
| **Downstream (8.0)** | Reports & Export | Use full `FullAnalysisResponse` + `citations` from `/api/v1/chat/ask` |

