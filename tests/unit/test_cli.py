"""
TDD Unit Tests for CLI.

Tests cover:
- start command
- resume command
- reset command
- decide command (HIL)
- status command
- init command
- validate command
"""

import json
import pytest
from pathlib import Path

from symforge.cli import main


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create a workspace directory."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


class TestCLIStart:
    """Tests for start command."""

    def test_start_creates_session(self, workspace: Path, capsys):
        result = main([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])

        assert result == 0
        captured = capsys.readouterr()
        session_id = captured.out.strip()
        assert len(session_id) == 8

    def test_start_with_required_artifacts_present(self, workspace: Path, capsys):
        (workspace / "doc.md").write_text("# Content")

        result = main([
            "start",
            "--process", "demo",
            "--required", "doc.md",
            "--workspace", str(workspace),
        ])

        assert result == 0

    def test_start_with_missing_artifacts(self, workspace: Path, capsys):
        result = main([
            "start",
            "--process", "demo",
            "--required", "missing.md",
            "--workspace", str(workspace),
        ])

        assert result == 0
        session_id = capsys.readouterr().out.strip()
        # Session created but in AWAITING_INPUT state
        assert len(session_id) == 8


class TestCLIResume:
    """Tests for resume command."""

    def test_resume_transitions_to_running(self, workspace: Path, capsys):
        # Start with missing artifact
        main([
            "start",
            "--process", "demo",
            "--required", "doc.md",
            "--workspace", str(workspace),
        ])
        session_id = capsys.readouterr().out.strip()

        # Create the artifact
        (workspace / "doc.md").write_text("# Created")

        # Resume
        result = main([
            "resume",
            session_id,
            "--workspace", str(workspace),
        ])

        assert result == 0
        state = capsys.readouterr().out.strip()
        assert state == "RUNNING"


class TestCLIReset:
    """Tests for reset command."""

    def test_reset_to_step(self, workspace: Path, capsys):
        # Start session
        main([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])
        session_id = capsys.readouterr().out.strip()

        # Add step manually via repo
        from symforge.infrastructure.session_repository import SessionRepository
        repo = SessionRepository(workspace / ".symforge" / "sessions")
        session = repo.load(session_id)
        session.add_step("step1")
        session.add_step("step2")
        repo.update(session)

        # Reset to step1
        result = main([
            "reset",
            session_id,
            "step1",
            "--workspace", str(workspace),
        ])

        assert result == 0
        state = capsys.readouterr().out.strip()
        assert state == "RUNNING"

        # Verify history truncated
        session = repo.load(session_id)
        assert session.history == ["step1"]


class TestCLIDecide:
    """Tests for decide command (HIL)."""

    def test_decide_registers_decision(self, workspace: Path, capsys):
        # Start session
        main([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])
        session_id = capsys.readouterr().out.strip()

        # Set session to AWAITING_DECISION
        from symforge.infrastructure.session_repository import SessionRepository
        repo = SessionRepository(workspace / ".symforge" / "sessions")
        session = repo.load(session_id)
        session.mark_awaiting_decision()
        repo.update(session)

        # Make decision
        result = main([
            "decide",
            session_id,
            "approved",
            "--workspace", str(workspace),
        ])

        assert result == 0
        state = capsys.readouterr().out.strip()
        assert state == "RUNNING"

        # Verify decision in history
        session = repo.load(session_id)
        assert "decision:approved" in session.history


class TestCLIStatus:
    """Tests for status command."""

    def test_status_shows_session_info(self, workspace: Path, capsys):
        # Start session
        main([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])
        session_id = capsys.readouterr().out.strip()

        # Get status
        result = main([
            "status",
            session_id,
            "--workspace", str(workspace),
        ])

        assert result == 0
        output = capsys.readouterr().out
        status = json.loads(output)

        assert status["id"] == session_id
        assert status["process_name"] == "demo"
        assert status["state"] == "RUNNING"


class TestCLIInit:
    """Tests for init command."""

    def test_init_creates_structure(self, tmp_path: Path, capsys):
        target = tmp_path / "my_project"

        result = main([
            "init",
            "-p", "bookforge",
            str(target),
        ])

        assert result == 0
        captured = capsys.readouterr()
        assert "init concluído" in captured.out
        assert (target / "process").exists()


class TestCLIHelp:
    """Tests for help output."""

    def test_help_shows_commands(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "start" in captured.out
        assert "resume" in captured.out
        assert "reset" in captured.out
        assert "decide" in captured.out
        assert "status" in captured.out
