# @csgaglobal/context7-docs

Context-aware documentation search and retrieval with semantic understanding and cross-reference capabilities.

**Category:** Documentation & Knowledge | **Version:** 1.0.0 | **License:** MIT

## Overview

Part of the [MEOK AI Labs MCP Server Platform](https://meok-global.org/) — a comprehensive suite of 70+ Model Context Protocol servers for AI governance, cybersecurity, and enterprise tooling.

## Features

- Semantic documentation search
- Cross-reference resolution
- Context-aware retrieval
- Multi-format document support

## Installation

```bash
npm install @csgaglobal/context7-docs
```

## Quick Start

```typescript
import { createServer } from "@csgaglobal/context7-docs";

const server = createServer({
  // Configuration options
});

server.start();
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `port` | `number` | `3000` | Server port |
| `logLevel` | `string` | `"info"` | Logging verbosity |

## MCP Protocol

This server implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification, enabling seamless integration with AI assistants and automation tools.

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test
```

## Related Packages

Explore the full suite at [meok-global.org/mcp](https://meok-global.org/mcp/)

## License

MIT © [MEOK AI Labs](https://meok-global.org/)
