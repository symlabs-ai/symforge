"""
TDD Unit Tests for Git integration in SessionRepository.

Tests cover:
- Auto-commit on session state transitions
- Commit message format
- Git repository initialization
- Skip commit when not in git repo
"""

import subprocess
from pathlib import Path

from symforge.domain.process_definition import ProcessDefinition
from symforge.infrastructure.session_repository import SessionRepository


def init_git_repo(path: Path) -> None:
    """Initialize a git repository for testing."""
    subprocess.run(
        ["git", "init"],
        cwd=path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=path,
        capture_output=True,
        check=True,
    )


def get_last_commit_message(path: Path) -> str:
    """Get the last commit message."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_commit_count(path: Path) -> int:
    """Get the number of commits."""
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0
    return int(result.stdout.strip())


class TestGitAutoCommit:
    """Tests for auto-commit functionality."""

    def test_create_session_commits_when_in_git_repo(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)
        process = ProcessDefinition(name="test")

        repo.create(process)

        # Should have at least one commit
        commit_count = get_commit_count(tmp_path)
        assert commit_count >= 1

    def test_create_session_commit_message_format(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)
        process = ProcessDefinition(name="my_process")

        repo.create(process)

        msg = get_last_commit_message(tmp_path)
        assert "symforge" in msg.lower() or "session" in msg.lower()

    def test_update_session_commits_state_change(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        initial_count = get_commit_count(tmp_path)

        session.mark_awaiting_input(["missing.md"])
        repo.update(session)

        new_count = get_commit_count(tmp_path)
        assert new_count > initial_count

    def test_no_commit_when_auto_commit_disabled(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=False)
        process = ProcessDefinition(name="test")

        repo.create(process)

        # Should have no commits (or just initial if any)
        commit_count = get_commit_count(tmp_path)
        assert commit_count == 0

    def test_no_error_when_not_in_git_repo(self, tmp_path: Path):
        # Don't init git repo
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)
        process = ProcessDefinition(name="test")

        # Should not raise error
        session = repo.create(process)

        assert session is not None
        assert session.id is not None

    def test_commit_includes_session_file(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)
        process = ProcessDefinition(name="test")

        session = repo.create(process)

        # Check that the session file is tracked
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", f".symforge/sessions/{session.id}.yml"],
            cwd=tmp_path,
            capture_output=True,
        )
        assert result.returncode == 0


class TestGitCommitMessages:
    """Tests for commit message content."""

    def test_commit_message_includes_session_id(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)
        process = ProcessDefinition(name="test")

        session = repo.create(process)

        msg = get_last_commit_message(tmp_path)
        assert session.id in msg

    def test_commit_message_includes_state_on_update(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        session.mark_awaiting_input(["file.md"])
        repo.update(session)

        msg = get_last_commit_message(tmp_path)
        assert "AWAITING_INPUT" in msg or "awaiting" in msg.lower()


class TestGitEdgeCases:
    """Edge cases for git integration."""

    def test_multiple_sessions_multiple_commits(self, tmp_path: Path):
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir, auto_commit=True)

        process1 = ProcessDefinition(name="process1")
        process2 = ProcessDefinition(name="process2")

        repo.create(process1)
        count_after_1 = get_commit_count(tmp_path)

        repo.create(process2)
        count_after_2 = get_commit_count(tmp_path)

        assert count_after_2 > count_after_1

    def test_default_auto_commit_is_false(self, tmp_path: Path):
        """Default behavior should not auto-commit for backwards compatibility."""
        init_git_repo(tmp_path)
        sessions_dir = tmp_path / ".symforge" / "sessions"
        repo = SessionRepository(sessions_dir)  # No auto_commit param
        process = ProcessDefinition(name="test")

        repo.create(process)

        commit_count = get_commit_count(tmp_path)
        assert commit_count == 0
