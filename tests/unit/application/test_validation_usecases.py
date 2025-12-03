"""
TDD Unit Tests for ValidateUseCases application layer.

Tests cover:
- validate_process with valid PROCESS.yml
- validate_process with missing file
- validate_process with empty file
- validate_process with invalid YAML
- validate_process with missing phases
- validate_process with recursive artifact validation
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from symforge.application.usecases.validation import ValidateUseCases, ValidationResult


@pytest.fixture
def validator() -> ValidateUseCases:
    return ValidateUseCases()


class TestValidateProcessBasic:
    """Tests for basic validation scenarios."""

    def test_validate_valid_process(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "  - id: phase1\n"
            "    name: Phase One\n",
            encoding="utf-8",
        )

        result = validator.validate_process(process_file)

        assert result.is_valid
        assert result.errors == []
        assert "phases" in result.details

    def test_validate_missing_file(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        # File does not exist

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "não encontrado" in result.errors[0]

    def test_validate_empty_file(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("", encoding="utf-8")

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "vazio" in result.errors[0]

    def test_validate_whitespace_only_file(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("   \n\n   ", encoding="utf-8")

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "vazio" in result.errors[0]


class TestValidateProcessYamlErrors:
    """Tests for YAML parsing errors."""

    def test_validate_invalid_yaml_syntax(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "  - id: phase1\n"
            "    invalid: [unclosed bracket\n",
            encoding="utf-8",
        )

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "YAML inválido" in result.errors[0]

    def test_validate_invalid_yaml_tabs(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "\t- id: phase1\n",  # Tab character causes YAML error
            encoding="utf-8",
        )

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "YAML inválido" in result.errors[0]


class TestValidateProcessPhases:
    """Tests for phases validation."""

    def test_validate_missing_phases(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("name: test\n", encoding="utf-8")

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "phases ausentes" in result.errors[0]

    def test_validate_empty_phases(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("name: test\nphases: []\n", encoding="utf-8")

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "phases ausentes ou vazias" in result.errors[0]

    def test_validate_phases_not_list(self, validator: ValidateUseCases, tmp_path: Path):
        process_file = tmp_path / "PROCESS.yml"
        process_file.write_text("name: test\nphases: 'not a list'\n", encoding="utf-8")

        result = validator.validate_process(process_file)

        assert not result.is_valid
        assert "phases ausentes ou vazias" in result.errors[0]


class TestValidateProcessRecursive:
    """Tests for recursive artifact validation."""

    def test_validate_recursive_with_existing_artifacts(
        self, validator: ValidateUseCases, tmp_path: Path
    ):
        # Create directory structure
        process_dir = tmp_path / "process"
        process_dir.mkdir()
        process_file = process_dir / "PROCESS.yml"

        # Create artifact
        artifact_path = tmp_path / "docs" / "readme.md"
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("# Readme", encoding="utf-8")

        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "  - id: phase1\n"
            "    artifacts:\n"
            "      - docs/readme.md\n",
            encoding="utf-8",
        )

        result = validator.validate_process(process_file, recursive=True)

        assert result.is_valid

    def test_validate_recursive_with_missing_artifacts(
        self, validator: ValidateUseCases, tmp_path: Path
    ):
        process_dir = tmp_path / "process"
        process_dir.mkdir()
        process_file = process_dir / "PROCESS.yml"

        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "  - id: phase1\n"
            "    artifacts:\n"
            "      - missing/file.md\n",
            encoding="utf-8",
        )

        result = validator.validate_process(process_file, recursive=True)

        assert not result.is_valid
        assert "Artefatos ausentes" in result.errors[0]
        assert "missing/file.md" in result.errors[0]

    def test_validate_recursive_with_multiple_missing_artifacts(
        self, validator: ValidateUseCases, tmp_path: Path
    ):
        process_dir = tmp_path / "process"
        process_dir.mkdir()
        process_file = process_dir / "PROCESS.yml"

        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "  - id: phase1\n"
            "    artifacts:\n"
            "      - missing1.md\n"
            "      - missing2.md\n",
            encoding="utf-8",
        )

        result = validator.validate_process(process_file, recursive=True)

        assert not result.is_valid
        assert "missing1.md" in result.errors[0]
        assert "missing2.md" in result.errors[0]

    def test_validate_recursive_with_non_dict_phase(
        self, validator: ValidateUseCases, tmp_path: Path
    ):
        process_dir = tmp_path / "process"
        process_dir.mkdir()
        process_file = process_dir / "PROCESS.yml"

        # Phase is a string instead of dict
        process_file.write_text(
            "name: test\n"
            "phases:\n"
            "  - phase1_string\n",
            encoding="utf-8",
        )

        result = validator.validate_process(process_file, recursive=True)

        # Should still be valid - just skip non-dict phases
        assert result.is_valid


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_defaults(self):
        result = ValidationResult(is_valid=True)

        assert result.is_valid
        assert result.errors == []
        assert result.details == {}

    def test_validation_result_with_errors(self):
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
        )

        assert not result.is_valid
        assert len(result.errors) == 2

    def test_validation_result_with_details(self):
        result = ValidationResult(
            is_valid=True,
            details={"phases": [{"id": "p1"}]},
        )

        assert result.details["phases"][0]["id"] == "p1"
