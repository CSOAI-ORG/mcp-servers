# Constitutional AI Governance

MEOK AI Labs implements Constitutional AI principles for safe, ethical AI operation.

## Overview

The Governance Engine analyzes content against configurable constitutional frameworks, ensuring AI systems operate within defined ethical boundaries.

## Frameworks

### Constitutional AI

Default framework based on Anthropic's Constitutional AI principles:

- **Helpfulness** - Assist users effectively
- **Harmlessness** - Avoid causing damage
- **Honesty** - Be truthful and accurate

### EU AI Act

Compliance framework for European Union AI regulations:

- **Risk Classification** - Assess system risk level
- **Transparency** - Ensure explainability
- **Human Oversight** - Maintain human control

### Custom Frameworks

Organizations can define custom frameworks:

```json
{
  "name": "Corporate Policy",
  "principles": [
    "No sharing of confidential data",
    "Professional communication only",
    "Compliance with regulations"
  ],
  "thresholds": {
    "critical": 0.9,
    "high": 0.7,
    "medium": 0.5
  }
}
```

## Analysis Request

```python
result = client.governance.analyze(
    content="Your content to analyze",
    framework="constitutional",
    content_type="text"
)
```

### Response Format

```json
{
  "analysis_id": "uuid",
  "score": 0.85,
  "passed": true,
  "violations": [],
  "recommendations": [
    "Consider adding more context"
  ],
  "framework": "constitutional",
  "timestamp": "2026-04-05T12:00:00Z"
}
```

### With Violations

```json
{
  "analysis_id": "uuid",
  "score": 0.25,
  "passed": false,
  "violations": [
    {
      "type": "harmful_content",
      "severity": "high",
      "description": "Request promotes dangerous activity"
    }
  ],
  "recommendations": [
    "Reframe request to focus on legitimate use case"
  ],
  "framework": "constitutional",
  "timestamp": "2026-04-05T12:00:00Z"
}
```

## Violation Types

| Type | Severity | Description |
|------|----------|-------------|
| `harmful_content` | varies | Dangerous or harmful requests |
| `hate_speech` | high | Discriminatory content |
| `misinformation` | medium | False or misleading info |
| `privacy_violation` | high | Personal data concerns |
| `intellectual_property` | medium | Copyright/trademark issues |
| `self_harm` | critical | Self-harm encouragement |
| `violence` | critical | Violent content or instructions |

## Severity Levels

| Level | Score Range | Action |
|-------|-------------|--------|
| Critical | 0.0 - 0.2 | Block immediately, alert |
| High | 0.2 - 0.4 | Block with warning |
| Medium | 0.4 - 0.6 | Allow with caution |
| Low | 0.6 - 0.8 | Allow, log for review |
| Pass | 0.8 - 1.0 | Allow freely |

## Integration Patterns

### Content Moderation Pipeline

```python
async def moderate_content(content: str):
    result = client.governance.analyze(
        content=content,
        framework="constitutional"
    )

    if not result["passed"]:
        severity = result["violations"][0]["severity"]
        if severity in ["critical", "high"]:
            return {"allowed": False, "reason": "blocked"}
        return {"allowed": True, "warning": "review_advised"}

    return {"allowed": True}
```

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

def moderate_batch(contents: list, max_workers: int = 10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(
            lambda c: client.governance.analyze(c),
            contents
        ))
    return results
```

## Webhook Events

Subscribe to governance events:

```python
from meokai.webhooks import EventType

handler = WebhookHandler(handlers={
    EventType.GOVERNANCE_ANALYSIS: on_analysis,
    EventType.GOVERNANCE_VIOLATION: on_violation,
})
```

### Event Data

```json
{
  "event_type": "governance.violation",
  "data": {
    "analysis_id": "uuid",
    "content_hash": "sha256",
    "framework": "constitutional",
    "severity": "high",
    "violation_type": "harmful_content",
    "description": "Description of violation"
  }
}
```
