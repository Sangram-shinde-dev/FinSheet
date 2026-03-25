# Project Progress

## Overview

This document tracks the development progress of the **Image to Excel Extraction Service**. The project follows a vertical slice approach, implementing end-to-end features incrementally.

---

## Completed Slices

### Slice 1: API-Key Authentication ✅

**Status**: Implemented (Currently Disabled)

**Description**: Added middleware that validates an `X-API-Key` header against a secret stored in the environment.

**Implementation Details**:
- Created `src/middleware/auth_middleware.py` with `AuthMiddleware` class
- Validates `X-API-Key` header against `settings.api_key`
- Returns 401 Unauthorized with `{"error": "Invalid API key"}` for missing/invalid keys
- Skips auth validation for `/health` and `/metrics` endpoints
- Added to `src/config/settings.py` with default dev key

**Files Touched**:
- `src/middleware/auth_middleware.py` (created)
- `src/config/settings.py` (updated)

**Note**: Middleware is currently commented out in `src/main.py` for development convenience.

---

### Slice 2: Document Extraction ✅

**Status**: Fully Implemented

**Description**: Created `POST /extract` endpoint that stores uploaded files temporarily, runs OCR, passes text to LLM, and returns extracted data as JSON.

**Implementation Details**:
- **Ingestion Service** (`src/services/ingestion_service.py`):
  - Validates file type (PDF, JPEG, JPG, PNG only)
  - Validates file size (max 20MB)
  - Saves files to temp directory with unique names
  - Handles cleanup after processing

- **OCR Service** (`src/services/ocr_service.py`):
  - Uses Tesseract OCR (Windows path: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
  - Preprocesses images (grayscale, contrast enhancement)
  - Extracts text from images via `pytesseract`
  - Extracts text from PDFs via `PyPDF2`
  - Falls back to LLM vision if OCR returns empty text

- **Extraction Service** (`src/services/extraction_service.py`):
  - Uses Ollama LLM (`qwen3.5:397b-cloud`) for structured data extraction
  - Builds prompts for text and image-based extraction
  - Supports JSON output format from LLM
  - Converts extracted data to pandas DataFrame
  - Includes schema validation method

**Files Touched**:
- `src/api/router.py` (added `/extract` endpoint)
- `src/services/ingestion_service.py` (created)
- `src/services/ocr_service.py` (created)
- `src/services/extraction_service.py` (created)
- `src/schemas/extract_request.py` (created)
- `src/schemas/extract_response.py` (created)

---

### Slice 3: Export to CSV/Excel ✅

**Status**: Fully Implemented

**Description**: Extended `/extract` endpoint with optional `format` query parameter to export data in CSV or XLSX format.

**Implementation Details**:
- Created `src/services/export_service.py`:
  - `export_to_csv()`: Returns CSV bytes with MIME type `text/csv`
  - `export_to_xlsx()`: Returns Excel bytes with MIME type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `export()`: Dispatches to appropriate format handler
- Updated `/extract` endpoint to handle `format=csv` and `format=xlsx` query params
- Returns streaming response with proper `Content-Disposition` headers

**Files Touched**:
- `src/api/router.py` (updated)
- `src/services/export_service.py` (created)

---

### Slice 4: Health Check ✅

**Status**: Fully Implemented

**Description**: Added lightweight `GET /health` endpoint returning `{"status": "ok"}`.

**Implementation Details**:
- Added to `src/api/router.py`
- Returns 200 status with static JSON response
- No internal details exposed
- Does not require authentication

**Files Touched**:
- `src/api/router.py` (updated)

---

### Slice 5: Metrics Endpoint ✅

**Status**: Fully Implemented

**Description**: Exposed `GET /metrics` endpoint returning Prometheus-compatible metrics.

**Implementation Details**:
- Added to `src/api/router.py`
- Uses `prometheus_client` library
- Returns metrics in Prometheus text format
- Skips auth validation (no secrets exposed)
- Content-Type: `text/plain; version=0.0.4`

**Files Touched**:
- `src/api/router.py` (updated)

---

## Project Structure (Current)

```
ImageToExcel/
├── src/
│   ├── main.py                         # FastAPI app factory
│   ├── api/
│   │   └── router.py                   # All API routes
│   ├── config/
│   │   └── settings.py                 # Environment configuration
│   ├── middleware/
│   │   └── auth_middleware.py          # API-Key authentication
│   ├── services/
│   │   ├── ingestion_service.py        # File upload handling
│   │   ├── ocr_service.py              # Tesseract OCR
│   │   ├── extraction_service.py       # Ollama LLM integration
│   │   └── export_service.py           # CSV/XLSX export
│   ├── schemas/
│   │   ├── extract_request.py          # Request models
│   │   └── extract_response.py         # Response models
│   ├── errors/
│   │   └── app_error.py                # Custom error classes
│   └── __init__.py
├── docs/
│   ├── SLICE_CATALOGUE.md              # Feature specifications
│   ├── PROJECT_FRAMING.md              # Project context
│   └── Progress.md                     # This file
├── .env.example                        # Environment template
├── .venv/                              # Virtual environment
├── pyproject.toml                      # Python project configuration
├── Dockerfile                          # Container configuration
├── README.md                           # Documentation
└── CLAUDE.md                           # Architecture contract
```

---

## API Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/health` | No | Health check - returns `{"status": "ok"}` |
| GET | `/metrics` | No | Prometheus metrics |
| POST | `/extract` | Yes* | Upload document, get extracted data |

*Note: Auth middleware is currently disabled for development.

### POST /extract Details

**Request**:
- Content-Type: `multipart/form-data`
- Field: `document` (file upload)
- Supported types: `.pdf`, `.jpeg`, `.jpg`, `.png`
- Max size: 20MB

**Query Parameters**:
- `format` (optional): `csv` or `xlsx`

**Response** (default JSON):
```json
{
  "data": [...extracted rows...],
  "row_count": 42
}
```

**Response** (file download):
- Content-Disposition: `attachment; filename=extraction.{format}`
- Streamed file bytes

---

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `dev-api-key-change-in-production` | Authentication key |
| `DATABASE_URL` | `postgresql://localhost:5432/image_to_excel` | PostgreSQL connection |
| `MAX_FILE_SIZE_MB` | `20` | Maximum upload size |

---

## External Dependencies

### Required Services
- **Tesseract OCR**: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **Ollama**: `http://localhost:11434` (model: `qwen3.5:397b-cloud`)

### Optional/Not Yet Integrated
- **PostgreSQL**: Not yet integrated (placeholder in config)

---

## Next Steps (Potential Improvements)

1. **Enable Authentication**: Uncomment auth middleware in production
2. **Database Integration**: Implement PostgreSQL storage using SQLAlchemy repository pattern
3. **Image-based PDF OCR**: Add full support for image-based PDFs using pdf2image or similar
4. **Testing**: Add unit and integration tests as per CLAUDE.md conventions
5. **Error Handling Improvements**: Add more specific error messages and logging
6. **Rate Limiting**: Add request rate limiting per API key
7. **Logging**: Add structured JSON logging
8. **Job Tracking**: Implement `/jobs/{job_id}` endpoints for async processing

---

## Progress Summary

| Slice | Feature | Status |
|-------|---------|--------|
| 1 | API-Key Authentication | ✅ Implemented (Disabled) |
| 2 | Document Extraction | ✅ Complete |
| 3 | Export to CSV/Excel | ✅ Complete |
| 4 | Health Check | ✅ Complete |
| 5 | Metrics Endpoint | ✅ Complete |

**Overall Progress**: 5/5 MVP slices completed

---

*Last Updated: 2026-03-23*