import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys

# Add the src directory to the path so we can import git_mcp
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from git_mcp import git_status, git_diff, git_log, InvalidGitRepositoryError

app = FastAPI(title="Git MCP Server", description="MCP server for Git operations")

# Configuration from environment variables
REPO_PATH = os.environ.get("GIT_MCP_SERVER_REPO_PATH", ".")

class GitCommandRequest(BaseModel):
    command: str
    args: Optional[Dict[str, Any]] = None

class GitCommandResponse(BaseModel):
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/git/command", response_model=GitCommandResponse)
async def execute_git_command(request: GitCommandRequest):
    """
    Execute a Git command and return structured JSON response.
    Uses GitPython to perform actual Git operations.
    """
    try:
        if request.command == "status":
            output = git_status(REPO_PATH, request.args)
        elif request.command == "diff":
            output = git_diff(REPO_PATH, request.args)
        elif request.command == "log":
            output = git_log(REPO_PATH, request.args)
        else:
            # For any other command, return an error
            return GitCommandResponse(
                success=False,
                output=None,
                error=f"Unsupported command: {request.command}"
            )

        return GitCommandResponse(
            success=True,
            output=output,
            error=None
        )
    except InvalidGitRepositoryError:
        return GitCommandResponse(
            success=False,
            output=None,
            error=f"Not a git repository: {REPO_PATH}"
        )
    except Exception as e:
        return GitCommandResponse(
            success=False,
            output=None,
            error=str(e)
        )

def main():
    """Run the FastAPI server with Uvicorn."""
    import uvicorn
    host = os.environ.get("GIT_MCP_SERVER_HOST", "localhost")
    port = int(os.environ.get("GIT_MCP_SERVER_PORT", 8080))
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()