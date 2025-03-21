

## Claude Desktop

```json
{
  "mcpServers": {
    "Hyperspell": {
      "command": "/Users/manu/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "hyperspell",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/Users/manu/hyperspell/mcp/hyperspell-mcp/server.py"
      ],
      "env": {
        "HYPERSPELL_TOKEN": "<app or user token>",
        "USE_RESOURCES": "false"
      }
    }
  }
}
```

## Using the inspector

```
USE_RESOURCES=true HYPERSPELL_TOKEN="..." uv run mcp dev hyperspell-mcp/server.py
```