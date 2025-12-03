"""
TDD Unit Tests for automatic handoff generation.

Tests cover:
- pause generates handoff file
- complete generates final handoff
- handoff contains session state
- handoff contains decisions
- handoff contains next steps
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from symforge.application.usecases.runtime import RuntimeUseCases
from symforge.domain.process_definition import ProcessDefinition
from symforge.domain.states import SessionState


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


@pytest.fixture
def sessions_dir(workspace: Path) -> Path:
    sessions = workspace / ".symforge" / "sessions"
    sessions.mkdir(parents=True)
    return sessions


@pytest.fixture
def runtime(sessions_dir: Path) -> RuntimeUseCases:
    return RuntimeUseCases(sessions_dir)


class TestPauseHandoff:
    """Tests for pause command generating handoff."""

    def test_pause_generates_handoff_file(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_path = runtime.pause(session, workspace)

        assert handoff_path.exists()
        assert "pause" in handoff_path.name
        assert session.id in handoff_path.name

    def test_pause_sets_paused_state(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        runtime.pause(session, workspace)

        assert session.state == SessionState.PAUSED

    def test_pause_handoff_contains_state(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_path = runtime.pause(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "PAUSED" in content
        assert "Estado Atual" in content

    def test_pause_handoff_contains_process_name(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="my_workflow")
        session = runtime.start(process, workspace)

        handoff_path = runtime.pause(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "my_workflow" in content

    def test_pause_handoff_contains_next_steps(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_path = runtime.pause(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "Proximos Passos" in content
        assert "symforge resume" in content


class TestCompleteHandoff:
    """Tests for complete command generating final handoff."""

    def test_complete_generates_handoff_file(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_path = runtime.complete(session, workspace)

        assert handoff_path.exists()
        assert "complete" in handoff_path.name
        assert session.id in handoff_path.name

    def test_complete_sets_completed_state(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        runtime.complete(session, workspace)

        assert session.state == SessionState.COMPLETED

    def test_complete_handoff_contains_completed_state(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_path = runtime.complete(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "COMPLETED" in content

    def test_complete_handoff_has_different_next_steps(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_path = runtime.complete(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "concluída" in content.lower()
        assert "symforge resume" not in content


class TestHandoffWithHistory:
    """Tests for handoff containing session history."""

    def test_handoff_contains_steps(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)
        session.add_step("step1")
        session.add_step("step2")
        runtime.repo.update(session)

        handoff_path = runtime.pause(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "step1" in content
        assert "step2" in content
        assert "Passos Executados" in content

    def test_handoff_contains_decisions(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)
        session.mark_awaiting_decision()
        runtime.repo.update(session)
        runtime.mark_decision(session, "approved")

        handoff_path = runtime.pause(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "approved" in content
        assert "Decisões Registradas" in content

    def test_handoff_contains_required_artifacts(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process", required_artifacts=["doc.md", "spec.yml"])
        session = runtime.start(process, workspace)

        handoff_path = runtime.pause(session, workspace)
        content = handoff_path.read_text(encoding="utf-8")

        assert "doc.md" in content
        assert "spec.yml" in content
        assert "Artefatos Requeridos" in content


class TestHandoffLocation:
    """Tests for handoff file location."""

    def test_handoff_saved_in_handoffs_directory(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_path = runtime.pause(session, workspace)

        expected_dir = workspace / ".symforge" / "handoffs"
        assert handoff_path.parent == expected_dir

    def test_multiple_handoffs_different_types(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test_process")
        session = runtime.start(process, workspace)

        handoff_pause = runtime.pause(session, workspace)
        # Reset to running to allow complete
        session.mark_running()
        runtime.repo.update(session)
        handoff_complete = runtime.complete(session, workspace)

        assert handoff_pause.exists()
        assert handoff_complete.exists()
        assert "pause" in handoff_pause.name
        assert "complete" in handoff_complete.name
