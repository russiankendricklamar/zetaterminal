"""
Main application entry point for the backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from src.api import compute
from src.api import hjb
from src.api import ccmv
from src.api import stress
from src.api import backtest
from src.api import bond
from src.api import portfolio

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Backend API starting up...")
    yield
    # Shutdown
    print("Backend API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Stochastic Dashboard Backend API",
    description="Backend API для вычислительных задач финансового дашборда",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(compute.router, prefix="/api/compute", tags=["compute"])
app.include_router(hjb.router, prefix="/api/hjb", tags=["hjb"])
app.include_router(ccmv.router, prefix="/api/ccmv", tags=["ccmv"])
app.include_router(stress.router, prefix="/api/stress", tags=["stress"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(bond.router, prefix="/api/bond", tags=["bond"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Stochastic Dashboard Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=debug
    )
