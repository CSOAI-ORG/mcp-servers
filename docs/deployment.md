# Deployment Guide

## Prerequisites

- Docker 20.10+
- Kubernetes 1.24+ (for production)
- PostgreSQL 15+ with pgvector
- Redis 7+
- 4GB RAM minimum

## Local Development

### Docker Compose

```bash
# Clone repository
git clone https://github.com/meok-ai/meokai.git
cd meokai

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Environment Variables

Create `.env`:

```bash
MEOK_API_KEY=your-api-key
MEOK_WEBHOOK_SECRET=your-webhook-secret
DATABASE_PASSWORD=secure-password
REDIS_PASSWORD=secure-redis-password
OPENAI_API_KEY=your-openai-key
```

## Production Deployment

### Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply secrets (update values first)
kubectl apply -f k8s/secrets.yaml

# Deploy
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/services.yaml

# Verify
kubectl get pods -n meokai
```

### Helm Chart (Alternative)

```bash
helm repo add meokai https://charts.meok.ai
helm install meokai meokai/meokai \
  --set apiKey=$MEOK_API_KEY \
  --set redis.password=$REDIS_PASSWORD
```

## Configuration

### API Server

| Variable | Default | Description |
|----------|---------|-------------|
| `API_VERSION` | 2.0.0 | API version |
| `LOG_LEVEL` | info | Logging level |
| `DATABASE_URL` | - | PostgreSQL connection |
| `REDIS_URL` | - | Redis connection |
| `CORS_ORIGINS` | * | Allowed origins |

### Resource Limits

| Component | CPU | Memory |
|-----------|-----|--------|
| API | 1000m | 1Gi |
| Webhooks | 500m | 512Mi |
| Workers | 2000m | 2Gi |

## Monitoring

### Prometheus Metrics

Available at `/metrics`:

- `meokai_requests_total` - Total requests
- `meokai_request_duration_seconds` - Latency histogram
- `meokai_violations_total` - Violations by type
- `meokai_active_agents` - Active agent count

### Grafana Dashboard

Import `docker/grafana-dashboards/meok-api.json`

### Health Checks

```bash
# Liveness
curl http://api.meok.ai/health

# Readiness
curl http://api.meok.ai/ready
```

## Scaling

### Horizontal Pod Autoscaler

```yaml
spec:
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Database Connection Pooling

Use PgBouncer for connection pooling:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: pgbouncer
        image: edoburu/pgbouncer
        env:
        - name: DATABASE_URL
          value: "postgres://meok:password@postgres:5432/meokai"
        - name: POOL_MODE
          value: "transaction"
        - name: MAX_CLIENT_CONN
          value: "1000"
        - name: DEFAULT_POOL_SIZE
          value: "25"
```

## Backup & Recovery

### Automated Backups

```bash
# Daily backup (add to crontab)
0 2 * * * /app/scripts/backup-manager.py --backup

# Verify backup
./scripts/backup-manager.py --verify

# Restore
./scripts/backup-manager.py --restore /backups/backup-2026-04-05.tar.gz
```

## Troubleshooting

### Pod Not Starting

```bash
kubectl describe pod <pod-name> -n meokai
kubectl logs <pod-name> -n meokai
```

### High Latency

1. Check database query times
2. Verify Redis connection
3. Review resource limits
4. Check for OOM kills

### Database Connection Errors

```bash
# Test connection
kubectl exec -it deploy/meokai-api -n meokai -- \
  python -c "import asyncpg; print('OK')"
```

## CI/CD

See `.github/workflows/deploy.yml` for automated deployment pipeline.
