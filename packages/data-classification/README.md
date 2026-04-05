# Data Classification MCP Server

> Part of the [MEOK AI Labs MCP Platform](https://meok-global.vercel.app/) — Cyber Security Global Alliance

Automated data classification and labeling with sensitivity detection, PII scanning, and data governance tagging.

## Installation

```bash
npx @smithery/cli install @csgaglobal/data-classification
```

## Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "data-classification": {
      "command": "npx",
      "args": ["-y", "@csgaglobal/data-classification"]
    }
  }
}
```

## Features

- AI governance compliance assessment
- Real-time policy validation
- CSOAI standards alignment
- Automated reporting

## License

CC0-1.0 — See [LICENSE](./LICENSE)

## Links

- [Product Page](https://meok-global.vercel.app/mcp/data-classification.html)
- [MEOK AI Labs Platform](https://meok-global.vercel.app/)
- [GitHub Repository](https://github.com/meok-global/mcp-servers)
