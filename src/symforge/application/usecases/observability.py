from pathlib import Path
from typing import List

import yaml

from symforge.domain.session import Session


class ObservabilityUseCases:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def generate_diagram(self, process_file: Path, output_path: Path) -> None:
        data = yaml.safe_load(process_file.read_text(encoding="utf-8")) or {}
        nodes = data.get("nodes", [])
        self._validate_nodes(nodes)
        mermaid = self._to_mermaid(nodes)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(mermaid, encoding="utf-8")

    def export_handoff(self, session: Session, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = [
            f"# Handoff da sessão {session.id}",
            f"Estado: {session.state.value}",
            f"Processo: {session.process_name}",
            "Histórico:",
        ]
        for item in session.history:
            content.append(f"- {item}")
        output_path.write_text("\n".join(content), encoding="utf-8")

    def _validate_nodes(self, nodes: List[dict]) -> None:
        for node in nodes:
            if "id" not in node or "type" not in node:
                raise ValueError("Nó inválido no PROCESS")

    def _to_mermaid(self, nodes: List[dict]) -> str:
        lines = ["```mermaid", "flowchart TD"]
        ids = [n["id"] for n in nodes]
        if len(ids) >= 2:
            lines.append(f"{ids[0]} --> {ids[-1]}")
        lines.append("```")
        return "\n".join(lines)
