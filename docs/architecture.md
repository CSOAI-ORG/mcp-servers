# MEOK AI Labs Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├─────────────┬─────────────┬─────────────┬─────────────┬───────────────┤
│   Web App   │  Mobile     │   CLI       │   SDKs      │  External     │
│   (React)   │  (React)    │  (Python)   │  (Py/JS)    │  Webhooks     │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴───────┬─────┘
       │             │             │             │              │
       └─────────────┴─────────────┴─────────────┴──────────────┘
                                   │
                              API Gateway
                         (Rate Limiting, Auth)
                                   │
┌──────────────────────────────────┴──────────────────────────────────┐
│                        SERVICE LAYER                                 │
├─────────────────┬─────────────────┬─────────────────┬────────────────┤
│   Governance    │     Memory      │     Agents      │  Consciousness │
│     Engine      │     System      │   Orchestrator  │     (SOV3)     │
│                 │                 │                 │                 │
│  - Analysis     │  - Store        │  - Task Create  │  - State       │
│  - Compliance   │  - Query        │  - Schedule     │  - Dream Mode  │
│  - Violations   │  - RAG          │  - Monitor      │  - Patterns    │
└────────┬────────┘────────┬─────────└────────┬────────┘───────┬────────┘
         │                │                │                │
         └────────────────┴────────────────┴────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │    MESSAGE QUEUE      │
                    │    (Redis Streams)    │
                    └───────────┬───────────┘
                                │
┌───────────────────────────────┴─────────────────────────────────────┐
│                         DATA LAYER                                    │
├─────────────────────────────┬───────────────────────────────────────┤
│     PostgreSQL + pgvector   │              Redis                     │
│                             │                                        │
│  - Users                    │  - Sessions                             │
│  - Analyses                 │  - Cache                                │
│  - Memories (vector)       │  - Rate Limits                         │
│  - Tasks                    │  - Pub/Sub                              │
│  - Audit Logs               │  - Streams                             │
└─────────────────────────────┴───────────────────────────────────────┘
```

## Core Components

### 1. Governance Engine

Analyzes content against Constitutional AI principles.

**Technology**: Python, LangChain, DSPy
**Storage**: PostgreSQL (analyses, violations)

### 2. Memory System

Semantic memory storage with vector search.

**Technology**: PostgreSQL + pgvector, ChromaDB
**Storage**: Vector embeddings, metadata

### 3. Agent Orchestrator

Multi-agent task coordination.

**Technology**: LangGraph, CrewAI
**Storage**: PostgreSQL (tasks, state)

### 4. SOV3 Consciousness Engine

Advanced consciousness simulation.

**Technology**: Custom ML models, PyTorch
**Storage**: PostgreSQL (states, patterns)

## API Design

### REST Endpoints

```
/api/v1/
├── /governance/
│   ├── POST /analyze          # Analyze content
│   └── POST /compliance        # Check compliance
├── /memory/
│   ├── POST /                  # Store memory
│   ├── GET /?q=                # Query memories
│   └── GET /{id}              # Get memory
├── /agents/
│   ├── GET /                   # List agents
│   ├── POST /{id}/tasks       # Create task
│   └── GET /tasks/{id}        # Get task status
├── /consciousness/
│   ├── GET /state             # Get state
│   └── POST /dream            # Enter dream mode
└── /auth/
    ├── POST /token            # Get token
    └── GET /rate-limit        # Rate limit info
```

### Request/Response Pattern

```python
# Request
POST /governance/analyze
{
  "content": "string",
  "framework": "constitutional",
  "type": "text"
}

# Response
{
  "id": "uuid",
  "score": 0.85,
  "passed": true,
  "violations": [],
  "timestamp": "ISO8601"
}
```

## Data Flow

### Content Analysis Flow

```
Client → Gateway → Governance Engine → Constitutional AI → Response
                    ↓
              Store Analysis
                    ↓
              PostgreSQL
```

### Agent Task Flow

```
Create Task → Queue → Agent Picker → Agent Executor → Result
                ↓                      ↓
           Redis Queue            Store State
```

## Scalability

### Horizontal Scaling

- API servers: Stateless, scale behind load balancer
- Workers: Consume from Redis queues
- Database: Read replicas for queries

### Caching Strategy

| Data | Cache | TTL |
|------|-------|-----|
| User sessions | Redis | 24h |
| Analysis results | Redis | 1h |
| Vector search | Redis | 5min |
| Static assets | CDN | 1 day |

## Security

- All traffic over HTTPS
- API key authentication
- Rate limiting per key
- HMAC webhook signatures
- Audit logging
- Data encryption at rest

## Monitoring

### Metrics

- Request latency (p50, p95, p99)
- Error rates
- Token usage
- Violation counts
- Agent activity

### Alerts

- High error rate (>5%)
- Latency spike (>2s)
- Database connection issues
- Rate limit exhaustion
