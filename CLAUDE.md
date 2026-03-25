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

## File/Folder Structure Diagram
```
ImageToExcel/
├─ src/
│  ├─ api/
│  │   └─ router.py           # FastAPI routes (extract, health, metrics)
│  ├─ config/
│  │   └─ settings.py         # Environment config, API‑Key
│  ├─ middleware/
│  │   └─ auth_middleware.py # API‑Key validation
│  ├─ services/
│  │   ├─ ingestion_service.py   # Temp file handling
│  │   ├─ ocr_service.py        # Tesseract OCR wrapper
│  │   ├─ extraction_service.py # LangExtract integration
│  │   └─ export_service.py     # CSV / XLSX serialization
│  ├─ schemas/
│  │   ├─ extract_request.py   # Pydantic request model
│  │   └─ extract_response.py  # Pydantic response model
│  └─ errors/
│      └─ app_error.py          # Central error handling
├─ tests/
│  ├─ unit/
│  │   └─ *.test.py            # Unit tests for services & middleware
│  └─ integration/
│      └─ *.test.py            # Integration tests (API endpoints)
├─ docs/
│  └─ slice_catalogue.md       # Vertical slice definitions
├─ Dockerfile
├─ pyproject.toml
└─ README.md
```

**Update Policy:** This diagram should be refreshed at the end of every Claude Code session **or** after every 4–5 structural changes to the codebase to keep it current.


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
- Unit tests: co-located with source (`*.test.py`)
- Integration tests: `/tests/integration/`
- Run: `pytest` for unit, `pytest -m integration` for integration
