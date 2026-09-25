"""MCP server exposing read-only Git operations as tools over stdio."""

import os
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from git_mcp_server import git_ops

mcp = FastMCP("git-mcp-server")


def _resolve_repo_path(repo_path: Optional[str]) -> str:
    return repo_path or os.environ.get("GIT_MCP_SERVER_REPO_PATH", ".")


@mcp.tool()
def git_status(repo_path: Optional[str] = None) -> Dict[str, Any]:
    """Show the working tree status: current branch, staged, unstaged and untracked files."""
    return git_ops.git_status(_resolve_repo_path(repo_path))


@mcp.tool()
def git_diff(
    repo_path: Optional[str] = None,
    staged: bool = False,
    file: Optional[str] = None,
) -> Dict[str, Any]:
    """Show changes between commits, commit and working tree, etc. (like `git diff`)."""
    return git_ops.git_diff(_resolve_repo_path(repo_path), staged=staged, file=file)


@mcp.tool()
def git_log(
    repo_path: Optional[str] = None,
    n: int = 10,
    since: Optional[str] = None,
    author: Optional[str] = None,
    file: Optional[str] = None,
) -> Dict[str, Any]:
    """Show commit history, optionally filtered by count, date, author or file."""
    return git_ops.git_log(
        _resolve_repo_path(repo_path), n=n, since=since, author=author, file=file
    )


@mcp.tool()
def git_show(
    repo_path: Optional[str] = None,
    ref: str = "HEAD",
    file: Optional[str] = None,
) -> Dict[str, Any]:
    """Show a commit's metadata and diff, or a file's content at a given ref."""
    return git_ops.git_show(_resolve_repo_path(repo_path), ref=ref, file=file)
