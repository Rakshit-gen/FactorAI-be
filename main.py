from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api import tasks, agents, executions
from app.core.database import Base, init_db
from app.core.redis_client import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = init_db()
    Base.metadata.create_all(bind=engine)
    await redis_client.connect()
    yield
    await redis_client.disconnect()

app = FastAPI(
    title="AI Agent Creator API",
    description="Create and manage AI agents dynamically",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(executions.router, prefix="/api/executions", tags=["Executions"])

@app.get("/")
async def root():
    return {
        "message": "AI Agent Creator API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    try:
        await redis_client.ping()
        return {"status": "healthy", "redis": "connected", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
