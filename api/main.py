"""
AlphaSignal FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent))

from routers import predictions, backtest, rl_agent, news, metrics

# Initialize FastAPI app
app = FastAPI(
    title="AlphaSignal API",
    description="Crude oil price prediction and trading system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtesting"])
app.include_router(rl_agent.router, prefix="/api/rl", tags=["RL Agent"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "AlphaSignal API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )
