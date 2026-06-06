# MEOK AI Labs Python SDK

Official Python SDK for MEOK AI Labs - Constitutional AI Governance Platform

## Installation

```bash
pip install meokai
```

Or with CLI dependencies:

```bash
pip install meokai[cli]
```

## Quick Start

```python
from meokai import MEOKClient

# Initialize client
client = MEOKClient(api_key="your-api-key")

# Analyze content with Constitutional AI
result = client.governance.analyze("Your content here")

# Store a memory
client.memory.store("User prefers dark mode", tags=["preference", "ui"])

# Query memories
memories = client.memory.query("user preferences")

# Create agent task
task = client.agents.create_task("researcher", "Find latest AI news")
```

## CLI Usage

```bash
# Set API key
export MEOK_API_KEY=your-api-key

# Analyze content
meok analyze "Your content" --framework constitutional

# Store memory
meok memory store "Important fact" --tags important work

# Query memories
meok memory query "what are user preferences"

# Get consciousness state
meok consciousness state
```

## Features

- **Constitutional AI Governance** - Analyze content against governance frameworks
- **Memory Management** - Store and query semantic memories
- **Agent Orchestration** - Create and manage agent tasks
- **Consciousness State** - Access consciousness engine state

## Documentation

Full documentation at https://docs.meok.ai

## License

MIT License - MEOK AI Labs
