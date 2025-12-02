from dataclasses import dataclass, field

from symforge.domain.states import SessionState


@dataclass
class Session:
    id: str
    process_name: str
    state: SessionState = SessionState.RUNNING
    required_artifacts: list[str] = field(default_factory=list)
    missing_artifacts: list[str] = field(default_factory=list)
    history: list[str] = field(default_factory=list)
    pending_decision: bool = False

    def mark_awaiting_input(self, missing: list[str]) -> None:
        self.state = SessionState.AWAITING_INPUT
        self.missing_artifacts = missing

    def mark_running(self) -> None:
        self.state = SessionState.RUNNING
        self.missing_artifacts = []

    def mark_awaiting_decision(self) -> None:
        self.state = SessionState.AWAITING_DECISION
        self.pending_decision = True

    def register_decision(self, decision: str) -> None:
        self.history.append(f"decision:{decision}")
        self.pending_decision = False
        self.state = SessionState.RUNNING

    def add_step(self, step_id: str) -> None:
        self.history.append(step_id)

    def can_reset(self, step_id: str) -> bool:
        return step_id in self.history

    def reset_to(self, step_id: str) -> None:
        if step_id not in self.history:
            raise ValueError("Passo sem versionamento para reset")
        idx = self.history.index(step_id)
        self.history = self.history[: idx + 1]
        self.state = SessionState.RUNNING
