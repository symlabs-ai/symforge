from dataclasses import dataclass, field
from typing import List


@dataclass
class ProcessDefinition:
    name: str
    required_artifacts: List[str] = field(default_factory=list)
