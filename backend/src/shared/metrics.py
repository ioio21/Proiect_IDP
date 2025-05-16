"""Prometheus instrumentation for FastAPI applications."""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from typing import Callable
import time

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests Count',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Latency',
    ['method', 'endpoint']
)

def setup_metrics(app: FastAPI) -> None:
    """Setup Prometheus metrics middleware and endpoint for a FastAPI application."""
    
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next: Callable) -> Response:
        """Middleware to track request count and latency."""
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Record request latency
        latency = time.time() - start_time
        endpoint = request.url.path
        REQUEST_LATENCY.labels(
            method=request.method, 
            endpoint=endpoint
        ).observe(latency)
        
        # Record request count
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=endpoint, 
            status_code=response.status_code
        ).inc()
        
        return response
    
    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        """Endpoint that exposes Prometheus metrics."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )