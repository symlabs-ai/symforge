"""
TDD Unit Tests for SessionRepository infrastructure.

Tests cover:
- YAML persistence (save/load)
- Session creation with UUID
- State serialization/deserialization
- History and artifacts persistence
- Edge cases (file not found, corrupted data)
"""

import pytest
import yaml
from pathlib import Path

from symforge.domain.process_definition import ProcessDefinition
from symforge.domain.states import SessionState
from symforge.infrastructure.session_repository import SessionRepository


class TestSessionRepositoryCreation:
    """Tests for repository initialization."""

    def test_repository_creates_base_directory(self, tmp_path: Path):
        sessions_dir = tmp_path / ".symforge" / "sessions"
        SessionRepository(sessions_dir)

        assert sessions_dir.exists()
        assert sessions_dir.is_dir()

    def test_repository_works_with_existing_directory(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir(parents=True)

        SessionRepository(sessions_dir)

        assert sessions_dir.exists()


class TestSessionCreate:
    """Tests for session creation."""

    def test_create_returns_session_with_id(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="test_process")

        session = repo.create(process)

        assert session.id is not None
        assert len(session.id) == 8  # hex[:8]

    def test_create_sets_process_name(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="my_process")

        session = repo.create(process)

        assert session.process_name == "my_process"

    def test_create_with_missing_artifacts_sets_awaiting_input(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])

        session = repo.create(process, missing=["doc.md"])

        assert session.state == SessionState.AWAITING_INPUT
        assert session.missing_artifacts == ["doc.md"]

    def test_create_without_missing_keeps_running(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])

        session = repo.create(process, missing=None)

        assert session.state == SessionState.RUNNING

    def test_create_persists_session_to_yaml(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")

        session = repo.create(process)

        yaml_file = sessions_dir / f"{session.id}.yml"
        assert yaml_file.exists()

    def test_create_generates_unique_ids(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="test")

        session1 = repo.create(process)
        session2 = repo.create(process)

        assert session1.id != session2.id


class TestSessionUpdate:
    """Tests for session update/save."""

    def test_update_persists_state_change(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        session.mark_awaiting_input(["missing.md"])
        repo.update(session)

        loaded = repo.load(session.id)
        assert loaded.state == SessionState.AWAITING_INPUT

    def test_update_persists_history(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        session.add_step("step1")
        session.add_step("step2")
        repo.update(session)

        loaded = repo.load(session.id)
        assert loaded.history == ["step1", "step2"]

    def test_update_persists_decisions(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        session.mark_awaiting_decision()
        session.register_decision("approved")
        repo.update(session)

        loaded = repo.load(session.id)
        assert "decision:approved" in loaded.history

    def test_update_persists_missing_artifacts(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        session.mark_awaiting_input(["file1.md", "file2.yml"])
        repo.update(session)

        loaded = repo.load(session.id)
        assert loaded.missing_artifacts == ["file1.md", "file2.yml"]


class TestSessionLoad:
    """Tests for session loading."""

    def test_load_restores_all_fields(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])
        session = repo.create(process, missing=["doc.md"])
        session.add_step("step1")
        repo.update(session)

        loaded = repo.load(session.id)

        assert loaded.id == session.id
        assert loaded.process_name == "test"
        assert loaded.state == SessionState.AWAITING_INPUT
        assert loaded.required_artifacts == ["doc.md"]
        assert loaded.missing_artifacts == ["doc.md"]
        assert loaded.history == ["step1"]

    def test_load_nonexistent_session_raises_error(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")

        with pytest.raises(FileNotFoundError):
            repo.load("nonexistent")

    def test_load_restores_pending_decision_flag(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        session.mark_awaiting_decision()
        repo.update(session)

        loaded = repo.load(session.id)
        assert loaded.pending_decision is True


class TestYamlSerialization:
    """Tests for YAML format compliance."""

    def test_yaml_file_is_valid_yaml(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        yaml_file = sessions_dir / f"{session.id}.yml"
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))

        assert isinstance(data, dict)

    def test_yaml_contains_required_fields(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test", required_artifacts=["doc.md"])
        session = repo.create(process, missing=["doc.md"])

        yaml_file = sessions_dir / f"{session.id}.yml"
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))

        assert "id" in data
        assert "process_name" in data
        assert "state" in data
        assert "required_artifacts" in data
        assert "missing_artifacts" in data
        assert "history" in data
        assert "pending_decision" in data

    def test_yaml_state_is_string_value(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        yaml_file = sessions_dir / f"{session.id}.yml"
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))

        assert data["state"] == "RUNNING"

    def test_yaml_handles_unicode_content(self, tmp_path: Path):
        sessions_dir = tmp_path / "sessions"
        repo = SessionRepository(sessions_dir)
        process = ProcessDefinition(name="processo_português")
        session = repo.create(process)

        session.add_step("passo_com_acentuação")
        session.mark_awaiting_decision()
        session.register_decision("aprovação")
        repo.update(session)

        loaded = repo.load(session.id)
        assert loaded.process_name == "processo_português"
        assert "passo_com_acentuação" in loaded.history
        assert "decision:aprovação" in loaded.history


class TestSessionRepositoryEdgeCases:
    """Edge cases and error handling."""

    def test_create_with_empty_process_name(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="")

        session = repo.create(process)

        assert session.process_name == ""

    def test_update_multiple_times(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        session.add_step("step1")
        repo.update(session)
        session.add_step("step2")
        repo.update(session)
        session.add_step("step3")
        repo.update(session)

        loaded = repo.load(session.id)
        assert loaded.history == ["step1", "step2", "step3"]

    def test_load_after_state_transitions(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process = ProcessDefinition(name="test")
        session = repo.create(process)

        # Simulate full workflow
        session.add_step("step1")
        session.mark_awaiting_input(["file.md"])
        repo.update(session)

        loaded1 = repo.load(session.id)
        assert loaded1.state == SessionState.AWAITING_INPUT

        loaded1.mark_running()
        loaded1.add_step("step2")
        loaded1.mark_awaiting_decision()
        repo.update(loaded1)

        loaded2 = repo.load(session.id)
        assert loaded2.state == SessionState.AWAITING_DECISION
        assert loaded2.history == ["step1", "step2"]

    def test_concurrent_sessions(self, tmp_path: Path):
        repo = SessionRepository(tmp_path / "sessions")
        process1 = ProcessDefinition(name="process_a")
        process2 = ProcessDefinition(name="process_b")

        session1 = repo.create(process1)
        session2 = repo.create(process2)

        session1.add_step("step_a")
        session2.add_step("step_b")
        repo.update(session1)
        repo.update(session2)

        loaded1 = repo.load(session1.id)
        loaded2 = repo.load(session2.id)

        assert loaded1.history == ["step_a"]
        assert loaded2.history == ["step_b"]
        assert loaded1.process_name == "process_a"
        assert loaded2.process_name == "process_b"
