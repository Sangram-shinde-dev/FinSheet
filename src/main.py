from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.api.router import router
from src.middleware.auth_middleware import AuthMiddleware
import os


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Image to Excel Extraction Service",
        description="PDF/Image extraction service with OCR and LLM",
        version="0.1.0",
    )

    # Configure CORS for frontend (development)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add auth middleware (disabled for development)
    # app.add_middleware(AuthMiddleware)

    # Include API routes
    app.include_router(router)

    # Serve frontend static files after build
    frontend_dist = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'dist')
    if os.path.exists(frontend_dist):
        # Mount static assets
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

        # Serve index.html for SPA routes (but not API routes)
        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            # Skip for API, docs, and openapi routes
            if (full_path.startswith('api/') or
                full_path.startswith('docs') or
                full_path.startswith('openapi')):
                return FileResponse(os.path.join(frontend_dist, 'index.html'))

            return FileResponse(os.path.join(frontend_dist, 'index.html'))

    return app


app = create_app()