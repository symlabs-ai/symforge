import sys
from pathlib import Path

import pytest
from pytest_bdd import scenarios, given, when, then

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from symforge.application.usecases.runtime import RuntimeUseCases
from symforge.domain.process_definition import ProcessDefinition
from symforge.domain.states import SessionState

scenarios("../../specs/bdd/10_forge_core/processos_codigo.feature")


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def process_def() -> ProcessDefinition:
    return ProcessDefinition(name="demo", required_artifacts=["artefato.md"])


@pytest.fixture
def runtime(workspace: Path) -> RuntimeUseCases:
    return RuntimeUseCases(workspace / ".symforge" / "sessions")


@given("que existe um processo descrito em Markdown/YAML com artefatos obrigatórios")
@given("o arquivo passou por validação de schema")
def processo_validado(process_def: ProcessDefinition, workspace: Path) -> dict:
    # cria artefato requerido
    (workspace / process_def.required_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (workspace / process_def.required_artifacts[0]).write_text("# ok", encoding="utf-8")
    return {"process": process_def, "workspace": workspace}


@when('executo "symforge start"')
def executo_start(runtime: RuntimeUseCases, processo_validado: dict):
    ctx = processo_validado
    session = runtime.start(ctx["process"], ctx["workspace"])
    ctx["session"] = session
    return ctx


@then("vejo a sessão criada com o fluxo carregado")
def sessao_criada(executo_start):
    session = executo_start["session"]
    assert session.state == SessionState.RUNNING


@then("a CLI lista os artefatos obrigatórios para o primeiro passo")
def lista_artefatos(executo_start):
    session = executo_start["session"]
    assert session.required_artifacts


@given("que falta um artefato obrigatório para o passo atual")
def falta_artefato(process_def: ProcessDefinition, workspace: Path) -> dict:
    # não cria o artefato, simulando falta
    return {"process": process_def, "workspace": workspace}


@then("a sessão fica em AWAITING_INPUT com a lista do que falta")
def awaiting_input(runtime: RuntimeUseCases, falta_artefato):
    session = runtime.start(falta_artefato["process"], falta_artefato["workspace"])
    assert session.state == SessionState.AWAITING_INPUT
    assert session.missing_artifacts == falta_artefato["process"].required_artifacts


@then('a execução só prossegue após o artefato ser criado e "symforge resume" ser usado')
def resume_apos_criar(runtime: RuntimeUseCases, falta_artefato):
    session = runtime.start(falta_artefato["process"], falta_artefato["workspace"])
    # cria artefato e chama resume
    (falta_artefato["workspace"] / session.missing_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (falta_artefato["workspace"] / session.missing_artifacts[0]).write_text("# criado", encoding="utf-8")
    session = runtime.resume_after_input(session, falta_artefato["workspace"])
    assert session.state == SessionState.RUNNING
    assert not session.missing_artifacts


@given("que a sessão avançou e registrou versionamento por passo")
def sessao_versionada(process_def: ProcessDefinition, workspace: Path, runtime: RuntimeUseCases) -> dict:
    (workspace / process_def.required_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (workspace / process_def.required_artifacts[0]).write_text("# ok", encoding="utf-8")
    session = runtime.start(process_def, workspace)
    session.add_step("passo1")
    runtime.repo.update(session)
    return {"session": session, "workspace": workspace, "runtime": runtime}


@when('executo "symforge reset <passo>"')
def executo_reset(sessao_versionada: dict):
    runtime: RuntimeUseCases = sessao_versionada["runtime"]
    session = runtime.repo.load(sessao_versionada["session"].id)
    session = runtime.reset_step(session, "passo1")
    sessao_versionada["session"] = session
    return sessao_versionada


@then("o estado retorna ao passo anterior sem perder rastros")
def rollback_sucesso(executo_reset):
    session = executo_reset["session"]
    assert session.state == SessionState.RUNNING
    assert "passo1" in session.history


@then("o histórico mantém o registro do reset")
def historico_reset(executo_reset):
    session = executo_reset["session"]
    assert session.history  # reset mantém histórico até o passo solicitado


@given("que o passo solicitado para reset não possui versão registrada")
def passo_sem_versionamento(process_def: ProcessDefinition, workspace: Path, runtime: RuntimeUseCases) -> dict:
    (workspace / process_def.required_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (workspace / process_def.required_artifacts[0]).write_text("# ok", encoding="utf-8")
    session = runtime.start(process_def, workspace)
    return {"session": session, "runtime": runtime}


@then("recebo uma mensagem de erro clara")
def erro_reset(passo_sem_versionamento):
    runtime: RuntimeUseCases = passo_sem_versionamento["runtime"]
    session = passo_sem_versionamento["session"]
    with pytest.raises(ValueError):
        runtime.reset_step(session, "passo-inexistente")


@then("a sessão permanece íntegra e continua no estado anterior")
def sessao_integra(passo_sem_versionamento):
    session = passo_sem_versionamento["session"]
    assert session.state == SessionState.RUNNING
