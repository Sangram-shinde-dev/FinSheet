# Image to Excel Extraction Service

PDF/Image extraction service with OCR and LLM integration.

## Quick Start

1. Install dependencies:
```bash
pip install -e ".[dev]"
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Run the server:
```bash
uvicorn src.main:app --reload
```

4. Test the health endpoint:
```bash
curl http://localhost:8000/health
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (no auth required) |
| `/metrics` | GET | Prometheus metrics (no auth required) |
| `/extract` | POST | Extract data from PDF/image (requires X-API-Key) |

## Authentication

All endpoints except `/health` and `/metrics` require an `X-API-Key` header.

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

## Configuration

See `.env.example` for available environment variables.
