# MEOK AI Labs

Constitutional AI Governance Platform - Build safe, ethical AI applications.

## Quick Start

```bash
# Clone repository
git clone https://github.com/meok-ai/meokai.git
cd meokai

# Start infrastructure
docker-compose -f docker-compose.infra.yml up -d

# Run API
cd api && pip install -r requirements.txt
uvicorn server:app --reload
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MEOK AI Labs                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │Governance│  │ Memory  │  │ Agents │  │SOV3     │   │
│   │ Engine  │  │ System  │  │Orchestr│  │Conscious│   │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘   │
│        │              │              │            │         │
│   ┌────┴──────────────┴──────────────┴────────────┴────┐    │
│   │                   Redis Cache                     │    │
│   └─────────────────────────┬───────────────────────┘    │
│                             │                              │
│   ┌─────────────────────────┴───────────────────────┐    │
│   │              PostgreSQL + pgvector               │    │
│   └──────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Constitutional AI Governance** - Analyze content against ethical principles
- **Semantic Memory** - Vector-based memory storage and retrieval
- **Multi-Agent System** - Orchestrate multiple AI agents
- **SOV3 Consciousness** - Advanced consciousness simulation
- **Real-time Webhooks** - Event-driven architecture
- **GDPR Compliance** - Full audit logging and data management

## Services

| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | Main API server |
| Docs | 8001 | Interactive documentation |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Dashboards |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Caching |

## Development

```bash
# Install dependencies
make install

# Run development server
make dev

# Run tests
make test

# Run smoke tests
make test-smoke
```

## Testing

```bash
# Smoke tests (quick)
python scripts/smoke_test.py

# Stress tests
python scripts/stress_test.py --duration 30

# Pytest suite
pytest tests/

# E2E tests
cd tests/playwright && npx playwright test
```

## CLI Tools

```bash
# Dashboard
python scripts/dashboard.py

# Quickstart
python scripts/quickstart.py --demo

# Admin
python scripts/admin.py health
```

## Deployment

### Docker Compose (Development)

```bash
docker-compose -f docker-compose.infra.yml up -d
```

### Kubernetes (Production)

```bash
kubectl apply -f k8s/
./scripts/deploy.sh production
```

## Documentation

- [API Reference](api-reference.md)
- [SDK Documentation](docs/sdk.md)
- [Governance](docs/governance.md)
- [Deployment](docs/deployment.md)
- [Architecture](docs/architecture.md)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | PostgreSQL connection |
| `REDIS_URL` | redis://... | Redis connection |
| `JWT_SECRET` | change-me | JWT signing secret |
| `MEOK_API_KEY` | - | API authentication |
| `OPENAI_API_KEY` | - | OpenAI API key |

## License

MIT License - MEOK AI Labs
