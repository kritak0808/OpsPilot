from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or []

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        # Trace ID from state (populated via middleware)
        trace_id = getattr(request.state, "trace_id", "unknown-trace")
        
        payload = {
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "trace_id": trace_id,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", "unknown-trace")
        
        payload = {
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
            "details": [{"error_type": type(exc).__name__, "message": str(exc)}],
            "trace_id": trace_id,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        return JSONResponse(status_code=500, content=payload)
