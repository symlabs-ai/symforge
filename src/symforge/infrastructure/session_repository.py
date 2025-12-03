import subprocess
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
    Suporta auto-commit Git por transição de estado.
    """

    def __init__(self, base_dir: Path, auto_commit: bool = False):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.auto_commit = auto_commit

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
        if self.auto_commit:
            self._git_commit(path, f"[symforge] session {session.id} -> {session.state.value}")

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

    def _git_root(self) -> Path | None:
        current = self.base_dir.resolve()
        for candidate in [current, *current.parents]:
            if (candidate / ".git").exists():
                return candidate
        return None

    def _git_commit(self, file_path: Path, message: str) -> None:
        """Commit session file to git if in a git repository."""
        repo_root = self._git_root()
        if repo_root is None:
            return
        try:
            subprocess.run(
                ["git", "-C", str(repo_root), "add", str(file_path.resolve())],
                check=False,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repo_root), "commit", "-m", message],
                check=False,
                capture_output=True,
            )
        except Exception:
            # Git indisponível ou sem configuração; não impede o fluxo.
            pass
