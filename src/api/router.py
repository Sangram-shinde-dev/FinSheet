"""API routes for the extraction service."""
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

import pandas as pd

from src.services.ingestion_service import handle_upload, cleanup_temp_file
from src.services.ocr_service import ocr_service
from src.services.extraction_service import extraction_service
from src.services.export_service import export_service
from src.errors.app_error import AppError, UnsupportedFileTypeError, FileTooLargeError

router = APIRouter()


@router.get("/health")
async def health_check():
    """Lightweight health check endpoint."""
    return {"status": "ok"}


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    from prometheus_client import REGISTRY

    # Import all metrics to ensure they're registered
    try:
        import process_collector
    except ImportError:
        pass

    return JSONResponse(
        content=generate_latest(REGISTRY).decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )


@router.post("/extract")
async def extract_document(
    document: UploadFile = File(...),
    format: Optional[str] = Query(default=None, pattern="^(csv|xlsx)$")
):
    """
    Extract structured data from uploaded document.

    Accepts PDF, JPEG, JPG, or PNG files and returns extracted data
    as JSON (default) or in CSV/Excel format.
    """
    temp_path = None

    try:
        # Handle file upload and validation
        temp_path, file_ext = await handle_upload(document)

        # Run OCR
        text = ocr_service.extract_text(temp_path, file_ext)

        # Extract structured data (pass image path for fallback if OCR fails)
        df = extraction_service.extract_to_dataframe(text, image_path=temp_path)

        # Handle export format
        if format:
            file_bytes, mime_type = export_service.export(df, format)
            return StreamingResponse(
                iter([file_bytes]),
                media_type=mime_type,
                headers={
                    "Content-Disposition": f"attachment; filename=extraction.{format}"
                }
            )

        # Default: return JSON
        data = df.to_dict(orient="records")
        return {
            "data": data,
            "row_count": len(data)
        }

    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        if temp_path:
            cleanup_temp_file(temp_path)
