import pytest

from git_mcp_server import git_ops


def test_status_clean_repo(git_repo):
    _repo, path = git_repo
    result = git_ops.git_status(str(path))
    assert result["branch"] in ("main", "master")
    assert result["staged"] == []
    assert result["unstaged"] == []
    assert result["untracked"] == []


def test_status_reports_unstaged_and_untracked(git_repo):
    repo, path = git_repo
    (path / "file1.txt").write_text("modified\n")
    (path / "new.txt").write_text("new\n")

    result = git_ops.git_status(str(path))
    assert result["unstaged"] == ["file1.txt"]
    assert result["untracked"] == ["new.txt"]

    repo.index.add(["new.txt"])
    result = git_ops.git_status(str(path))
    assert result["staged"] == ["new.txt"]


def test_diff_shows_working_tree_changes(git_repo):
    _repo, path = git_repo
    (path / "file1.txt").write_text("modified\n")

    result = git_ops.git_diff(str(path))
    assert "diff --git" in result["diff"]
    assert "modified" in result["diff"]


def test_diff_staged_only_shows_index_changes(git_repo):
    repo, path = git_repo
    (path / "file1.txt").write_text("modified\n")
    repo.index.add(["file1.txt"])

    result = git_ops.git_diff(str(path), staged=True)
    assert "diff --git" in result["diff"]

    unstaged_result = git_ops.git_diff(str(path))
    assert unstaged_result["diff"] == ""


def test_log_returns_commit_metadata(git_repo):
    _repo, path = git_repo
    result = git_ops.git_log(str(path))
    assert len(result["log"]) == 1
    commit = result["log"][0]
    assert commit["message"] == "Initial commit"
    assert len(commit["hash"]) == 40
    assert "Test User" in commit["author"]


def test_log_respects_n(git_repo):
    repo, path = git_repo
    (path / "file2.txt").write_text("more\n")
    repo.index.add(["file2.txt"])
    repo.index.commit("Second commit")

    result = git_ops.git_log(str(path), n=1)
    assert len(result["log"]) == 1
    assert result["log"][0]["message"] == "Second commit"


def test_show_commit_metadata(git_repo):
    _repo, path = git_repo
    result = git_ops.git_show(str(path), ref="HEAD")
    assert result["message"] == "Initial commit"
    assert "file1.txt" in result["show"]


def test_show_file_content_at_ref(git_repo):
    # GitPython strips trailing whitespace from `git show` output.
    _repo, path = git_repo
    result = git_ops.git_show(str(path), ref="HEAD", file="file1.txt")
    assert result["content"] == "hello"


def test_invalid_repository_raises(tmp_path):
    with pytest.raises(git_ops.InvalidGitRepositoryError):
        git_ops.git_status(str(tmp_path))
