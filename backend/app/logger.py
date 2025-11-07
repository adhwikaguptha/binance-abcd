import logging
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Custom filter to attach extra fields to log records
class ExtraFieldsFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = getattr(record, "trace_id", "no-trace")
        record.user_id = getattr(record, "user_id", "anonymous")
        record.route = getattr(record, "route", "unknown")
        record.extra = getattr(record, "extra", {})
        return True


logger = logging.getLogger()

def setup_logging(app=None):
    """Configure logging and optionally attach middleware to FastAPI app."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(trace_id)s %(user_id)s %(route)s %(message)s"
    )
    logger.addFilter(ExtraFieldsFilter())
    logging.getLogger("uvicorn").addFilter(ExtraFieldsFilter())
    logging.getLogger("uvicorn.access").addFilter(ExtraFieldsFilter())

    if app:
        app.add_middleware(LoggingMiddleware)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        user_id = request.headers.get("X-User-Id", "anonymous")
        route = request.url.path
        extra = {"trace_id": trace_id, "user_id": user_id, "route": route, "extra": {}}
        logger.info("Request started", extra=extra)
        response = await call_next(request)
        logger.info("Request completed", extra=extra)
        response.headers["X-Trace-Id"] = trace_id
        return response
