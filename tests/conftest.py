import pytest
from git import Repo


@pytest.fixture
def git_repo(tmp_path):
    """A real, throwaway git repository with one commit."""
    repo = Repo.init(tmp_path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test User")
        cw.set_value("user", "email", "test@example.com")

    (tmp_path / "file1.txt").write_text("hello\n")
    repo.index.add(["file1.txt"])
    repo.index.commit("Initial commit")

    return repo, tmp_path
