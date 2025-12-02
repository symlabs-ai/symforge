import uuid
from pathlib import Path

import yaml

from symforge.domain.process_definition import ProcessDefinition
from symforge.domain.session import Session
from symforge.domain.states import SessionState


class SessionRepository:
    """
    Repositório simples em YAML para sessões.
    Usa diretório base (ex.: .symforge/sessions) e cria arquivos por sessão.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create(self, process: ProcessDefinition, missing: list[str] | None = None) -> Session:
        session_id = uuid.uuid4().hex[:8]
        session = Session(
            id=session_id,
            process_name=process.name,
            required_artifacts=process.required_artifacts,
        )
        if missing:
            session.mark_awaiting_input(missing)
        self._save(session)
        return session

    def update(self, session: Session) -> None:
        self._save(session)

    def _save(self, session: Session) -> None:
        path = self.base_dir / f"{session.id}.yml"
        data = {
            "id": session.id,
            "process_name": session.process_name,
            "state": session.state.value,
            "required_artifacts": session.required_artifacts,
            "missing_artifacts": session.missing_artifacts,
            "history": session.history,
            "pending_decision": session.pending_decision,
        }
        with path.open("w", encoding="utf-8") as fp:
            yaml.safe_dump(data, fp)

    def load(self, session_id: str) -> Session:
        path = self.base_dir / f"{session_id}.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Session(
            id=data["id"],
            process_name=data["process_name"],
            state=SessionState(data["state"]),
            required_artifacts=data.get("required_artifacts", []),
            missing_artifacts=data.get("missing_artifacts", []),
            history=data.get("history", []),
            pending_decision=data.get("pending_decision", False),
        )
