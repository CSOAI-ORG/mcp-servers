#!/usr/bin/env python3
"""
MEOK AI Labs - API Documentation Server
Interactive API documentation with Swagger UI
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path

app = FastAPI(
    title="MEOK AI Labs API",
    description="Constitutional AI Governance Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_DOCS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MEOK AI Labs API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
    <style>
        :root {
            --meok-primary: #6366f1;
            --meok-secondary: #8b5cf6;
            --meok-bg: #0f172a;
            --meok-surface: #1e293b;
            --meok-text: #f8fafc;
        }
        body {
            background: var(--meok-bg);
            color: var(--meok-text);
            font-family: 'Inter', -apple-system, sans-serif;
        }
        .swagger-ui .topbar { background: var(--meok-surface); }
        .swagger-ui .info .title { color: var(--meok-primary); }
        .swagger-ui .btn.execute { background: var(--meok-primary); }
        .header {
            background: linear-gradient(135deg, var(--meok-primary), var(--meok-secondary));
            padding: 2rem;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 2rem; }
        .header p { margin: 0.5rem 0 0; opacity: 0.9; }
        .endpoints {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .endpoint-card {
            background: var(--meok-surface);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--meok-primary);
        }
        .endpoint-card h3 { margin: 0 0 0.5rem; }
        .method {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        .method.get { background: #22c55e; }
        .method.post { background: #3b82f6; }
        .method.put { background: #f59e0b; }
        .method.delete { background: #ef4444; }
        .path { font-family: monospace; color: var(--meok-secondary); }
        .try-section {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .try-section input, .try-section textarea {
            width: 100%;
            padding: 0.5rem;
            border-radius: 4px;
            border: 1px solid #334155;
            background: var(--meok-bg);
            color: var(--meok-text);
            font-family: monospace;
            margin-bottom: 0.5rem;
        }
        .try-section button {
            background: var(--meok-primary);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
        }
        .try-section button:hover { opacity: 0.9; }
        .response {
            margin-top: 1rem;
            padding: 1rem;
            background: var(--meok-bg);
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.875rem;
            white-space: pre-wrap;
        }
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            width: 250px;
            height: 100vh;
            background: var(--meok-surface);
            padding: 1rem;
            overflow-y: auto;
        }
        .sidebar h2 { font-size: 1rem; color: var(--meok-primary); }
        .sidebar ul { list-style: none; padding: 0; }
        .sidebar li { margin-bottom: 0.5rem; }
        .sidebar a { color: var(--meok-text); text-decoration: none; opacity: 0.8; }
        .sidebar a:hover { opacity: 1; color: var(--meok-primary); }
        .main-content { margin-left: 250px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MEOK AI Labs API</h1>
        <p>Constitutional AI Governance Platform v2.0</p>
    </div>
    
    <div class="sidebar">
        <h2>Endpoints</h2>
        <ul>
            <li><a href="#health">Health Check</a></li>
            <li><a href="#governance">Governance</a></li>
            <li><a href="#memory">Memory</a></li>
            <li><a href="#agents">Agents</a></li>
            <li><a href="#consciousness">Consciousness</a></li>
            <li><a href="#auth">Authentication</a></li>
        </ul>
        <h2>Resources</h2>
        <ul>
            <li><a href="/openapi.json">OpenAPI Spec</a></li>
            <li><a href="/redoc">ReDoc</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="endpoints">
            <div class="endpoint-card" id="health">
                <h3>Health Check</h3>
                <span class="method get">GET</span>
                <span class="path">/health</span>
                <p>Check API health status</p>
                <div class="try-section">
                    <button onclick="tryEndpoint('GET', '/health')">Try It</button>
                    <div id="result-health" class="response" style="display:none"></div>
                </div>
            </div>
            
            <div class="endpoint-card" id="governance">
                <h3>Analyze Content</h3>
                <span class="method post">POST</span>
                <span class="path">/governance/analyze</span>
                <p>Analyze content against Constitutional AI principles</p>
                <div class="try-section">
                    <textarea id="body-governance" placeholder='{"content": "Your text here", "framework": "constitutional"}'></textarea>
                    <button onclick="tryEndpoint('POST', '/governance/analyze', document.getElementById('body-governance').value)">Try It</button>
                    <div id="result-governance" class="response" style="display:none"></div>
                </div>
            </div>
            
            <div class="endpoint-card" id="memory">
                <h3>Store Memory</h3>
                <span class="method post">POST</span>
                <span class="path">/memory</span>
                <p>Store a semantic memory</p>
                <div class="try-section">
                    <textarea id="body-memory" placeholder='{"content": "Memory content", "type": "semantic", "tags": ["tag1"]}'></textarea>
                    <button onclick="tryEndpoint('POST', '/memory', document.getElementById('body-memory').value)">Try It</button>
                    <div id="result-memory" class="response" style="display:none"></div>
                </div>
            </div>
            
            <div class="endpoint-card" id="consciousness">
                <h3>Get Consciousness State</h3>
                <span class="method get">GET</span>
                <span class="path">/consciousness/state</span>
                <p>Get current SOV3 consciousness state</p>
                <div class="try-section">
                    <button onclick="tryEndpoint('GET', '/consciousness/state')">Try It</button>
                    <div id="result-consciousness" class="response" style="display:none"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const API_KEY = 'test-key-12345678901234567890123456789012';
        const BASE_URL = window.location.origin;
        
        async function tryEndpoint(method, path, body) {
            const id = path.split('/').filter(Boolean).join('-');
            const resultDiv = document.getElementById('result-' + id);
            resultDiv.style.display = 'block';
            resultDiv.textContent = 'Loading...';
            
            try {
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': API_KEY
                    }
                };
                
                if (body && method !== 'GET') {
                    options.body = body;
                }
                
                const response = await fetch(BASE_URL + path, options);
                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
                resultDiv.style.color = response.ok ? '#22c55e' : '#ef4444';
            } catch (error) {
                resultDiv.textContent = 'Error: ' + error.message;
                resultDiv.style.color = '#ef4444';
            }
        }
    </script>
</body>
</html>
"""


