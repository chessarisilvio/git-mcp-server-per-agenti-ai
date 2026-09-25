"""End-to-end test: spawns the real server subprocess and speaks MCP over stdio."""

import json
import sys

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_server_exposes_git_tools_over_stdio(git_repo):
    _repo, path = git_repo
    params = StdioServerParameters(command=sys.executable, args=["-m", "git_mcp_server.main"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {t.name for t in tools.tools}
            assert {"git_status", "git_diff", "git_log", "git_show"} <= tool_names

            result = await session.call_tool("git_status", {"repo_path": str(path)})
            assert result.isError is False
            payload = json.loads(result.content[0].text)
            assert payload["staged"] == []
            assert payload["unstaged"] == []

            log_result = await session.call_tool("git_log", {"repo_path": str(path), "n": 1})
            log_payload = json.loads(log_result.content[0].text)
            assert log_payload["log"][0]["message"] == "Initial commit"


async def test_server_reports_invalid_repo_as_tool_error(tmp_path):
    params = StdioServerParameters(command=sys.executable, args=["-m", "git_mcp_server.main"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("git_status", {"repo_path": str(tmp_path)})
            assert result.isError is True
