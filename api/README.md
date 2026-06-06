# MEOK AI Labs API

Production-ready FastAPI server with all MEOK services.

## Quick Start

```bash
cd api
pip install -r requirements.txt
uvicorn server:app --reload
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| POST | `/governance/analyze` | Analyze content |
| POST | `/governance/compliance` | Check compliance |
| POST | `/memory` | Store memory |
| GET | `/memory?q=` | Query memories |
| POST | `/agents/{id}/tasks` | Create task |
| GET | `/agents/tasks/{id}` | Get task status |
| GET | `/consciousness/state` | Get consciousness |
| POST | `/consciousness/dream` | Enter dream mode |
| GET | `/auth/rate-limit` | Rate limit info |
| GET | `/metrics` | Prometheus metrics |

## Authentication

Include API key in header:

```
X-API-Key: your-api-key
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | PostgreSQL connection |
| `REDIS_URL` | redis://... | Redis connection |
| `JWT_SECRET` | change-me | JWT signing secret |
| `OPENAI_API_KEY` | - | OpenAI API key |

## Development

```bash
# Run with hot reload
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Run with Docker
docker build -t meokai/api api/
docker run -p 8000:8000 meokai/api
```

## Production

```bash
# Build
docker build -t meokai/api:latest api/

# Deploy
kubectl apply -f k8s/api-deployment.yaml
```
