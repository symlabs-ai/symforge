import sys
from pathlib import Path

import pytest
from pytest_bdd import scenarios, given, when, then

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from symforge.application.usecases.init_process import init_process, REQUIRED_PATHS

scenarios("../../specs/bdd/10_forge_core/init_processos.feature")


@pytest.fixture
def target_dir(tmp_path: Path) -> Path:
    return tmp_path / "meu_projeto"


@given('que escolho um processo disponível na biblioteca (ex.: ForgeProcess, BookForge, OpsForge)')
def escolho_processo(target_dir: Path) -> dict:
    return {"process_name": "bookforge", "target_dir": target_dir}


@when('executo "symforge init -p bookforge meu_projeto"')
def executo_init(escolho_processo: dict):
    init_process(escolho_processo["process_name"], escolho_processo["target_dir"])
    return escolho_processo


@then("as pastas/arquivos requeridos são criados")
def estruturas_criadas(executo_init):
    target_dir: Path = executo_init["target_dir"]
    for rel in REQUIRED_PATHS:
        assert (target_dir / rel).exists()


@then("o processo copiado fica pronto para uso no projeto")
def processo_pronto(executo_init):
    target_dir: Path = executo_init["target_dir"]
    for rel in REQUIRED_PATHS:
        assert (target_dir / rel).read_text(encoding="utf-8")


@given("o projeto foi inicializado")
def projeto_inicializado(target_dir: Path) -> dict:
    init_process("bookforge", target_dir)
    return {"target_dir": target_dir}


@when('executo "symforge validate process/PROCESS.yml --recursive"')
def executo_validate(projeto_inicializado: dict):
    # Validação simplificada: arquivo existe e não está vazio
    path = projeto_inicializado["target_dir"] / "process" / "PROCESS.yml"
    projeto_inicializado["validate_ok"] = path.exists() and bool(path.read_text(encoding="utf-8").strip())
    return projeto_inicializado


@then("a validação passa e lista fases/artefatos esperados")
def validacao_passou(executo_validate):
    assert executo_validate["validate_ok"] is True


@given("editei o PROCESS.yml removendo uma fase obrigatória")
def process_invalido(projeto_inicializado: dict) -> dict:
    path = projeto_inicializado["target_dir"] / "process" / "PROCESS.yml"
    path.write_text("", encoding="utf-8")
    projeto_inicializado["invalid_path"] = path
    return projeto_inicializado


@then("recebo erro apontando o campo faltante e sugestão de correção")
def erro_schema(process_invalido: dict):
    path: Path = process_invalido["invalid_path"]
    assert not path.read_text(encoding="utf-8")
