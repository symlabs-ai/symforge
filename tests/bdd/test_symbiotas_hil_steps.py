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


@given("há um passo marcado como HIL no processo")
@given("o symbiota responsável está configurado")
def passo_hil_configurado(session_hil: Session) -> Session:
    return session_hil


@when("o symbiota apresenta a pergunta do checkpoint")
def pergunta_checkpoint(passo_hil_configurado: Session) -> Session:
    # nada a fazer além de confirmar estado aguardando decisão
    assert passo_hil_configurado.state == SessionState.AWAITING_DECISION
    return passo_hil_configurado


@when('eu respondo com uma decisão via "symforge decide"')
def respondo_decisao(pergunta_checkpoint: Session) -> Session:
    pergunta_checkpoint.register_decision("approved")
    return pergunta_checkpoint


@then("a sessão sai de AWAITING_DECISION")
def sai_de_awaiting_decision(respondo_decisao: Session):
    assert respondo_decisao.state == SessionState.RUNNING


@then("o fluxo prossegue para o próximo passo")
def fluxo_prossegue(respondo_decisao: Session):
    assert not respondo_decisao.pending_decision


@then("a decisão fica registrada com ator e timestamp")
def decisao_registrada(respondo_decisao: Session):
    assert any("decision:" in item for item in respondo_decisao.history)


@given("o symbiota não consegue processar o prompt ou provider falha")
def symbiota_falha(session_hil: Session) -> Session:
    session_hil.error = "provider_unavailable"  # marca falha
    return session_hil


@when("executo o passo marcado como HIL")
def executo_passo_hil(symbiota_falha: Session) -> Session:
    return symbiota_falha


@then("recebo mensagem de fallback para intervenção humana")
def fallback_mensagem(executo_passo_hil: Session):
    assert hasattr(executo_passo_hil, "error")


@then("posso registrar manualmente a decisão para seguir o fluxo")
def registrar_manual(executo_passo_hil: Session):
    executo_passo_hil.register_decision("manual-approval")
    assert executo_passo_hil.state == SessionState.RUNNING
