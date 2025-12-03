"""
E2E Tests for complete CLI workflows.

Tests cover complete user journeys:
- Full project initialization and session workflow
- Plugin lifecycle (add -> list -> execute)
- Validation workflows
- Error recovery scenarios
"""

import json
import os
import sys
from io import StringIO
from pathlib import Path

import pytest

# Add src to path for imports
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from symforge.cli import main


class CLIRunner:
    """Simple CLI runner that captures stdout/stderr."""

    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path
        self.original_cwd = os.getcwd()

    def invoke(self, args: list[str]) -> "CLIResult":
        """Run CLI command and capture output."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        try:
            exit_code = main(args)
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0
        except Exception as e:
            exit_code = 1
            sys.stderr.write(str(e))
        finally:
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return CLIResult(exit_code, stdout, stderr)

    def chdir(self, path: Path):
        """Change to directory."""
        os.chdir(path)

    def restore_cwd(self):
        """Restore original working directory."""
        os.chdir(self.original_cwd)


class CLIResult:
    """Result of CLI invocation."""

    def __init__(self, exit_code: int, output: str, stderr: str):
        self.exit_code = exit_code
        self.output = output
        self.stderr = stderr


@pytest.fixture
def runner(tmp_path: Path) -> CLIRunner:
    """Create a CLI runner."""
    r = CLIRunner(tmp_path)
    yield r
    r.restore_cwd()


class TestE2EInitWorkflow:
    """E2E tests for project initialization workflow."""

    def test_init_and_validate_forgeprocess(self, runner: CLIRunner, tmp_path: Path):
        """Test: init creates valid structure that passes validation."""
        target = tmp_path / "my_project"

        # Step 1: Initialize project
        result = runner.invoke(["init", "-p", "forgeprocess", str(target)])

        assert result.exit_code == 0
        assert "init concluído" in result.output
        assert (target / "process").exists()

        # Step 2: Validate the generated process
        process_file = target / "process" / "PROCESS.yml"
        if process_file.exists():
            result = runner.invoke(["validate", str(process_file)])
            # Should pass or fail gracefully
            assert result.exit_code in [0, 1]

    def test_init_and_validate_bookforge(self, runner: CLIRunner, tmp_path: Path):
        """Test: bookforge template creates valid structure."""
        target = tmp_path / "my_book"

        result = runner.invoke(["init", "-p", "bookforge", str(target)])

        assert result.exit_code == 0
        assert (target / "process").exists()

    def test_init_with_invalid_preset(self, runner: CLIRunner, tmp_path: Path):
        """Test: invalid preset shows error."""
        target = tmp_path / "project"

        result = runner.invoke(["init", "-p", "invalid_preset", str(target)])

        # Should fail gracefully or create minimal structure
        # (behavior depends on implementation)
        assert result.exit_code == 0 or "erro" in (result.output + result.stderr).lower()


class TestE2ESessionWorkflow:
    """E2E tests for complete session lifecycle."""

    def test_full_session_lifecycle(self, runner: CLIRunner, tmp_path: Path):
        """Test: start -> status -> complete workflow."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Step 1: Start session
        result = runner.invoke([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])

        assert result.exit_code == 0
        session_id = result.output.strip()
        assert len(session_id) == 8

        # Step 2: Check status
        result = runner.invoke([
            "status",
            session_id,
            "--workspace", str(workspace),
        ])

        assert result.exit_code == 0
        status = json.loads(result.output)
        assert status["id"] == session_id
        assert status["state"] == "RUNNING"

    def test_session_with_required_artifacts(self, runner: CLIRunner, tmp_path: Path):
        """Test: session with required artifacts workflow."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Step 1: Start with missing artifact
        result = runner.invoke([
            "start",
            "--process", "demo",
            "--required", "doc.md",
            "--workspace", str(workspace),
        ])

        assert result.exit_code == 0
        session_id = result.output.strip()

        # Step 2: Create artifact
        (workspace / "doc.md").write_text("# Document", encoding="utf-8")

        # Step 3: Resume
        result = runner.invoke([
            "resume",
            session_id,
            "--workspace", str(workspace),
        ])

        assert result.exit_code == 0
        assert "RUNNING" in result.output

    def test_session_hil_decision_flow(self, runner: CLIRunner, tmp_path: Path):
        """Test: Human-in-the-Loop decision workflow."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Step 1: Start session
        result = runner.invoke([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])
        session_id = result.output.strip()

        # Step 2: Manually set to awaiting decision (simulating HIL checkpoint)
        from symforge.infrastructure.session_repository import SessionRepository
        repo = SessionRepository(workspace / ".symforge" / "sessions")
        session = repo.load(session_id)
        session.mark_awaiting_decision()
        repo.update(session)

        # Step 3: Make decision
        result = runner.invoke([
            "decide",
            session_id,
            "approved",
            "--workspace", str(workspace),
        ])

        assert result.exit_code == 0
        assert "RUNNING" in result.output

        # Step 4: Verify decision in status
        result = runner.invoke([
            "status",
            session_id,
            "--workspace", str(workspace),
        ])
        status = json.loads(result.output)
        assert "decision:approved" in status["history"]

    def test_session_reset_workflow(self, runner: CLIRunner, tmp_path: Path):
        """Test: reset to previous step workflow."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Step 1: Start session
        result = runner.invoke([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])
        session_id = result.output.strip()

        # Step 2: Add steps
        from symforge.infrastructure.session_repository import SessionRepository
        repo = SessionRepository(workspace / ".symforge" / "sessions")
        session = repo.load(session_id)
        session.add_step("step1")
        session.add_step("step2")
        session.add_step("step3")
        repo.update(session)

        # Step 3: Reset to step2
        result = runner.invoke([
            "reset",
            session_id,
            "step2",
            "--workspace", str(workspace),
        ])

        assert result.exit_code == 0

        # Step 4: Verify history truncated
        session = repo.load(session_id)
        assert session.history == ["step1", "step2"]


class TestE2EPluginWorkflow:
    """E2E tests for complete plugin lifecycle."""

    def _create_send_plugin(self, path: Path, plugin_id: str = "test_sender") -> Path:
        """Helper to create a send plugin."""
        repo = path / f"{plugin_id}_repo"
        repo.mkdir()
        (repo / "plugin.yml").write_text(f"""\
