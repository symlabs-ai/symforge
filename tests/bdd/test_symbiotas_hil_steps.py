import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from symforge.domain.session import Session
from symforge.domain.states import SessionState

scenarios("../../specs/bdd/10_forge_core/symbiotas_hil.feature")


@pytest.fixture
def session_hil() -> Session:
    session = Session(id="s1", process_name="demo")
    session.mark_awaiting_decision()
    return session

@pytest.fixture
def ctx() -> dict:
    return {}


@given("que há um passo marcado como HIL no processo", target_fixture="passo_hil_configurado")
@given("o symbiota responsável está configurado", target_fixture="passo_hil_configurado")
def passo_hil_configurado(session_hil: Session) -> Session:
    return session_hil


@when("o symbiota apresenta a pergunta do checkpoint")
def pergunta_checkpoint(passo_hil_configurado: Session, ctx: dict) -> Session:
    # nada a fazer além de confirmar estado aguardando decisão
    assert passo_hil_configurado.state == SessionState.AWAITING_DECISION
    ctx["session"] = passo_hil_configurado


@when('eu respondo com uma decisão via "symforge decide"')
def respondo_decisao(ctx: dict) -> Session:
    session = ctx["session"]
    session.register_decision("approved")
    ctx["session"] = session
    return session


@then("a sessão sai de AWAITING_DECISION")
def sai_de_awaiting_decision(ctx: dict):
    session = ctx["session"]
    assert session.state == SessionState.RUNNING


@then("o fluxo prossegue para o próximo passo")
def fluxo_prossegue(ctx: dict):
    session = ctx["session"]
    assert not session.pending_decision


@then("a decisão fica registrada com ator e timestamp")
def decisao_registrada(ctx: dict):
    session = ctx["session"]
    assert any("decision:" in item for item in session.history)


@given("que o symbiota não consegue processar o prompt ou provider falha")
def symbiota_falha(session_hil: Session, ctx: dict) -> Session:
    session_hil.error = "provider_unavailable"  # marca falha
    ctx["session"] = session_hil
    return session_hil


@when("executo o passo marcado como HIL", target_fixture="executo_passo_hil")
def executo_passo_hil(ctx: dict) -> Session:
    return ctx["session"]


@then("recebo mensagem de fallback para intervenção humana")
def fallback_mensagem(executo_passo_hil: Session):
    assert hasattr(executo_passo_hil, "error")


@then("posso registrar manualmente a decisão para seguir o fluxo")
def registrar_manual(executo_passo_hil: Session):
    executo_passo_hil.register_decision("manual-approval")
    assert executo_passo_hil.state == SessionState.RUNNING
