from pathlib import Path
from typing import List, Optional

from symforge.domain.process_definition import ProcessDefinition
from symforge.domain.session import Session
from symforge.domain.states import SessionState
from symforge.infrastructure.session_repository import SessionRepository


class RuntimeUseCases:
    def __init__(self, sessions_dir: Path):
        self.repo = SessionRepository(sessions_dir)

    def start(self, process: ProcessDefinition, workspace: Path) -> Session:
        missing = self._missing_artifacts(process.required_artifacts, workspace)
        session = self.repo.create(process, missing)
        if not missing:
            session.state = SessionState.RUNNING
        self.repo.update(session)
        return session

    def resume_after_input(self, session: Session, workspace: Path) -> Session:
        missing = self._missing_artifacts(session.required_artifacts, workspace)
        if missing:
            session.mark_awaiting_input(missing)
        else:
            session.mark_running()
        self.repo.update(session)
        return session

    def reset_step(self, session: Session, step_id: str) -> Session:
        if not session.can_reset(step_id):
            raise ValueError("Passo sem versionamento para reset")
        session.reset_to(step_id)
        self.repo.update(session)
        return session

    def mark_decision(self, session: Session, decision: str) -> Session:
        if session.state != SessionState.AWAITING_DECISION:
            raise ValueError("Sem decisão pendente")
        session.register_decision(decision)
        self.repo.update(session)
        return session

    def _missing_artifacts(self, required: List[str], workspace: Path) -> List[str]:
        missing: List[str] = []
        for rel in required:
            path = workspace / rel
            if not path.exists():
                missing.append(rel)
        return missing
