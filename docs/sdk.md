# MEOK AI Labs - SDK Documentation

## Python SDK

### Installation

```bash
pip install meokai
```

### Quick Start

```python
from meokai import MEOKClient

# Initialize
client = MEOKClient(api_key="your-api-key")

# Analyze content
result = client.governance.analyze(
    content="Your content",
    framework="constitutional"
)
```

### Governance Client

```python
# Analyze text
result = client.governance.analyze(
    content="Hello world",
    framework="constitutional",
    content_type="text"
)

# Check compliance
result = client.governance.check_compliance(
    content="Your content",
    standards=["constitutional", "eu-ai-act"]
)
```

### Memory Client

```python
# Store memory
result = client.memory.store(
    content="Important fact",
    memory_type="semantic",
    tags=["important"],
    importance=0.9
)

# Query memories
results = client.memory.query(
    query="what was stored",
    limit=10
)
```

### Agent Client

```python
# Create task
task = client.agents.create_task(
    agent_id="researcher",
    instruction="Find AI news",
    priority="high"
)

# Get status
status = client.agents.get_task(task["id"])
```

### Consciousness Client

```python
# Get state
state = client.consciousness.get_state()

# Enter dream mode
result = client.consciousness.enter_dream_mode()
```

---

## JavaScript SDK

### Installation

```bash
npm install @meokai/js
```

### Usage

```javascript
import { MEOKClient } from '@meokai/js';

const meok = new MEOKClient({ apiKey: 'your-api-key' });

// Analyze
const result = await meok.governance.analyze({
  content: 'Your content',
  framework: 'constitutional'
});

// Store memory
await meok.memory.store({
  content: 'Important info',
  tags: ['important']
});
```

---

## CLI Tool

```bash
# Install
pip install meokai[cli]

# Analyze content
meok analyze "Your content" --framework constitutional

# Store memory
meok memory store "Important fact" --tags important

# Query memories
meok memory query "what facts"

# Consciousness state
meok consciousness state
```

---

## Webhook Integration

```python
from meokai.webhooks.base import WebhookHandler, EventType

handler = WebhookHandler(
    webhook_secret="your-secret",
    handlers={
        EventType.GOVERNANCE_VIOLATION: handle_violation,
        EventType.AGENT_TASK_COMPLETED: handle_completed,
    }
)

# In FastAPI route
@app.post("/webhooks/meok")
async def webhook(request: Request):
    return await handler.handle(request)
```

---

## LangGraph Integration

```python
from meokai import MEOKClient
from langgraph.graph import StateGraph

meok = MEOKClient(api_key="...")

def safety_check(state):
    result = meok.governance.analyze(
        content=state["content"],
        framework="constitutional"
    )
    return {"safe": not result.get("violations")}
```

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | env MEOK_API_KEY | API authentication |
| `base_url` | https://meok.ai/api/v1 | API endpoint |
| `timeout` | 60 | Request timeout (seconds) |
| `max_retries` | 3 | Retry attempts |
