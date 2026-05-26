from __future__ import annotations
import time
import logging
from fastapi import Request

logger = logging.getLogger("telegram_notifier")


async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = int((time.time() - start_time) * 1000)

    logger.info(
        "%s %s %s %dms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response
