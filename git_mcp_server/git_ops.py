"""Git operations backed by GitPython, returning JSON-serializable dicts."""

from typing import Any, Dict, List, Optional

from git import InvalidGitRepositoryError, Repo

__all__ = [
    "InvalidGitRepositoryError",
    "git_status",
    "git_diff",
    "git_log",
    "git_show",
]


def _get_repo(repo_path: str) -> Repo:
    return Repo(repo_path)


def git_status(repo_path: str) -> Dict[str, Any]:
    repo = _get_repo(repo_path)
    try:
        active_branch = repo.active_branch.name
    except TypeError:
        active_branch = f"HEAD detached at {repo.head.commit.hexsha[:7]}"

    staged = [item.a_path for item in repo.index.diff("HEAD")]
    unstaged = [item.a_path for item in repo.index.diff(None)]
    untracked = repo.untracked_files

    return {
        "branch": active_branch,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
    }


def git_diff(
    repo_path: str,
    staged: bool = False,
    file: Optional[str] = None,
) -> Dict[str, Any]:
    repo = _get_repo(repo_path)
    kwargs: Dict[str, Any] = {}
    if staged:
        kwargs["staged"] = True
    if file:
        kwargs["paths"] = [file]
    return {"diff": repo.git.diff(**kwargs)}


def git_log(
    repo_path: str,
    n: int = 10,
    since: Optional[str] = None,
    author: Optional[str] = None,
    file: Optional[str] = None,
) -> Dict[str, Any]:
    repo = _get_repo(repo_path)
    kwargs: Dict[str, Any] = {"max_count": n}
    if since:
        kwargs["since"] = since
    if author:
        kwargs["author"] = author
    if file:
        kwargs["paths"] = [file]

    commits: List[Dict[str, Any]] = []
    for commit in repo.iter_commits(**kwargs):
        commits.append(
            {
                "hash": commit.hexsha,
                "author": f"{commit.author.name} <{commit.author.email}>",
                "date": commit.authored_datetime.isoformat(),
                "message": commit.message.strip(),
            }
        )
    return {"log": commits}


def git_show(
    repo_path: str,
    ref: str = "HEAD",
    file: Optional[str] = None,
) -> Dict[str, Any]:
    repo = _get_repo(repo_path)
    if file:
        content = repo.git.show(f"{ref}:{file}")
        return {"ref": ref, "file": file, "content": content}

    commit = repo.commit(ref)
    return {
        "ref": ref,
        "hash": commit.hexsha,
        "author": f"{commit.author.name} <{commit.author.email}>",
        "date": commit.authored_datetime.isoformat(),
        "message": commit.message.strip(),
        "show": repo.git.show(ref),
    }
