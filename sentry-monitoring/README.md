# @csgaglobal/sentry-monitoring

Sentry error monitoring integration for issue tracking, performance monitoring, and release management.

**Category:** Monitoring & Observability | **Version:** 1.0.0 | **License:** MIT

## Overview

Part of the [MEOK AI Labs MCP Server Platform](https://meok-global.org/) — a comprehensive suite of 70+ Model Context Protocol servers for AI governance, cybersecurity, and enterprise tooling.

## Features

- Error tracking & alerting
- Performance monitoring
- Release tracking
- Issue assignment & resolution

## Installation

```bash
npm install @csgaglobal/sentry-monitoring
```

## Quick Start

```typescript
import { createServer } from "@csgaglobal/sentry-monitoring";

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
