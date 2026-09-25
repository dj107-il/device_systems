import logging
import re
from time import perf_counter
from uuid import uuid4

from fastapi import Request

logger = logging.getLogger("uvicorn.error")

async def request_middleware(request: Request, call_next):
    start_time = perf_counter()
    
    request_id = request.headers.get("X-Request-ID", "")
    
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", request_id):
        request_id = str(uuid4())
        
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_id=%s method=%s path=%s status=500",
            request_id,
            request.method,
            request.url.path,
        )
        raise
    
    process_time = perf_counter() - start_time
    
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = request.app.version
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    response.headers["X-Request-ID"] = request_id
    
    logger.info(
        "request_id=%s method=%s path=%s status=%s time=%.6fs",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )
    
    return response