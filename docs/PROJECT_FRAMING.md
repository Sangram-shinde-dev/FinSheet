# Engineering Brief

---

### SECTION 1 — Problem Definition

```
What are we building?   A backend‑only service that ingests PDFs and images, extracts tabular/structured information via OCR + LLM, and returns the data as a Pandas‑like DataFrame (or CSV/Excel/DB) through a REST API.

Who is it for?          Internal developers / data‑engineering teams who need to turn unstructured documents into structured datasets quickly.

What does "done" mean?  An API endpoint `/extract` accepts a PDF or image, runs OCR + LangExtract, and returns a JSON‑serialised DataFrame with > 95 % field‑level accuracy. A simple CLI wrapper can invoke the same functionality locally.

What does success look like?
- > 95 % extraction accuracy on a validation set of 100 diverse documents.
- End‑to‑end latency ≤ 2 s for a typical 2‑page PDF.
- All core functionality covered by unit tests (≥ 80 % coverage) and integration tests.
- Documentation and example scripts for local development.
```

---

### SECTION 2 — Core Features

```
Feature: Upload Document
  What it does:    Accepts a PDF or image (PNG/JPEG) via multipart/form‑data.
  Who uses it:    Backend developers / scripts.
  Priority:        P0
  Scope:           MVP

Feature: OCR Extraction
  What it does:    Runs Tesseract OCR to produce plain text from the uploaded file.
  Who uses it:    Internal extraction pipeline.
  Priority:        P0
  Scope:           MVP

Feature: LLM‑driven Structured Extraction
  What it does:    Calls LangExtract (Gemini‑2.5‑flash) with a user‑defined schema to turn raw text into a structured DataFrame.
  Who uses it:    Developers needing structured output.
  Priority:        P0
  Scope:           MVP

Feature: JSON DataFrame Response
  What it does:    Serialises the DataFrame to JSON (records format) and returns it to the caller.
  Who uses it:    API clients / CLI scripts.
  Priority:        P0
  Scope:           MVP

Feature: Export to CSV/Excel
  What it does:    Provides optional query parameters to download the result as CSV or XLSX.
  Who uses it:    Users who want portable files.
  Priority:        P1
  Scope:           Post‑MVP

Feature: Persist Extraction Results
  What it does:    Saves the extracted DataFrame into a PostgreSQL table for later retrieval.
  Who uses it:    Teams building data pipelines.
  Priority:        P2
  Scope:           Post‑MVP

Feature: Health / Metrics Endpoint
  What it does:    Exposes `/health` and Prometheus metrics for observability.
  Who uses it:    Ops / monitoring.
  Priority:        P1
  Scope:           Post‑MVP

Feature: Simple Authentication (API Key)
  What it does:    Requires a static API‑Key header for all endpoints.
  Who uses it:    All callers.
  Priority:        P1
  Scope:           Post‑MVP
```

---

### SECTION 3 — Non‑Functional Requirements

```
Performance:    ≤ 200 ms avg OCR per page; ≤ 1 s total extraction latency for ≤ 5‑page docs (p95).
Scale:          Support 10 concurrent extraction requests at launch; design for 200 RPS after 12 months.
Availability: 99.5 % uptime (rolling 30‑day window).
Security:      API‑Key auth; no data stored without encryption at rest; input size limits (max 20 MB).
⚠ ASSUMPTION: No PII‑specific compliance (e.g., HIPAA) required; can be added later.
Deployment:    Docker containers on a single‑node Linux VM (local dev); easy to move to any cloud provider.
Observability: Structured logs (JSON) via Pino; metrics via Prometheus; error tracking via Sentry (optional).
Accessibility:  N/A (API‑only service).
```

---

### SECTION 4 — Architecture Boundaries

```
Module: Ingestion
  Owns:       Receiving multipart uploads, validating file type/size, storing temporary files.
  Does NOT:   Perform any OCR or LLM calls.
  Depends on: utils, config.

Module: OCR
  Owns:       Converting PDFs/images to plain text using Tesseract.
  Does NOT:   Access the database or expose HTTP routes.
  Depends on: Ingestion, utils.

Module: Extraction
  Owns:       Calling LangExtract with the OCR text, enforcing schema, returning a DataFrame object.
  Does NOT:   Read/write files directly (receive text only).
  Depends on: OCR, config.

Module: Export
  Owns:       Serialising DataFrames to JSON, CSV, XLSX; optional DB persistence.
  Does NOT:   Perform OCR or LLM calls.
  Depends on: Extraction, storage (optional).

Module: API
  Owns:       All HTTP endpoints (`/extract`, `/health`, `/metrics`), API‑Key validation, request routing.
  Does NOT:   Run OCR/LLM directly (delegates to other modules).
  Depends on: Ingestion, OCR, Extraction, Export, auth.

Module: Storage
  Owns:       PostgreSQL schema, repository pattern for persisting extraction results.
  Does NOT:   Call Tesseract or LangExtract.
  Depends on: config.
```

