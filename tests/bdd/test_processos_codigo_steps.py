import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from symforge.application.usecases.runtime import RuntimeUseCases
from symforge.domain.exceptions import StepNotFoundError
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


@pytest.fixture
def ctx() -> dict:
    return {}


@given("que existe um processo descrito em Markdown/YAML com artefatos obrigatórios")
@given("o arquivo passou por validação de schema")
def processo_validado(process_def: ProcessDefinition, workspace: Path, ctx: dict) -> dict:
    # cria artefato requerido
    (workspace / process_def.required_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (workspace / process_def.required_artifacts[0]).write_text("# ok", encoding="utf-8")
    ctx["process"] = process_def
    ctx["workspace"] = workspace
    return ctx


@when('executo "symforge start"')
def executo_start(runtime: RuntimeUseCases, ctx: dict):
    session = runtime.start(ctx["process"], ctx["workspace"])
    ctx["session"] = session


@then("vejo a sessão criada com o fluxo carregado")
def sessao_criada(ctx: dict):
    session = ctx["session"]
    assert session.state == SessionState.RUNNING


@then("a CLI lista os artefatos obrigatórios para o primeiro passo")
def lista_artefatos(ctx: dict):
    session = ctx["session"]
    assert session.required_artifacts


@given("que falta um artefato obrigatório para o passo atual")
def falta_artefato(process_def: ProcessDefinition, workspace: Path, ctx: dict) -> dict:
    # não cria o artefato, simulando falta
    ctx["process"] = process_def
    ctx["workspace"] = workspace
    artefato = workspace / process_def.required_artifacts[0]
    if artefato.exists():
        artefato.unlink()
    return ctx


@then("a sessão fica em AWAITING_INPUT com a lista do que falta")
def awaiting_input(runtime: RuntimeUseCases, ctx: dict):
    session = runtime.start(ctx["process"], ctx["workspace"])
    ctx["session"] = session
    assert session.state == SessionState.AWAITING_INPUT
    assert session.missing_artifacts == ctx["process"].required_artifacts


@then('a execução só prossegue após o artefato ser criado e "symforge resume" ser usado')
def resume_apos_criar(runtime: RuntimeUseCases, ctx: dict):
    session = runtime.start(ctx["process"], ctx["workspace"])
    # cria artefato e chama resume
    (ctx["workspace"] / session.missing_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (ctx["workspace"] / session.missing_artifacts[0]).write_text("# criado", encoding="utf-8")
    session = runtime.resume_after_input(session, ctx["workspace"])
    assert session.state == SessionState.RUNNING
    assert not session.missing_artifacts


@given("que a sessão avançou e registrou versionamento por passo")
def sessao_versionada(process_def: ProcessDefinition, workspace: Path, runtime: RuntimeUseCases, ctx: dict) -> dict:
    (workspace / process_def.required_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (workspace / process_def.required_artifacts[0]).write_text("# ok", encoding="utf-8")
    session = runtime.start(process_def, workspace)
    session.add_step("passo1")
    runtime.repo.update(session)
    ctx.update({"session": session, "workspace": workspace, "runtime": runtime})
    return ctx


@when('executo "symforge reset <passo>"')
def executo_reset(ctx: dict):
    runtime: RuntimeUseCases = ctx["runtime"]
    session = runtime.repo.load(ctx["session"].id)
    try:
        session = runtime.reset_step(session, "passo1")
        ctx["session"] = session
        ctx["error"] = None
    except StepNotFoundError as exc:
        ctx["error"] = exc


@then("o estado retorna ao passo anterior sem perder rastros")
def rollback_sucesso(ctx: dict):
    assert ctx.get("error") is None
    session = ctx["session"]
    assert session.state == SessionState.RUNNING
    assert "passo1" in session.history


@then("o histórico mantém o registro do reset")
def historico_reset(ctx: dict):
    session = ctx["session"]
    assert session.history  # reset mantém histórico até o passo solicitado


@given("que o passo solicitado para reset não possui versão registrada")
def passo_sem_versionamento(process_def: ProcessDefinition, workspace: Path, runtime: RuntimeUseCases, ctx: dict) -> dict:
    (workspace / process_def.required_artifacts[0]).parent.mkdir(parents=True, exist_ok=True)
    (workspace / process_def.required_artifacts[0]).write_text("# ok", encoding="utf-8")
    session = runtime.start(process_def, workspace)
    ctx.update({"session": session, "runtime": runtime})
    return ctx


@then("recebo uma mensagem de erro clara")
def erro_reset(ctx: dict):
    runtime: RuntimeUseCases = ctx["runtime"]
    session = ctx["session"]
    with pytest.raises(StepNotFoundError):
        runtime.reset_step(session, "passo-inexistente")


@then("a sessão permanece íntegra e continua no estado anterior")
def sessao_integra(ctx: dict):
    session = ctx["session"]
    assert session.state == SessionState.RUNNING
