## Configuration

- `HYPERSPELL_TOKEN` should be a valid user or app token (refer to the [Hyperspell docs](https://docs.hyperspell.com/) for how to obtain a user token).
- Some MCP clients don't support resources well (looking at you, Claude Desktop), so we can expose them as tools instead. Set `HYPERSPELL_USE_RESOURCES` to `false` (default) to expose everything as tools, `true` to expose retrieveing single documents or listing collections as resources instead, or `both` if you want it all.
- Optionally, set `HYPERSPELL_COLLECTION` to the name of the collection you want to query and add data to. If not set, it will use the user's default collection instead.


## Claude Desktop

Note that Claude needs the absolute path to `uv`, which can be found with `which uv` (it's usually `~/.local/bin/uv`). 

```json
{
  "mcpServers": {
    "Hyperspell": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--with",
        "hyperspell",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/path/to/hyperspell_mcp/server.py"
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

Create a `.env` file with the following contents:

```
HYPERSPELL_TOKEN=...
HYPERSPELL_USE_RESOURCES=true
```

Then run this to start the inspector:

```
uv run mcp dev hyperspell_mcp/server.py
```