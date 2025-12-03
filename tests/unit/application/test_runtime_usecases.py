"""
TDD Unit Tests for RuntimeUseCases application layer.

Tests cover:
- start() - session initialization with artifact validation
- resume_after_input() - resume after missing artifacts provided
- reset_step() - rollback to previous step
- mark_decision() - HIL decision registration
- Error handling and edge cases
"""

import pytest
from pathlib import Path

from symforge.application.usecases.runtime import RuntimeUseCases
from symforge.domain.exceptions import NoPendingDecisionError, StepNotFoundError
from symforge.domain.process_definition import ProcessDefinition
from symforge.domain.states import SessionState


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create a workspace directory for tests."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


@pytest.fixture
def runtime(workspace: Path) -> RuntimeUseCases:
    """Create RuntimeUseCases instance."""
    return RuntimeUseCases(workspace / ".symforge" / "sessions")


class TestRuntimeStart:
    """Tests for start() use case."""

    def test_start_creates_session(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test")

        session = runtime.start(process, workspace)

        assert session is not None
        assert session.id is not None

    def test_start_with_no_artifacts_returns_running(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test", required_artifacts=[])

        session = runtime.start(process, workspace)

        assert session.state == SessionState.RUNNING

    def test_start_with_all_artifacts_present_returns_running(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        (workspace / "doc.md").write_text("# Content")
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])

        session = runtime.start(process, workspace)

        assert session.state == SessionState.RUNNING

    def test_start_with_missing_artifact_returns_awaiting_input(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test", required_artifacts=["missing.md"])

        session = runtime.start(process, workspace)

        assert session.state == SessionState.AWAITING_INPUT

    def test_start_sets_missing_artifacts_list(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(
            name="test", required_artifacts=["file1.md", "file2.md"]
        )

        session = runtime.start(process, workspace)

        assert session.missing_artifacts == ["file1.md", "file2.md"]

    def test_start_with_partial_artifacts(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        (workspace / "file1.md").write_text("# Exists")
        process = ProcessDefinition(
            name="test", required_artifacts=["file1.md", "file2.md"]
        )

        session = runtime.start(process, workspace)

        assert session.state == SessionState.AWAITING_INPUT
        assert session.missing_artifacts == ["file2.md"]

    def test_start_persists_session(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)

        loaded = runtime.repo.load(session.id)

        assert loaded.id == session.id
        assert loaded.process_name == "test"

    def test_start_with_nested_artifact_path(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        nested = workspace / "docs" / "readme.md"
        nested.parent.mkdir(parents=True)
        nested.write_text("# Nested")
        process = ProcessDefinition(
            name="test", required_artifacts=["docs/readme.md"]
        )

        session = runtime.start(process, workspace)

        assert session.state == SessionState.RUNNING


class TestRuntimeResumeAfterInput:
    """Tests for resume_after_input() use case."""

    def test_resume_with_artifacts_present_transitions_to_running(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])
        session = runtime.start(process, workspace)
        assert session.state == SessionState.AWAITING_INPUT

        # Create missing artifact
        (workspace / "doc.md").write_text("# Created")

        session = runtime.resume_after_input(session, workspace)

        assert session.state == SessionState.RUNNING

    def test_resume_clears_missing_artifacts(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])
        session = runtime.start(process, workspace)

        (workspace / "doc.md").write_text("# Created")
        session = runtime.resume_after_input(session, workspace)

        assert session.missing_artifacts == []

    def test_resume_with_still_missing_stays_awaiting_input(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(
            name="test", required_artifacts=["file1.md", "file2.md"]
        )
        session = runtime.start(process, workspace)

        # Only create one file
        (workspace / "file1.md").write_text("# Created")

        session = runtime.resume_after_input(session, workspace)

        assert session.state == SessionState.AWAITING_INPUT
        assert session.missing_artifacts == ["file2.md"]

    def test_resume_persists_updated_session(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])
        session = runtime.start(process, workspace)

        (workspace / "doc.md").write_text("# Created")
        session = runtime.resume_after_input(session, workspace)

        loaded = runtime.repo.load(session.id)
        assert loaded.state == SessionState.RUNNING


class TestRuntimeResetStep:
    """Tests for reset_step() use case."""

    def test_reset_to_existing_step_succeeds(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.add_step("step1")
        session.add_step("step2")
        runtime.repo.update(session)

        session = runtime.reset_step(session, "step1")

        assert session.history == ["step1"]

    def test_reset_changes_state_to_running(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.add_step("step1")
        session.mark_awaiting_input(["file.md"])
        runtime.repo.update(session)

        session = runtime.reset_step(session, "step1")

        assert session.state == SessionState.RUNNING

    def test_reset_to_nonexistent_step_raises_error(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.add_step("step1")
        runtime.repo.update(session)

        with pytest.raises(StepNotFoundError):
            runtime.reset_step(session, "step_unknown")

    def test_reset_persists_updated_session(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.add_step("step1")
        session.add_step("step2")
        runtime.repo.update(session)

        session = runtime.reset_step(session, "step1")

        loaded = runtime.repo.load(session.id)
        assert loaded.history == ["step1"]

    def test_reset_on_empty_history_raises_error(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)

        with pytest.raises(StepNotFoundError):
            runtime.reset_step(session, "step1")


class TestRuntimeMarkDecision:
    """Tests for mark_decision() use case (HIL)."""

    def test_mark_decision_registers_decision(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.mark_awaiting_decision()
        runtime.repo.update(session)

        session = runtime.mark_decision(session, "approved")

        assert "decision:approved" in session.history

    def test_mark_decision_transitions_to_running(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.mark_awaiting_decision()
        runtime.repo.update(session)

        session = runtime.mark_decision(session, "approved")

        assert session.state == SessionState.RUNNING

    def test_mark_decision_clears_pending_flag(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.mark_awaiting_decision()
        runtime.repo.update(session)

        session = runtime.mark_decision(session, "approved")

        assert session.pending_decision is False

    def test_mark_decision_without_pending_raises_error(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)

        with pytest.raises(NoPendingDecisionError):
            runtime.mark_decision(session, "approved")

    def test_mark_decision_persists_session(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.mark_awaiting_decision()
        runtime.repo.update(session)

        session = runtime.mark_decision(session, "approved")

        loaded = runtime.repo.load(session.id)
        assert "decision:approved" in loaded.history


class TestRuntimeEdgeCases:
    """Edge cases and integration scenarios."""

    def test_full_workflow_scenario(self, runtime: RuntimeUseCases, workspace: Path):
        """Test complete workflow: start -> await -> resume -> step -> decide."""
        # 1. Start with missing artifact
        process = ProcessDefinition(name="workflow", required_artifacts=["doc.md"])
        session = runtime.start(process, workspace)
        assert session.state == SessionState.AWAITING_INPUT

        # 2. Create artifact and resume
        (workspace / "doc.md").write_text("# Done")
        session = runtime.resume_after_input(session, workspace)
        assert session.state == SessionState.RUNNING

        # 3. Add steps
        session.add_step("step1")
        session.add_step("step2")
        runtime.repo.update(session)

        # 4. Require decision
        session.mark_awaiting_decision()
        runtime.repo.update(session)
        assert session.state == SessionState.AWAITING_DECISION

        # 5. Make decision
        session = runtime.mark_decision(session, "go_ahead")
        assert session.state == SessionState.RUNNING

        # 6. Verify history
        assert session.history == ["step1", "step2", "decision:go_ahead"]

    def test_reset_after_decision(self, runtime: RuntimeUseCases, workspace: Path):
        process = ProcessDefinition(name="test")
        session = runtime.start(process, workspace)
        session.add_step("step1")
        session.mark_awaiting_decision()
        session.register_decision("approved")
        session.add_step("step2")
        runtime.repo.update(session)

        session = runtime.reset_step(session, "step1")

        assert session.history == ["step1"]
        assert "decision:approved" not in session.history

    def test_multiple_artifacts_validation(
        self, runtime: RuntimeUseCases, workspace: Path
    ):
        (workspace / "a.md").write_text("a")
        (workspace / "c.md").write_text("c")
        process = ProcessDefinition(
            name="test", required_artifacts=["a.md", "b.md", "c.md", "d.md"]
        )

        session = runtime.start(process, workspace)

        assert session.state == SessionState.AWAITING_INPUT
        assert sorted(session.missing_artifacts) == ["b.md", "d.md"]
