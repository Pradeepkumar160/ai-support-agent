"""
AI Support Agent — FastAPI application.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.db.database import engine, Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup if they don't exist."""
    logger.info("Starting up — creating DB tables if needed...")
    from app.models.all_models import Customer, Order, Ticket  # noqa: F401 — needed for metadata
    Base.metadata.create_all(bind=engine)
    logger.info("DB tables ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="AI Tool-Calling Support Agent",
    description="Production-grade AI customer support with LangGraph, FastAPI, and tool calling.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Restrict to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(health_router)


@app.get("/")
def root():
    return {"message": "AI Support Agent API is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