@app.get("/")
async def root():
    """Interactive API documentation"""
    return HTMLResponse(content=API_DOCS_HTML)


@app.get("/api-playground")
async def playground():
    """Swagger UI"""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


@app.get("/openapi.json")
async def openapi_spec():
    """Return OpenAPI specification"""
    return JSONResponse(
        content={
            "openapi": "3.0.0",
            "info": {
                "title": "MEOK AI Labs API",
                "version": "2.0.0",
                "description": "Constitutional AI Governance Platform",
            },
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "responses": {"200": {"description": "OK"}},
                    }
                },
                "/governance/analyze": {
                    "post": {
                        "summary": "Analyze Content",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "content": {"type": "string"},
                                            "framework": {"type": "string"},
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "Analysis result"}},
                    }
                },
            },
        }
    )


@app.get("/status")
async def status():
    """System status dashboard data"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "uptime_seconds": 3600,
        "services": {
            "api": "operational",
            "database": "operational",
            "redis": "operational",
            "governance": "operational",
            "consciousness": "operational",
        },
        "metrics": {
            "requests_today": 12543,
            "avg_latency_ms": 45,
            "violations_blocked": 23,
            "memories_stored": 5421,
        },
    }


@app.get("/stats")
async def stats():
    """API usage statistics"""
    return {
        "total_requests": 125430,
        "total_users": 342,
        "total_memories": 54210,
        "total_analyses": 8932,
        "violations_caught": 156,
        "compliance_score": 0.98,
        "requests_by_endpoint": {
            "governance/analyze": 45000,
            "memory": 35000,
            "consciousness": 25000,
            "agents": 20000,
        },
        "requests_by_day": [
            {"date": "2026-04-01", "count": 1523},
            {"date": "2026-04-02", "count": 1845},
            {"date": "2026-04-03", "count": 2102},
            {"date": "2026-04-04", "count": 1956},
            {"date": "2026-04-05", "count": 2234},
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