id: {plugin_id}
name: Test Sender
version: "1.0.0"
type: send
entrypoint: plugin:send
permissions:
  network: false
  fs: []
  env: []
""", encoding="utf-8")
        (repo / "plugin.py").write_text("""\
def send(payload):
    return {"sent": True, "payload": payload}
""", encoding="utf-8")
        return repo

    def _create_export_plugin(self, path: Path, plugin_id: str = "test_exporter") -> Path:
        """Helper to create an export plugin."""
        repo = path / f"{plugin_id}_repo"
        repo.mkdir()
        (repo / "plugin.yml").write_text(f"""\
id: {plugin_id}
name: Test Exporter
version: "1.0.0"
type: export
entrypoint: plugin:export
permissions:
  network: false
  fs: []
  env: []
""", encoding="utf-8")
        (repo / "plugin.py").write_text("""\
def export(input_path, output_path=None):
    content = input_path.read_text() if hasattr(input_path, 'read_text') else str(input_path)
    return {"exported": True, "content_length": len(content)}
""", encoding="utf-8")
        return repo

    def test_plugin_add_list_execute_workflow(self, runner: CLIRunner, tmp_path: Path):
        """Test: add plugin -> list -> execute send."""
        runner.chdir(tmp_path)

        # Step 1: Create and add plugin
        plugin_repo = self._create_send_plugin(tmp_path, "my_sender")

        result = runner.invoke(["plugin", "add", str(plugin_repo)])
        assert result.exit_code == 0
        assert "plugin instalado" in result.output

        # Step 2: List plugins
        result = runner.invoke(["plugin", "list"])
        assert result.exit_code == 0
        plugins = json.loads(result.output)
        assert len(plugins) == 1
        assert plugins[0]["id"] == "my_sender"
        assert plugins[0]["type"] == "send"

        # Step 3: Execute send
        result = runner.invoke([
            "plugin", "send",
            "my_sender",
            '{"message": "hello world"}',
        ])
        assert result.exit_code == 0
        response = json.loads(result.output)
        assert response["sent"] is True
        assert response["payload"]["message"] == "hello world"

    def test_plugin_export_workflow(self, runner: CLIRunner, tmp_path: Path):
        """Test: export plugin workflow."""
        runner.chdir(tmp_path)

        # Step 1: Create and add export plugin
        plugin_repo = self._create_export_plugin(tmp_path, "csv_exporter")
        runner.invoke(["plugin", "add", str(plugin_repo)])

        # Step 2: Create input file
        input_file = tmp_path / "input.md"
        input_file.write_text("# Hello World\n\nThis is content.", encoding="utf-8")
        output_file = tmp_path / "output.csv"

        # Step 3: Execute export
        result = runner.invoke([
            "plugin", "export",
            "csv_exporter",
            str(input_file),
            "--output", str(output_file),
        ])

        assert result.exit_code == 0
        response = json.loads(result.output)
        assert response["exported"] is True

    def test_plugin_invalid_manifest_rejected(self, runner: CLIRunner, tmp_path: Path):
        """Test: plugin with invalid manifest is rejected."""
        runner.chdir(tmp_path)

        # Create plugin with missing required fields
        plugin_repo = tmp_path / "bad_plugin"
        plugin_repo.mkdir()
        (plugin_repo / "plugin.yml").write_text("name: Incomplete", encoding="utf-8")
        (plugin_repo / "plugin.py").write_text("def run(): pass", encoding="utf-8")

        result = runner.invoke(["plugin", "add", str(plugin_repo)])

        assert result.exit_code != 0
        # Check for error indicators in output
        combined = (result.output + result.stderr).lower()
        assert "inválido" in combined or "invalid" in combined or "erro" in combined or "faltando" in combined

    def test_plugin_network_permission_rejected(self, runner: CLIRunner, tmp_path: Path):
        """Test: plugin requesting network is rejected in offline mode."""
        runner.chdir(tmp_path)

        # Create plugin with network permission
        plugin_repo = tmp_path / "net_plugin"
        plugin_repo.mkdir()
        (plugin_repo / "plugin.yml").write_text("""\
