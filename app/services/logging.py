import logging
from fastapi import Request
import time

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Headers: {dict(request.headers)} | "
        f"Body: {await request.body()} |"
        f"Query Params: {dict(request.query_params)} | "
        f"Client: {request.client.host if request.client else None}"
        
    )
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} | "
        f"Process Time: {process_time:.2f}s"
    )
    
    return response