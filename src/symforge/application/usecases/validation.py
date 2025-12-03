from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class ValidateUseCases:
    """
    Valida PROCESS.yml e, quando solicitado, verifica templates/artefatos.
    Nesta etapa, a validação é leve: garante presença de conteúdo YAML e
    existência da chave phases com lista.
    """

    def validate_process(self, process_path: Path, recursive: bool = False) -> ValidationResult:
        if not process_path.exists():
            return ValidationResult(False, ["PROCESS.yml não encontrado"])

        content = process_path.read_text(encoding="utf-8")
        if not content.strip():
            return ValidationResult(False, ["PROCESS.yml vazio ou sem conteúdo"])

        try:
            data = yaml.safe_load(content) or {}
        except yaml.YAMLError as exc:
            return ValidationResult(False, [f"YAML inválido: {exc}"])

        phases = data.get("phases", [])
        if not isinstance(phases, list) or not phases:
            return ValidationResult(False, ["phases ausentes ou vazias em PROCESS.yml"])

        details: dict[str, Any] = {"phases": phases}

        # Validação recursiva simplificada: assegura que artefatos referenciados existem.
        if recursive:
            missing_artifacts: list[str] = []
            process_dir = process_path.parent
            for phase in phases:
                artifacts = phase.get("artifacts", []) if isinstance(phase, dict) else []
                for artifact in artifacts:
                    artifact_path = process_dir.parent / artifact
                    if not artifact_path.exists():
                        missing_artifacts.append(str(artifact))
            if missing_artifacts:
                return ValidationResult(
                    False,
                    [f"Artefatos ausentes: {', '.join(missing_artifacts)}"],
                    details,
                )

        return ValidationResult(True, [], details)
