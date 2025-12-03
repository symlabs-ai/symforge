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


class TestCLIValidate:
    """Tests for validate command."""

    def test_validate_valid_process(self, tmp_path: Path, capsys):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "  - id: phase1\n"
            "    name: Phase One\n",
            encoding="utf-8",
        )

        result = main([
            "validate",
            str(process_file),
        ])

        assert result == 0
        captured = capsys.readouterr()
        assert "PROCESS.yml ok" in captured.out

    def test_validate_invalid_process(self, tmp_path: Path, capsys):
        process_file = tmp_path / "PROCESS.yml"
        # Invalid: missing name
        process_file.write_text("phases: []\n", encoding="utf-8")

        result = main([
            "validate",
            str(process_file),
        ])

        assert result == 1
        captured = capsys.readouterr()
        assert "validação falhou" in captured.err


class TestCLIPlugin:
    """Tests for plugin commands."""

    def _create_plugin(self, tmp_path: Path, plugin_id: str = "test_plugin") -> Path:
        repo = tmp_path / f"{plugin_id}_repo"
        repo.mkdir()
        manifest = f"""\
id: {plugin_id}
name: Test Plugin
version: "1.0.0"
type: send
entrypoint: plugin:run
permissions:
  network: false
  fs: []
  env: []
"""
        code = """\
def run(payload):
    return {"status": "ok", "data": payload}
"""
        (repo / "plugin.yml").write_text(manifest, encoding="utf-8")
        (repo / "plugin.py").write_text(code, encoding="utf-8")
        return repo

    def test_plugin_add(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        repo = self._create_plugin(tmp_path)

        result = main([
            "plugin", "add",
            str(repo),
        ])

        assert result == 0
        captured = capsys.readouterr()
        assert "plugin instalado" in captured.out

    def test_plugin_list_empty(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)

        result = main([
            "plugin", "list",
        ])

        assert result == 0
        captured = capsys.readouterr()
        plugins = json.loads(captured.out)
        assert plugins == []

    def test_plugin_list_with_plugins(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        repo = self._create_plugin(tmp_path, "my_plugin")
        main(["plugin", "add", str(repo)])
        capsys.readouterr()  # Clear output

        result = main([
            "plugin", "list",
        ])

        assert result == 0
        captured = capsys.readouterr()
        plugins = json.loads(captured.out)
        assert len(plugins) == 1
        assert plugins[0]["id"] == "my_plugin"

    def test_plugin_send(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        repo = self._create_plugin(tmp_path, "sender")
        main(["plugin", "add", str(repo)])
        capsys.readouterr()

        result = main([
            "plugin", "send",
            "sender",
            '{"message": "hello"}',
        ])

        assert result == 0
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["status"] == "ok"
        assert response["data"]["message"] == "hello"

    def test_plugin_export(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Create export plugin
        repo = tmp_path / "export_repo"
        repo.mkdir()
        (repo / "plugin.yml").write_text("""\
id: exporter
name: Exporter
version: "1.0.0"
type: export
entrypoint: plugin:export_file
permissions:
  network: false
  fs: []
  env: []
""", encoding="utf-8")
        (repo / "plugin.py").write_text("""\
def export_file(input_path, output_path=None):
    return {"input": str(input_path), "output": str(output_path)}
""", encoding="utf-8")
        main(["plugin", "add", str(repo)])
        capsys.readouterr()

        input_file = tmp_path / "input.md"
        input_file.write_text("# Input")
        output_file = tmp_path / "output.csv"

        result = main([
            "plugin", "export",
            "exporter",
            str(input_file),
            "--output", str(output_file),
        ])

        assert result == 0
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert "input" in response

    def test_plugin_hook(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Create hook plugin
        repo = tmp_path / "hook_repo"
        repo.mkdir()
        (repo / "plugin.yml").write_text("""\
id: hooker
name: Hooker
version: "1.0.0"
type: hook
entrypoint: plugin:on_event
permissions:
  network: false
  fs: []
  env: []
""", encoding="utf-8")
        (repo / "plugin.py").write_text("""\
def on_event(context):
    return {"event": context.get("event"), "handled": True}
""", encoding="utf-8")
        main(["plugin", "add", str(repo)])
        capsys.readouterr()

        result = main([
            "plugin", "hook",
            "hooker",
            '{"event": "step_completed"}',
        ])

        assert result == 0
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["event"] == "step_completed"
        assert response["handled"] is True

    def test_plugin_generate(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Create generate plugin
        repo = tmp_path / "gen_repo"
        repo.mkdir()
        (repo / "plugin.yml").write_text("""\
id: generator
name: Generator
version: "1.0.0"
type: generate
entrypoint: plugin:generate
permissions:
  network: false
  fs: []
  env: []
""", encoding="utf-8")
        (repo / "plugin.py").write_text("""\
def generate(payload):
    return {"content": f"Generated: {payload.get('prompt', '')}"}
""", encoding="utf-8")
        main(["plugin", "add", str(repo)])
        capsys.readouterr()

        result = main([
            "plugin", "generate",
            "generator",
            '{"prompt": "hello world"}',
        ])

        assert result == 0
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert "Generated: hello world" in response["content"]


class TestCLIAutoCommit:
    """Tests for --auto-commit flag."""

    def test_start_with_auto_commit(self, workspace: Path, capsys):
        result = main([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
            "--auto-commit",
        ])

        assert result == 0
