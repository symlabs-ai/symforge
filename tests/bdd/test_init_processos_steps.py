import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from symforge.application.usecases.init_process import REQUIRED_PATHS, init_process
from symforge.application.usecases.validation import ValidateUseCases

scenarios("../../specs/bdd/10_forge_core/init_processos.feature")


@pytest.fixture
def target_dir(tmp_path: Path) -> Path:
    return tmp_path / "meu_projeto"

@pytest.fixture
def ctx() -> dict:
    return {}


@pytest.fixture
def validator() -> ValidateUseCases:
    return ValidateUseCases()


@given('que escolho um processo disponível na biblioteca (ex.: ForgeProcess, BookForge, OpsForge)', target_fixture="escolho_processo")
def escolho_processo(target_dir: Path) -> dict:
    return {"process_name": "bookforge", "target_dir": target_dir}


@when('executo "symforge init -p bookforge meu_projeto"')
def executo_init(escolho_processo: dict, ctx: dict):
    init_process(escolho_processo["process_name"], escolho_processo["target_dir"])
    ctx.update(escolho_processo)


@then("as pastas/arquivos requeridos são criados")
def estruturas_criadas(ctx: dict):
    target_dir: Path = ctx["target_dir"]
    for rel in REQUIRED_PATHS:
        assert (target_dir / rel).exists()


@then("o processo copiado fica pronto para uso no projeto")
def processo_pronto(ctx: dict):
    target_dir: Path = ctx["target_dir"]
    for rel in REQUIRED_PATHS:
        assert (target_dir / rel).read_text(encoding="utf-8")


@given("o projeto foi inicializado", target_fixture="projeto_inicializado")
def projeto_inicializado(target_dir: Path, ctx: dict) -> dict:
    init_process("bookforge", target_dir)
    ctx["target_dir"] = target_dir
    return ctx


def _read_process(ctx: dict) -> Path:
    target_dir = ctx.get("target_dir")
    if target_dir is None:
        raise AssertionError("target_dir não definido; inicialize o projeto ou configure o contexto.")
    return target_dir / "process" / "PROCESS.yml"


@when('executo "symforge validate process/PROCESS.yml"')
def executo_validate(ctx: dict, validator: ValidateUseCases):
    path = ctx.get("invalid_path") or _read_process(ctx)
    result = validator.validate_process(path, recursive=False)
    ctx["validation"] = result
    ctx["target_dir"] = ctx.get("target_dir")


@when('executo "symforge validate process/PROCESS.yml --recursive"')
def executo_validate_recursive(ctx: dict, validator: ValidateUseCases):
    path = ctx.get("invalid_path") or _read_process(ctx)
    result = validator.validate_process(path, recursive=True)
    ctx["validation"] = result
    ctx["target_dir"] = ctx.get("target_dir")


@then("a validação passa e lista fases/artefatos esperados")
def validacao_passou(ctx: dict):
    result = ctx["validation"]
    assert result.is_valid is True
    assert result.details.get("phases") is not None


@given("editei o PROCESS.yml removendo uma fase obrigatória", target_fixture="process_invalido")
def process_invalido(target_dir: Path, ctx: dict) -> dict:
    init_process("bookforge", target_dir)
    path = target_dir / "process" / "PROCESS.yml"
    path.write_text("", encoding="utf-8")
    ctx["target_dir"] = target_dir
    ctx["invalid_path"] = path
    return ctx


@then("recebo erro apontando o campo faltante e sugestão de correção")
def erro_schema(ctx: dict):
    result = ctx["validation"]
    assert result.is_valid is False
    assert result.errors
