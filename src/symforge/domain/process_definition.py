from dataclasses import dataclass, field


@dataclass
class ProcessDefinition:
    name: str
    required_artifacts: list[str] = field(default_factory=list)
