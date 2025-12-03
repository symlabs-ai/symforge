from pathlib import Path
from typing import Optional

from symforge.application.usecases.runtime import RuntimeUseCases
from symforge.domain.process_definition import ProcessDefinition


class RuntimeCLI:
    """
    Adapter CLI para operações de runtime de sessão.
    Delega toda a lógica para RuntimeUseCases (Clean Architecture).
    """

    def __init__(self, workspace: Path, auto_commit: bool = False):
        self.workspace = workspace
        sessions_dir = workspace / ".symforge" / "sessions"
        self.runtime = RuntimeUseCases(sessions_dir, auto_commit=auto_commit)

    def start(self, process_name: str, required_artifacts: Optional[list[str]] = None) -> str:
        process = ProcessDefinition(name=process_name, required_artifacts=required_artifacts or [])
        session = self.runtime.start(process, self.workspace)
        return session.id

    def resume(self, session_id: str) -> str:
        session = self.runtime.repo.load(session_id)
        session = self.runtime.resume_after_input(session, self.workspace)
        return session.state.value

    def reset(self, session_id: str, step_id: str) -> str:
        session = self.runtime.repo.load(session_id)
        session = self.runtime.reset_step(session, step_id)
        return session.state.value

    def decide(self, session_id: str, decision: str) -> str:
        session = self.runtime.repo.load(session_id)
        session = self.runtime.mark_decision(session, decision)
        return session.state.value

    def status(self, session_id: str) -> dict:
        session = self.runtime.repo.load(session_id)
        return {
            "id": session.id,
            "process_name": session.process_name,
            "state": session.state.value,
            "missing_artifacts": session.missing_artifacts,
            "history": session.history,
            "pending_decision": session.pending_decision,
        }

    def pause(self, session_id: str) -> str:
        session = self.runtime.repo.load(session_id)
        handoff_path = self.runtime.pause(session, self.workspace)
        return str(handoff_path)

    def complete(self, session_id: str) -> str:
        session = self.runtime.repo.load(session_id)
        handoff_path = self.runtime.complete(session, self.workspace)
        return str(handoff_path)
