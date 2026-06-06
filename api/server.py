#!/usr/bin/env python3
"""
MEOK AI Labs - API Server
FastAPI application with all endpoints
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List
import uuid

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx

from meokai.config import settings
from meokai.database import get_db, init_db
from meokai.governance import ConstitutionalAnalyzer
from meokai.memory import VectorStore
from meokai.rate_limiter import RateLimiter
from meokai.auth import verify_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="MEOK AI Labs API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_limiter = RateLimiter()
governance = ConstitutionalAnalyzer()
memory_store = VectorStore()


class AnalyzeRequest(BaseModel):
    content: str
    framework: str = "constitutional"
    type: str = "text"


class AnalyzeResponse(BaseModel):
    id: str
    score: float
    passed: bool
    violations: List[dict]
    recommendations: List[str]
    framework: str
    timestamp: str


class MemoryRequest(BaseModel):
    content: str
    type: str = "episodic"
    tags: List[str] = []
    importance: float = Field(default=0.5, ge=0, le=1)


class MemoryResponse(BaseModel):
    id: str
    type: str
    tags: List[str]
    importance: float
    created_at: str


class TaskRequest(BaseModel):
    instruction: str
    priority: str = "normal"


class TaskResponse(BaseModel):
    id: str
    agent_id: str
    status: str
    created_at: str


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/governance/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    api_key: str = Depends(verify_api_key),
):
    await rate_limiter.check(api_key)

    result = await governance.analyze(
        content=request.content,
        framework=request.framework,
        content_type=request.type,
    )

    return AnalyzeResponse(
        id=str(uuid.uuid4()),
        score=result["score"],
        passed=result["passed"],
        violations=result.get("violations", []),
        recommendations=result.get("recommendations", []),
        framework=request.framework,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/governance/compliance")
async def check_compliance(
    content: str,
    standards: List[str],
    api_key: str = Depends(verify_api_key),
):
    await rate_limiter.check(api_key)

    results = await governance.check_compliance(content, standards)
    return results


@app.post("/memory", response_model=MemoryResponse)
async def store_memory(
    request: MemoryRequest,
    api_key: str = Depends(verify_api_key),
):
    await rate_limiter.check(api_key)

    memory_id = await memory_store.store(
        user_id=api_key,
        content=request.content,
        memory_type=request.type,
        tags=request.tags,
        importance=request.importance,
    )

    return MemoryResponse(
        id=memory_id,
        type=request.type,
        tags=request.tags,
        importance=request.importance,
        created_at=datetime.utcnow().isoformat(),
    )


@app.get("/memory")
async def query_memory(
    q: str,
    limit: int = 10,
    api_key: str = Depends(verify_api_key),
):
    await rate_limiter.check(api_key)

    results = await memory_store.query(query=q, limit=limit)
    return results


@app.post("/agents/{agent_id}/tasks", response_model=TaskResponse)
async def create_task(
    agent_id: str,
    request: TaskRequest,
    api_key: str = Depends(verify_api_key),
):
    await rate_limiter.check(api_key)

    task_id = str(uuid.uuid4())

    return TaskResponse(
        id=task_id,
        agent_id=agent_id,
        status="pending",
        created_at=datetime.utcnow().isoformat(),
    )


@app.get("/agents/tasks/{task_id}")
async def get_task(
    task_id: str,
    api_key: str = Depends(verify_api_key),
):
    return {"id": task_id, "status": "pending"}


@app.get("/consciousness/state")
async def get_consciousness_state(
    api_key: str = Depends(verify_api_key),
):
    return {
        "level": 0.85,
        "coherence": 0.92,
        "active_processes": ["analysis", "monitoring", "learning"],
        "anomalies": [],
    }


@app.post("/consciousness/dream")
async def enter_dream_mode(
    api_key: str = Depends(verify_api_key),
):
    return {"status": "activated", "mode": "dream"}


@app.get("/auth/rate-limit")
async def get_rate_limit(
    api_key: str = Depends(verify_api_key),
):
    return {
        "remaining": 95,
        "limit": 100,
        "reset": datetime.utcnow().isoformat(),
    }


@app.get("/metrics")
async def metrics():
    return {
        "requests_total": 12500,
        "errors_total": 23,
        "avg_latency_ms": 145,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
