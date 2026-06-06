# MEOK AI Labs Platform

Comprehensive documentation for the MEOK AI platform.

## Quick Links

- [API Reference](api-reference.md)
- [SDK Documentation](sdk/)
- [Deployment Guide](deployment/)
- [Architecture](architecture/)

## Getting Started

### 1. Install SDK

```bash
# Python
pip install meokai

# JavaScript
npm install @meokai/js
```

### 2. Initialize Client

```python
from meokai import MEOKClient

client = MEOKClient(api_key="your-api-key")
```

### 3. Start Building

```python
# Analyze content
result = client.governance.analyze("Your content here")

# Store memory
client.memory.store("Important information", tags=["work"])

# Create agent task
task = client.agents.create_task("researcher", "Find AI news")
```

## Core Services

| Service | Description |
|---------|-------------|
| [Governance](governance.md) | Constitutional AI analysis |
| [Memory](memory.md) | Semantic memory storage |
| [Agents](agents.md) | Task orchestration |
| [Consciousness](consciousness.md) | SOV3 consciousness engine |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      MEOK AI Labs                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │Governance│  │ Memory   │  │ Agents   │  │SOV3   │ │
│  │ Engine   │  │ System   │  │Orchestrator│  │Core  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬───┘ │
│       │              │              │            │      │
│  ┌────┴──────────────┴──────────────┴────────────┴──┐ │
│  │                  Redis Cache Layer                 │ │
│  └────────────────────────┬─────────────────────────┘ │
│                           │                            │
│  ┌────────────────────────┴─────────────────────────┐ │
│  │              PostgreSQL + pgvector                │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## SDK Examples

### Constitutional AI Analysis

```python
result = client.governance.analyze(
    content="Your content",
    framework="constitutional",
    content_type="text"
)

if result.get("violations"):
    print("Safety concerns found")
```

### Multi-Agent Workflow

```python
# Create task for research agent
task = client.agents.create_task(
    agent_id="researcher",
    instruction="Find latest AI regulations",
    priority="high"
)

# Monitor progress
status = client.agents.get_task(task["id"])
```

### Memory Query

```python
# Store important info
client.memory.store(
    content="User prefers email notifications",
    tags=["preference", "notifications"],
    importance=0.8
)

# Retrieve relevant memories
memories = client.memory.query("user notification preferences")
```

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

### Kubernetes (Production)

```bash
kubectl apply -f k8s/
./scripts/deploy.sh production
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/governance/analyze` | Analyze content |
| POST | `/memory` | Store memory |
| GET | `/memory?q=` | Query memories |
| POST | `/agents/{id}/tasks` | Create task |
| GET | `/consciousness/state` | Get consciousness |

## Support

- Documentation: https://docs.meok.ai
- API: https://api.meok.ai
- Email: support@meok.ai