---

### SECTION 5 — Tech Stack

```
Language / Runtime:   Python 3.12 (strict typing)
Framework:           FastAPI
Database:            PostgreSQL 15 via SQLAlchemy + Prisma‑style repository layer
Auth:                Simple API‑Key header (configurable)
Queue / Events:      None (synchronous processing) – can add Celery later
File Storage:        Local temporary directory (./tmp) – can swap to S3 later
Testing:             Pytest + httpx + pytest‑asyncio
CI/CD:               GitHub Actions (lint, test, build Docker image)
Observability:       Pino‑style JSON logs (structlog), Prometheus client, optional Sentry
OCR Engine:          Tesseract 5 (via pytesseract)
LLM Extraction:       LangExtract (Gemini‑2.5‑flash backend, also supports OpenAI)
DataFrames:          Polars (faster than pandas) – serialises to JSON/CSV/XLSX
Containerisation:    Docker (official python base image)
```

---

### SECTION 6 — Data Model Sketch

```
Entity: ExtractionJob
  Fields:        id, user_api_key, filename, status, created_at, completed_at
  Relationships: has many ExtractionResult

Entity: ExtractionResult
  Fields:        id, job_id, row_index, column_name, value, source_text, confidence
  Relationships: belongs to ExtractionJob
```

---

### SECTION 7 — API Surface (High Level)

```
POST   /extract               (multipart upload → JSON/CSV/XLSX)
GET    /health
GET    /metrics
GET    /jobs/{job_id}         (retrieve job status or results)
GET    /jobs/{job_id}/download?format=csv|xlsx|json
```

---

### SECTION 8 — Risk Register

```
Risk: OCR inaccuracies on low‑quality scans
Severity: High
Mitigation: Reject files < 300 dpi; provide clear error message; allow optional pre‑processing (deskew, denoise).

Risk: LLM hallucination / incorrect schema mapping
Severity: Medium
Mitigation: Use few‑shot examples; validate output against JSON schema; add unit tests covering edge cases.

Risk: API‑Key leakage / unauthorised use
Severity: Medium
Mitigation: Store API keys in env var; enforce rate‑limit (e.g., 10 RPS per key); log all accesses.

Risk: Dependency breakage (tesseract / LangExtract version changes)
Severity: Low
Mitigation: Pin exact versions in `requirements.txt`; run integration tests in CI on each PR.

Risk: Data privacy – uploaded documents may contain sensitive info
Severity: Medium
Mitigation: Run service locally only (no external storage) in MVP; add optional at‑rest encryption for DB.
```

---

### SECTION 9 — CLAUDE.md Bootstrap

```
# Project Architecture Contract

## Stack
- Runtime:   Python 3.12
- Framework: FastAPI
- DB:        PostgreSQL 15 (SQLAlchemy repository pattern)
- Testing:   Pytest + httpx

## Module Boundaries
- Ingestion: Owns receiving multipart uploads, validating file type/size. Does NOT perform OCR or LLM calls. Depends on utils, config.
- OCR: Owns converting PDFs/images to plain text via Tesseract. Does NOT access the database or expose HTTP routes. Depends on Ingestion, utils.
- Extraction: Owns calling LangExtract with OCR text, enforcing schema, returning a DataFrame. Does NOT read/write files directly. Depends on OCR, config.
- Export: Owns serialising DataFrames to JSON, CSV, XLSX; optional DB persistence. Does NOT run OCR or LLM calls. Depends on Extraction, storage (optional).
- API: Owns all HTTP endpoints (`/extract`, `/health`, `/metrics`), API‑Key validation, request routing. Does NOT run OCR/LLM directly. Depends on Ingestion, OCR, Extraction, Export, auth.
- Storage: Owns PostgreSQL schema, repository pattern for persisting extraction results. Does NOT call Tesseract or LangExtract. Depends on config.

## Patterns to Follow
- All errors must go through `src/errors/AppError.ts`  ⚠ ASSUMPTION: In Python we map this to a central `app.errors` module.
- All DB access through repository pattern — no ORM calls in controllers.
- Validation via Zod schemas in `src/schemas/`  ⚠ ASSUMPTION: In Python we use Pydantic models for request/response validation.

## Naming Conventions
- Files: kebab-case
- Functions: camelCase
- Types/Interfaces: PascalCase

## Do NOT Do These
- Do not install new npm packages without explicit approval
- Do not modify migration files once created
- Do not add logic to route files — route files call service functions only
- Do not change public API interfaces without flagging it first

## Test Conventions
- Unit tests: co‑located with source (`*.test.py`)
- Integration tests: `/tests/integration/`
- Run: `pytest` for unit, `pytest -m integration` for integration
```

---

*End of Engineering Brief*