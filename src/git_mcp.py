import os
from git import Repo, InvalidGitRepositoryError
from typing import Dict, Any, Optional, List

def _get_repo(repo_path: str) -> Repo:
    """
    Get a GitPython Repo object for the given path.
    Raises InvalidGitRepositoryError if the path is not a valid git repository.
    """
    return Repo(repo_path)

def git_status(repo_path: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute git status and return structured data.
    Args:
        repo_path: Path to the git repository.
        args: Optional arguments (not used for status, but kept for consistency).
    Returns:
        A dictionary with the status information.
    """
    repo = _get_repo(repo_path)
    # We can get the status in a structured way
    # Using repo.git.status(porcelain=True) for machine-readable format
    # But we want to return a dict, so we can parse or use repo.heads, etc.
    # Let's return a simple dict with branch, active branch, and changes.
    # For simplicity, we'll use the porcelain format and then parse?
    # Alternatively, we can return the raw string and let the caller parse?
    # The task says "restituiscono risultati strutturati JSON", so we should structure it.
    # We'll do:
    #   - branch: active branch name
    #   - staged: list of staged files (from index diff)
    #   - unstaged: list of unstaged files (from working tree diff)
    #   - untracked: list of untracked files
    try:
        active_branch = repo.active_branch.name
    except TypeError:
        # Detached HEAD
        active_branch = "HEAD detached at {}".format(repo.head.commit.hexsha[:7])

    # Get staged changes (index vs HEAD)
    staged = [item.a_path for item in repo.index.diff("HEAD")]
    # Get unstaged changes (working tree vs index)
    unstaged = [item.a_path for item in repo.index.diff(None)]
    # Get untracked files
    untracked = repo.untracked_files

    return {
        "branch": active_branch,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
    }

def git_diff(repo_path: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute git diff and return structured data.
    Args:
        repo_path: Path to the git repository.
        args: Optional arguments. Supported keys:
            - 'staged': if True, show staged changes (--staged)
            - 'file': path to a specific file to diff
    Returns:
        A dictionary with the diff information.
    """
    repo = _get_repo(repo_path)
    kwargs = {}
    if args:
        if args.get('staged'):
            kwargs['staged'] = True
        if args.get('file'):
            kwargs['paths'] = [args['file']]
    # We'll get the diff as a string and then maybe split by file?
    # But the task says structured JSON. We can return a list of files with their diffs.
    # However, for simplicity, we can return the diff as a string and let the client parse?
    # Let's return a dict with a 'diff' string and optionally a list of files if we can parse.
    # We'll use repo.git.diff(**kwargs) to get the diff string.
    diff_string = repo.git.diff(**kwargs)
    return {
        "diff": diff_string,
    }

def git_log(repo_path: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute git log and return structured data.
    Args:
        repo_path: Path to the git repository.
        args: Optional arguments. Supported keys:
            - 'n': number of commits to show (default 10)
            - 'since': show commits since a date (e.g., "2026-01-01")
            - 'author': filter by author
            - 'file': show commits that modified a specific file
    Returns:
        A dictionary with a list of commits, each commit having:
            - hash: commit hash
            - author: author name and email
            - date: commit date (ISO format)
            - message: commit message
    """
    repo = _get_repo(repo_path)
    kwargs = {}
    if args:
        if args.get('n'):
            kwargs['max_count'] = int(args['n'])
        if args.get('since'):
            kwargs['since'] = args['since']
        if args.get('author'):
            kwargs['author'] = args['author']
        if args.get('file'):
            kwargs['paths'] = [args['file']]
    # We'll iterate over the commits and build a list
    commits_list = []
    for commit in repo.iter_commits(**kwargs):
        commits_list.append({
            "hash": commit.hexsha,
            "author": f"{commit.author.name} <{commit.author.email}>",
            "date": commit.authored_datetime.isoformat(),
            "message": commit.message.strip(),
        })
    return {
        "log": commits_list,
    }