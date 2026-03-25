# Slice Catalogue

This document lists the vertical slices that will be implemented for the PDF/Image extraction service. Each slice is a thin, end‑to‑end flow covering the full stack (API → services → DB → response). The slices are ordered by dependency and risk, and each includes the required tests, touched files, and risk assessment.

```
Slice 1: API‑Key Authentication
  **Micro‑Feature**: Add middleware that validates an `X‑API‑Key` header against a secret stored in the environment and returns 401 when the key is missing or invalid.
  **Acceptance Criteria**:
    1. Request proceeds only when the header matches the configured secret.
    2. Missing or mismatched keys cause a `401 Unauthorized` response with JSON `{ "error": "Invalid API key" }`.
    3. Middleware does not modify the request body or path.
  **Initial Tests**:
    - Happy path: `GET /health` with correct `X‑API‑Key` returns 200 and normal payload.
    - Failure case: `GET /health` with **no** `X‑API‑Key` returns 401 and error JSON.
    - Edge case: `GET /health` with an **incorrect** key returns 401 and error JSON.
  User action:    Client includes an `X‑API‑Key` header and receives a 200 OK when the key is valid.
  Flow:           Request → AuthMiddleware → API‑Key lookup (env/config) → allow request or reject 401.
  Touches:        src/middleware/auth_middleware.py, src/config/settings.py
  Depends on:     none
  Risk:           Medium
  Risk reason:    Must correctly read the secret and reject missing/invalid keys; a mistake would expose the whole service.

  **Micro‑Feature**
  Add middleware that validates an `X‑API‑Key` header against a secret stored in the environment and returns 401 when the key is missing or invalid.

  **Acceptance Criteria**
  1. The request proceeds only when the header matches the configured secret.
  2. Missing or mismatched keys cause an immediate `401 Unauthorized` response with JSON `{ "error": "Invalid API key" }`.
  3. The middleware does not alter the request body or path; it only short‑circuits on failure.

  **Initial Tests**
  - Happy path: `GET /health` with a correct `X‑API‑Key` header returns **200** and the normal health payload.
  - Failure case: `GET /health` with **no** `X‑API‑Key` header returns **401** and the error JSON.
  - Edge case: `GET /health` with an **incorrect** key returns **401** and the same error JSON.

Slice 2: Document Extraction (Upload → OCR → LLM → JSON response)
  **Micro‑Feature**: Create `POST /extract` that stores the uploaded file temporarily, runs OCR, passes text to LangExtract with a predefined schema, and returns extracted data as a JSON array.
  **Acceptance Criteria**:
    1. Accepts only `multipart/form‑data` with a file field `document`.
    2. Returns 200 with JSON array of extracted rows when processing succeeds.
    3. Returns 400 for unsupported file types.
    4. Returns 413 when file exceeds 20 MB.
  **Initial Tests**:
    - Happy path: upload a valid small PDF (mocked OCR/LLM) → 200 with non‑empty JSON array.
    - Failure case: upload a `.txt` file → 400 with error `{ "error": "Unsupported file type" }`.
    - Edge case: upload a PDF larger than 20 MB → 413 with error `{ "error": "File too large" }`.
  **Micro‑Feature**: Create `POST /extract` that stores the uploaded file temporarily, runs OCR, passes text to LangExtract with a predefined schema, and returns extracted data as a JSON array.
  **Acceptance Criteria**:
    1. Accepts only `multipart/form‑data` with a file field `document`.
    2. Returns 200 with JSON array of extracted rows when processing succeeds.
    3. Returns 400 for unsupported file types.
    4. Returns 413 when file exceeds 20 MB.
  **Initial Tests**:
    - Happy path: upload a valid small PDF (mocked OCR/LLM) → 200 with non‑empty JSON array.
    - Failure case: upload a `.txt` file → 400 with error `{ "error": "Unsupported file type" }`.
    - Edge case: upload a PDF larger than 20 MB → 413 with error `{ "error": "File too large" }`.
  User action:    User POSTs a PDF or image to `/extract` and receives a JSON‑serialised DataFrame.
  Flow:           POST /extract → IngestionService (store temp file) → OCRService (Tesseract) → ExtractionService (LangExtract) → JSON response.
  Touches:        src/api/router.py, src/services/ingestion_service.py, src/services/ocr_service.py,
                  src/services/extraction_service.py, src/schemas/extract_request.py,
                  src/schemas/extract_response.py
  Depends on:     Slice 1
  Risk:           High
  Risk reason:    Integration of OCR and LLM must succeed end‑to‑end; any mismatch (e.g., timeout, malformed output) breaks the whole slice.

  **Micro‑Feature**
  Create an endpoint `POST /extract` that stores the uploaded file temporarily, runs Tesseract OCR, passes the text to LangExtract with a predefined schema, and returns the extracted data as a JSON array of rows.

  **Acceptance Criteria**
  1. Accepts only `multipart/form‑data` with a single file field named `document`.
  2. Returns **200** with a JSON body containing an array of extracted rows (`[{...}]`).
  3. Returns **400** when the file type is not PDF/JPEG/PNG.
  4. Returns **413** when the uploaded file exceeds **20 MB**.

  **Initial Tests**
  - Happy path: Upload a valid small PDF (mocked OCR/LLM) → response **200** with a non‑empty JSON array; each row contains the required fields defined in the schema.
  - Failure case: Upload a file with extension `.txt` → response **400** with error `{ "error": "Unsupported file type" }`.
  - Edge case: Upload a PDF larger than 20 MB → response **413** with error `{ "error": "File too large" }`.

Slice 3: Export to CSV / Excel
  **Micro‑Feature**: Extend `GET /extract` with optional `format=csv|xlsx` query parameter to stream the DataFrame in the requested format.
  **Acceptance Criteria**:
    1. `format=csv` returns `Content‑Type: text/csv` and CSV data matching the JSON output.
    2. `format=xlsx` returns appropriate Excel MIME type and a readable file.
    3. Any other `format` value returns 400 with error `{ "error": "Unsupported export format" }`.
  **Initial Tests**:
    - Happy path (CSV): request with `format=csv` → 200, correct MIME, CSV matches JSON rows.
    - Failure case: request with `format=pdf` → 400 and error JSON.
    - Edge case (XLSX): request with `format=xlsx` → 200, correct MIME, file opens and contains same data as JSON.
  **Micro‑Feature**: Extend `GET /extract` with optional `format=csv|xlsx` query parameter to stream the DataFrame in the requested format.
  **Acceptance Criteria**:
    1. `format=csv` returns `Content‑Type: text/csv` and CSV data matching the JSON output.
    2. `format=xlsx` returns appropriate Excel MIME type and a readable file.
    3. Any other `format` value returns 400 with error `{ "error": "Unsupported export format" }`.
  **Initial Tests**:
    - Happy path (CSV): request with `format=csv` → 200, correct MIME, CSV matches JSON rows.
    - Failure case: request with `format=pdf` → 400 and error JSON.
    - Edge case (XLSX): request with `format=xlsx` → 200, correct MIME, file opens and contains same data as JSON.
  User action:    User adds `?format=csv` (or `xlsx`) to the `/extract` request and receives a downloadable file.
  Flow:           GET /extract?format=csv → ExtractionResultService → serialises DataFrame to CSV/XLSX → file stream response.
  Touches:        src/api/router.py (adds query handling), src/services/export_service.py
  Depends on:     Slice 2
  Risk:           Medium
  Risk reason:    Correct MIME type, column ordering, and proper streaming are required; a mistake could corrupt downstream pipelines.

  **Micro‑Feature**
  Extend `GET /extract` to accept an optional query parameter `format=csv|xlsx` and stream the extracted DataFrame in the requested format.

  **Acceptance Criteria**
  1. When `format=csv` the endpoint returns `Content‑Type: text/csv` and a CSV payload that matches the JSON representation.
  2. When `format=xlsx` the endpoint returns `Content‑Type: application/vnd.openxmlformats‑officedocument.spreadsheetml.sheet` and a valid Excel file.
  3. Any other value for `format` results in **400** with an error message.

  **Initial Tests**
  - Happy path (CSV): Request `GET /extract?format=csv` after a successful extraction → response **200**, `Content‑Type: text/csv`, CSV rows match JSON rows.
  - Failure case: Request `GET /extract?format=pdf` → response **400** with error `{ "error": "Unsupported export format" }`.
  - Edge case (XLSX): Request `GET /extract?format=xlsx` → response **200**, `Content‑Type` for Excel, file can be opened and contains the same data as the JSON output.

Slice 4: Health Check
  **Micro‑Feature**: Add lightweight `GET /health` returning `{ "status": "ok" }`.
  **Acceptance Criteria**:
    1. Returns 200 with exact JSON `{ "status": "ok" }`.
    2. Responds within 100 ms.
    3. No stack traces or internal details are exposed.
  **Initial Tests**:
    - Happy path: `GET /health` → 200 and exact JSON.
    - Edge case: response time < 100 ms.
  **Micro‑Feature**: Add lightweight `GET /health` returning `{ "status": "ok" }`.
  **Acceptance Criteria**:
    1. Returns 200 with exact JSON `{ "status": "ok" }`.
    2. Responds within 100 ms.
    3. No stack traces or internal details are exposed.
  **Initial Tests**:
    - Happy path: `GET /health` → 200 and exact JSON.
    - Edge case: response time < 100 ms.

  User action:    User GETs `/health` and receives `{status:"ok"}`.
  Flow:           GET /health → health_check_handler → static JSON response.
  Touches:        src/api/router.py (health endpoint), src/health.py
  Depends on:     none
  Risk:           Low
  Risk reason:    Simple static response; only failure would be a missing route.

  **Micro‑Feature**
  Add a lightweight `GET /health` endpoint that returns a static JSON payload confirming the service is running.

  **Acceptance Criteria**
  1. Returns **200** with JSON `{ "status": "ok" }`.
  2. Must respond within **100 ms** (checked by the test).
  3. No stack traces or internal details are exposed.

  **Initial Tests**
  - Happy path: `GET /health` → **200** and exact JSON `{ "status": "ok" }`.
  - Edge case: Measure response time; test asserts it is **< 100 ms**.

Slice 5: Metrics Endpoint
  **Micro‑Feature**: Expose `GET /metrics` returning Prometheus‑compatible metrics in plain‑text.
  **Acceptance Criteria**:
    1. Returns 200 with `Content‑Type: text/plain; version=0.0.4`.
    2. Includes at least one metric line such as `process_cpu_seconds_total`.
    3. No environment‑derived secrets appear in the output.
  **Initial Tests**:
    - Happy path: `GET /metrics` → 200, correct MIME, contains metric line.
    - Failure case: simulate metrics client failure – endpoint still returns 200 with empty metric set.
    - Edge case: scan response for any occurrence of `SECRET` – none should be present.
  **Micro‑Feature**: Expose `GET /metrics` returning Prometheus‑compatible metrics in plain‑text.
  **Acceptance Criteria**:
    1. Returns 200 with `Content‑Type: text/plain; version=0.0.4`.
    2. Includes at least one metric line such as `process_cpu_seconds_total`.
    3. No environment‑derived secrets appear in the output.
  **Initial Tests**:
    - Happy path: `GET /metrics` → 200, correct MIME, contains metric line.
    - Failure case: simulate metrics client failure – endpoint still returns 200 with empty metric set.
    - Edge case: scan response for any occurrence of `SECRET` – none should be present.
  User action:    Monitoring system scrapes `/metrics` for Prometheus‑compatible metrics.
  Flow:           GET /metrics → metrics_handler → Prometheus client registry → text/plain response.
  Touches:        src/api/router.py (metrics endpoint), src/metrics.py
  Depends on:     none
  Risk:           Low
  Risk reason:    Must correctly expose the registry; a typo could break CI monitoring.

  **Micro‑Feature**
  Expose a `GET /metrics` endpoint that returns Prometheus‑compatible metrics in plain‑text format.

  **Acceptance Criteria**
  1. Returns **200** with `Content‑Type: text/plain; version=0.0.4`.
  2. Includes at least one metric line (e.g., `process_cpu_seconds_total`).
  3. No sensitive environment variables appear in the output.

  **Initial Tests**
  - Happy path: `GET /metrics` → **200**, correct `Content‑Type`, payload contains a line matching `/^process_cpu_seconds_total/`.
  - Failure case: Simulate the metrics client being unavailable (mock) → endpoint still returns **200** with an empty metric set (no crash).
  - Edge case: Scan the response for any occurrence of `SECRET` or other env‑derived values; test asserts none are present.
```