# Git MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that exposes
read-only Git operations as tools, built with the official [`mcp`](https://pypi.org/project/mcp/)
Python SDK and [GitPython](https://github.com/gitpython-developers/GitPython).

The server speaks MCP over stdio: it is meant to be launched as a subprocess by an MCP
client (an AI agent, an IDE integration, `claude` Desktop, etc.), not called directly
over HTTP.

## What it does

It exposes four tools against a local Git repository:

| Tool | Description | Parameters |
|---|---|---|
| `git_status` | Working tree status: current branch, staged/unstaged/untracked files | `repo_path` (optional) |
| `git_diff` | Diff of working tree or staged changes, optionally scoped to one file | `repo_path`, `staged` (bool), `file` |
| `git_log` | Commit history, filterable by count, date, author, or file | `repo_path`, `n`, `since`, `author`, `file` |
| `git_show` | A commit's metadata + diff, or a file's content at a given ref | `repo_path`, `ref`, `file` |

`repo_path` is optional on every tool: if omitted, it falls back to the
`GIT_MCP_SERVER_REPO_PATH` environment variable, or `.` if that isn't set either.

All operations are read-only. There is no `git_commit`, `git_push`, `git_add`, etc.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verified in a clean virtual environment (Python 3.10–3.13) with no errors.

## Running the server

The server communicates over stdio using the MCP protocol — it does not print anything
useful if you just run it in a terminal and type at it. It is meant to be started by an
MCP client. For example, in a client configured via a JSON file (the format used by
Claude Desktop and similar tools):

```json
{
  "mcpServers": {
    "git": {
      "command": "git-mcp-server",
      "env": {
        "GIT_MCP_SERVER_REPO_PATH": "/path/to/your/repo"
      }
    }
  }
}
```

`GIT_MCP_SERVER_REPO_PATH` is just the default; any tool call can override it by passing
its own `repo_path` argument.

### Manually talking to it

You can drive the server with the official `mcp` client library to see the protocol
in action, without any external client:

```python
import asyncio, sys
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def main():
    params = StdioServerParameters(command=sys.executable, args=["-m", "git_mcp_server.main"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            result = await session.call_tool("git_status", {"repo_path": "."})
            print(result.content[0].text)

asyncio.run(main())
```

Running this against the repository itself prints the four tool names followed by a
JSON status payload (branch, staged/unstaged/untracked files).

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

11 tests, verified passing on Python 3.10, 3.11, 3.12 and 3.13:
- `tests/test_git_ops.py` exercises `git_status`/`git_diff`/`git_log`/`git_show`
  directly against a throwaway Git repository created per test.
- `tests/test_server.py` spawns the actual server subprocess and talks to it over
  stdio using the MCP client, checking tool discovery and a couple of real tool calls
  end to end.

CI (`.github/workflows/ci.yml`) runs the same suite on every push and pull request
across that same Python version matrix.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `GIT_MCP_SERVER_REPO_PATH` | Default repository path when a tool call doesn't specify `repo_path` | `.` |

## Limitations

- **Read-only.** No write operations (commit, push, add, branch, checkout, ...) are
  implemented.
- **No path sandboxing.** Any `repo_path` the caller passes is opened as-is — the
  server does not restrict which repositories on disk it will read. Don't expose it to
  untrusted callers without adding your own access control.
- **Stdio transport only.** The underlying SDK also supports SSE/streamable-HTTP
  transports, but this server only wires up stdio.
- **Pinned to `mcp<2`.** The `mcp` SDK's `2.x` line renamed `FastMCP` to `MCPServer`
  and changed parts of its API; this project targets the `1.x` `FastMCP` API and pins
  accordingly. Porting to `2.x` should be a small, mostly mechanical change.
- **Not published to PyPI.** Install from source as shown above.
- No authentication or rate limiting — the process trusts whatever MCP client launches
  it.

## License

MIT — see [LICENSE](LICENSE).
