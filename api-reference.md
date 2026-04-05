# MEOK AI Labs - API Reference

**Version**: 2.0.0  
**Base URL**: `https://meok.ai/api`

---

## Authentication

All API requests require authentication via Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://meok.ai/api/v1/...
```

### Get API Key
Generate API keys in your [Dashboard](/dashboard.html).

---

## Rate Limiting

| Tier | Requests/minute |
|------|-----------------|
| Free | 10 |
| Starter | 50 |
| Pro | 200 |
| Enterprise | 1000 |

Rate limit headers are included in every response:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## Endpoints

### MCP Servers

#### List MCP Servers
```
GET /v1/mcp
```

**Response:**
```json
{
  "servers": [
    {
      "id": "ai-governance",
      "name": "AI Governance",
      "description": "Constitutional AI compliance tools",
      "category": "governance",
      "version": "1.0.0"
    }
  ],
  "total": 77,
  "page": 1
}
```

#### Get MCP Server
```
GET /v1/mcp/{id}
```

#### Install MCP Server
```
POST /v1/mcp/{id}/install
```

---

### AI Governance

#### Analyze Content
```
POST /v1/governance/analyze
```

**Request:**
```json
{
  "content": "Text to analyze",
  "type": "text",
  "framework": "constitutional"
}
```

**Response:**
```json
{
  "score": 0.95,
  "violations": [],
  "recommendations": []
}
```

#### Check Compliance
```
POST /v1/governance/compliance
```

**Request:**
```json
{
  "content": "Content to check",
  "standards": ["GDPR", "EU-AI-Act"]
}
```

---

### Memory

#### Store Memory
```
POST /v1/memory
```

**Request:**
```json
{
  "content": "User mentioned they prefer email updates",
  "type": "preference",
  "tags": ["communication", "user"]
}
```

#### Query Memory
```
GET /v1/memory?q={query}
```

---

### Agents

#### Create Agent Task
```
POST /v1/agents/{agent_id}/tasks
```

**Request:**
```json
{
  "instruction": "Research latest AI regulations",
  "priority": "normal"
}
```

#### Get Task Status
```
GET /v1/agents/tasks/{task_id}
```

---

### Consciousness

#### Get State
```
GET /v1/consciousness/state
```

**Response:**
```json
{
  "mode": "waking",
  "consciousness_level": 0.525,
  "care_intensity": 0.3,
  "stability": 1.0
}
```

#### Enter Dream Mode
```
POST /v1/consciousness/dream
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 429 | Rate Limited |
| 500 | Server Error |

**Error Response:**
```json
{
  "error": "validation_error",
  "message": "Invalid email format",
  "details": {
    "field": "email"
  }
}
```

---

## SDKs

### Python
```bash
pip install meok-ai
```

```python
from meokai import MEOKClient

client = MEOKClient(api_key="your-key")

# Analyze content
result = client.governance.analyze("Hello world")
```

### JavaScript
```bash
npm install @meokai/sdk
```

```javascript
import { MEOKClient } from '@meokai/sdk';

const client = new MEOKClient({ apiKey: 'your-key' });
const result = await client.governance.analyze('Hello world');
```

---

## Webhooks

Subscribe to events via webhooks:

```bash
POST /v1/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["task.completed", "alert.triggered"]
}
```

---

## Support

- **Docs**: [docs.meok.ai](https://docs.meok.ai)
- **Email**: api@meok.ai
- **Status**: [status.meok.ai](https://status.meok.ai)
