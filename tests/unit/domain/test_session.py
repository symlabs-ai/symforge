"""
TDD Unit Tests for Session domain entity.

Tests cover:
- State transitions (state machine)
- History management
- Decision registration
- Reset/rollback behavior
- Edge cases and invariants
"""

import pytest

from symforge.domain.exceptions import StepNotFoundError
from symforge.domain.session import Session
from symforge.domain.states import SessionState


class TestSessionCreation:
    """Tests for Session instantiation."""

    def test_session_created_with_running_state_by_default(self):
        session = Session(id="abc123", process_name="demo")
        assert session.state == SessionState.RUNNING

    def test_session_created_with_empty_history(self):
        session = Session(id="abc123", process_name="demo")
        assert session.history == []

    def test_session_created_with_empty_missing_artifacts(self):
        session = Session(id="abc123", process_name="demo")
        assert session.missing_artifacts == []

    def test_session_created_with_required_artifacts(self):
        session = Session(
            id="abc123",
            process_name="demo",
            required_artifacts=["doc.md", "config.yml"],
        )
        assert session.required_artifacts == ["doc.md", "config.yml"]

    def test_session_pending_decision_false_by_default(self):
        session = Session(id="abc123", process_name="demo")
        assert session.pending_decision is False


class TestSessionStateTransitions:
    """Tests for state machine transitions."""

    def test_mark_awaiting_input_changes_state(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_input(["missing.md"])

        assert session.state == SessionState.AWAITING_INPUT

    def test_mark_awaiting_input_sets_missing_artifacts(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_input(["file1.md", "file2.yml"])

        assert session.missing_artifacts == ["file1.md", "file2.yml"]

    def test_mark_running_changes_state_from_awaiting_input(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_input(["missing.md"])
        session.mark_running()

        assert session.state == SessionState.RUNNING

    def test_mark_running_clears_missing_artifacts(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_input(["missing.md"])
        session.mark_running()

        assert session.missing_artifacts == []

    def test_mark_awaiting_decision_changes_state(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_decision()

        assert session.state == SessionState.AWAITING_DECISION

    def test_mark_awaiting_decision_sets_pending_decision(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_decision()

        assert session.pending_decision is True


class TestSessionDecisionRegistration:
    """Tests for HIL decision registration."""

    def test_register_decision_adds_to_history(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_decision()
        session.register_decision("approved")

        assert "decision:approved" in session.history

    def test_register_decision_clears_pending_decision(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_decision()
        session.register_decision("approved")

        assert session.pending_decision is False

    def test_register_decision_returns_to_running(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_decision()
        session.register_decision("approved")

        assert session.state == SessionState.RUNNING

    def test_register_multiple_decisions(self):
        session = Session(id="abc123", process_name="demo")

        session.mark_awaiting_decision()
        session.register_decision("first_decision")

        session.mark_awaiting_decision()
        session.register_decision("second_decision")

        assert "decision:first_decision" in session.history
        assert "decision:second_decision" in session.history
        assert len([h for h in session.history if h.startswith("decision:")]) == 2


class TestSessionHistory:
    """Tests for step history management."""

    def test_add_step_appends_to_history(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")

        assert "step1" in session.history

    def test_add_multiple_steps_preserves_order(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.add_step("step2")
        session.add_step("step3")

        assert session.history == ["step1", "step2", "step3"]

    def test_history_includes_both_steps_and_decisions(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.mark_awaiting_decision()
        session.register_decision("go")
        session.add_step("step2")

        assert session.history == ["step1", "decision:go", "step2"]


class TestSessionReset:
    """Tests for rollback/reset behavior."""

    def test_can_reset_returns_true_for_existing_step(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")

        assert session.can_reset("step1") is True

    def test_can_reset_returns_false_for_nonexistent_step(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")

        assert session.can_reset("step_unknown") is False

    def test_can_reset_returns_false_for_empty_history(self):
        session = Session(id="abc123", process_name="demo")

        assert session.can_reset("step1") is False

    def test_reset_to_truncates_history(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.add_step("step2")
        session.add_step("step3")

        session.reset_to("step1")

        assert session.history == ["step1"]

    def test_reset_to_middle_step(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.add_step("step2")
        session.add_step("step3")

        session.reset_to("step2")

        assert session.history == ["step1", "step2"]

    def test_reset_to_last_step_keeps_all_history(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.add_step("step2")

        session.reset_to("step2")

        assert session.history == ["step1", "step2"]

    def test_reset_to_sets_state_to_running(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.mark_awaiting_input(["file.md"])

        session.reset_to("step1")

        assert session.state == SessionState.RUNNING

    def test_reset_to_nonexistent_step_raises_error(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")

        with pytest.raises(StepNotFoundError):
            session.reset_to("step_unknown")

    def test_reset_preserves_step_in_history(self):
        """Reset should keep the target step in history (inclusive reset)."""
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.add_step("step2")

        session.reset_to("step1")

        assert "step1" in session.history


class TestSessionEdgeCases:
    """Edge cases and invariants."""

    def test_empty_missing_artifacts_list(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_input([])

        assert session.state == SessionState.AWAITING_INPUT
        assert session.missing_artifacts == []

    def test_decision_with_empty_string(self):
        session = Session(id="abc123", process_name="demo")
        session.mark_awaiting_decision()
        session.register_decision("")

        assert "decision:" in session.history

    def test_step_with_special_characters(self):
        session = Session(id="abc123", process_name="demo")
        session.add_step("step:with:colons")
        session.add_step("step/with/slashes")

        assert "step:with:colons" in session.history
        assert "step/with/slashes" in session.history

    def test_duplicate_step_ids_in_history(self):
        """Duplicate steps are allowed (re-execution)."""
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.add_step("step1")

        assert session.history.count("step1") == 2

    def test_reset_to_first_occurrence_of_duplicate_step(self):
        """Reset to step with duplicates resets to first occurrence."""
        session = Session(id="abc123", process_name="demo")
        session.add_step("step1")
        session.add_step("step2")
        session.add_step("step1")  # duplicate
        session.add_step("step3")

        session.reset_to("step1")

        # Should reset to first occurrence
        assert session.history == ["step1"]
