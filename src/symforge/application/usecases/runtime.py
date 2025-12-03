from datetime import datetime
from pathlib import Path

from symforge.domain.exceptions import NoPendingDecisionError, StepNotFoundError
from symforge.domain.process_definition import ProcessDefinition
from symforge.domain.session import Session
from symforge.domain.states import SessionState
from symforge.infrastructure.session_repository import SessionRepository


class RuntimeUseCases:
    def __init__(self, sessions_dir: Path, auto_commit: bool = False):
        self.repo = SessionRepository(sessions_dir, auto_commit=auto_commit)

    def start(self, process: ProcessDefinition, workspace: Path) -> Session:
        missing = self._missing_artifacts(process.required_artifacts, workspace)
        session = self.repo.create(process, missing)
        if process.required_artifacts and missing:
            session.mark_awaiting_input(missing)
            self.repo.update(session)
        else:
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
            raise StepNotFoundError(step_id)
        session.reset_to(step_id)
        self.repo.update(session)
        return session

    def mark_decision(self, session: Session, decision: str) -> Session:
        if session.state != SessionState.AWAITING_DECISION:
            raise NoPendingDecisionError()
        session.register_decision(decision)
        self.repo.update(session)
        return session

    def pause(self, session: Session, workspace: Path) -> Path:
        """Pause session and generate handoff."""
        session.mark_paused()
        self.repo.update(session)
        return self._generate_handoff(session, workspace, "pause")

    def complete(self, session: Session, workspace: Path) -> Path:
        """Complete session and generate final handoff."""
        session.mark_completed()
        self.repo.update(session)
        return self._generate_handoff(session, workspace, "complete")

    def _generate_handoff(self, session: Session, workspace: Path, handoff_type: str) -> Path:
        """Generate handoff file for session."""
        handoffs_dir = workspace / ".symforge" / "handoffs"
        handoffs_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{session.id}_{handoff_type}_{timestamp}.md"
        handoff_path = handoffs_dir / filename

        # Extract decisions from history
        decisions = [h for h in session.history if h.startswith("decision:")]
        steps = [h for h in session.history if not h.startswith("decision:")]

        content = [
            f"# Handoff: {session.process_name}",
            "",
            f"**Session ID**: {session.id}",
            f"**Type**: {handoff_type}",
            f"**State**: {session.state.value}",
            f"**Timestamp**: {datetime.now().isoformat()}",
            "",
            "## Estado Atual",
            "",
            f"Sessão está em estado `{session.state.value}`.",
            "",
        ]

        if steps:
            content.extend([
                "## Passos Executados",
                "",
            ])
            for step in steps:
                content.append(f"- {step}")
            content.append("")

        if decisions:
            content.extend([
                "## Decisões Registradas",
                "",
            ])
            for dec in decisions:
                content.append(f"- {dec.replace('decision:', '')}")
            content.append("")

        if session.required_artifacts:
            content.extend([
                "## Artefatos Requeridos",
                "",
            ])
            for art in session.required_artifacts:
                content.append(f"- {art}")
            content.append("")

        # Next steps based on state
        content.extend([
            "## Proximos Passos",
            "",
        ])
        if handoff_type == "pause":
            content.append("- Retomar sessão com `symforge resume`")
            content.append("- Verificar artefatos pendentes")
        else:
            content.append("- Sessão concluída")
            content.append("- Revisar artefatos gerados")

        handoff_path.write_text("\n".join(content), encoding="utf-8")
        return handoff_path

    def _missing_artifacts(self, required: list[str], workspace: Path) -> list[str]:
        missing: list[str] = []
        for rel in required:
            path = workspace / rel
            if not path.exists():
                missing.append(rel)
        return missing
