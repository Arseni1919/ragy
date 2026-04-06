"""
Middleware for demo/read-only mode.
Blocks write operations (create, delete, upload) in hosted demo.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os

class ReadOnlyMiddleware(BaseHTTPMiddleware):
    """Block write operations in demo mode."""

    async def dispatch(self, request: Request, call_next):
        # Check if demo mode is enabled
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

        if not demo_mode:
            return await call_next(request)

        # Block write operations
        write_endpoints = [
            "/api/v1/index/create",
            "/api/v1/database/collection/",  # DELETE
            "/api/v1/upload/csv",
            "/api/v1/system/scheduler/jobs/create",
            "/api/v1/system/scheduler/jobs/delete",
        ]

        for endpoint in write_endpoints:
            if request.url.path.startswith(endpoint):
                if request.method in ["POST", "DELETE", "PUT", "PATCH"]:
                    raise HTTPException(
                        status_code=403,
                        detail="Demo mode: Write operations are disabled. "
                               "Clone the repo to run your own instance: "
                               "https://github.com/Arseni1919/ragy"
                    )

        return await call_next(request)