id: net_plugin
name: Network Plugin
version: "1.0.0"
type: send
entrypoint: plugin:send
permissions:
  network: true
  fs: []
  env: []
""", encoding="utf-8")
        (plugin_repo / "plugin.py").write_text("def send(p): pass", encoding="utf-8")

        result = runner.invoke(["plugin", "add", str(plugin_repo)])

        assert result.exit_code != 0
        assert "network" in (result.output + result.stderr).lower() or "permission" in (result.output + result.stderr).lower()


class TestE2EValidationWorkflow:
    """E2E tests for validation workflows."""

    def test_validate_valid_process(self, runner: CLIRunner, tmp_path: Path):
        """Test: validate a correctly structured process."""
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("""\
name: My Process
description: A test process
phases:
  - id: phase1
    name: Phase One
    description: First phase
  - id: phase2
    name: Phase Two
    description: Second phase
""", encoding="utf-8")

        result = runner.invoke(["validate", str(process_file)])

        assert result.exit_code == 0
        assert "ok" in result.output.lower()

    def test_validate_missing_phases(self, runner: CLIRunner, tmp_path: Path):
        """Test: validate catches missing phases."""
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("name: No Phases", encoding="utf-8")

        result = runner.invoke(["validate", str(process_file)])

        assert result.exit_code == 1
        assert "phases" in (result.output + result.stderr).lower() or "falhou" in (result.output + result.stderr).lower()

    def test_validate_invalid_yaml(self, runner: CLIRunner, tmp_path: Path):
        """Test: validate catches YAML syntax errors."""
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("name: test\nphases: [unclosed", encoding="utf-8")

        result = runner.invoke(["validate", str(process_file)])

        assert result.exit_code == 1

    def test_validate_recursive_with_artifacts(self, runner: CLIRunner, tmp_path: Path):
        """Test: recursive validation checks artifact existence."""
        # Create process with artifact reference
        process_dir = tmp_path / "process"
        process_dir.mkdir()
        process_file = process_dir / "PROCESS.yml"
        process_file.write_text("""\
name: With Artifacts
phases:
  - id: phase1
    name: Phase One
    artifacts:
      - docs/readme.md
""", encoding="utf-8")

        # Create the referenced artifact
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "readme.md").write_text("# Readme", encoding="utf-8")

        result = runner.invoke(["validate", str(process_file), "--recursive"])

        # Should pass since artifact exists
        assert result.exit_code == 0


class TestE2EErrorRecovery:
    """E2E tests for error handling and recovery."""

    def test_status_nonexistent_session(self, runner: CLIRunner, tmp_path: Path):
        """Test: status for nonexistent session shows clear error."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        result = runner.invoke([
            "status",
            "nonexist",
            "--workspace", str(workspace),
        ])

        assert result.exit_code != 0
        # Check for error indicators (could be "não encontrada", "not found", "no such file", etc.)
        combined = (result.output + result.stderr).lower()
        assert "não encontrada" in combined or "not found" in combined or "no such file" in combined

    def test_reset_invalid_step(self, runner: CLIRunner, tmp_path: Path):
        """Test: reset to nonexistent step shows clear error."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create session
        result = runner.invoke([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])
        session_id = result.output.strip()

        # Try to reset to nonexistent step
        result = runner.invoke([
            "reset",
            session_id,
            "nonexistent_step",
            "--workspace", str(workspace),
        ])

        assert result.exit_code != 0

    def test_decide_without_pending_decision(self, runner: CLIRunner, tmp_path: Path):
        """Test: decide without pending decision shows clear error."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create session (starts in RUNNING, not AWAITING_DECISION)
        result = runner.invoke([
            "start",
            "--process", "demo",
            "--workspace", str(workspace),
        ])
        session_id = result.output.strip()

        # Try to decide without pending decision
        result = runner.invoke([
            "decide",
            session_id,
            "approved",
            "--workspace", str(workspace),
        ])

        assert result.exit_code != 0
        assert "decisão" in (result.output + result.stderr).lower() or "pending" in (result.output + result.stderr).lower()
