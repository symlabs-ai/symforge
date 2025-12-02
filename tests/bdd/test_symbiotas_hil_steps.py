import pytest
from pytest_bdd import scenarios, given, when, then

pytestmark = pytest.mark.skip("BDD (symbiotas_hil) pendente de implementação")

scenarios("../../specs/bdd/10_forge_core/symbiotas_hil.feature")


@given("há um passo marcado como HIL no processo")
@given("o symbiota responsável está configurado")
def passo_hil_configurado():
    pytest.skip("Aguardando implementação (TDD)")


@when("o symbiota apresenta a pergunta do checkpoint")
def pergunta_checkpoint():
    pytest.skip("Aguardando implementação (TDD)")


@when('eu respondo com uma decisão via "symforge decide"')
def respondo_decisao():
    pytest.skip("Aguardando implementação (TDD)")


@then("a sessão sai de AWAITING_DECISION")
def sai_de_awaiting_decision():
    pytest.skip("Aguardando implementação (TDD)")


@then("o fluxo prossegue para o próximo passo")
def fluxo_prossegue():
    pytest.skip("Aguardando implementação (TDD)")


@then("a decisão fica registrada com ator e timestamp")
def decisao_registrada():
    pytest.skip("Aguardando implementação (TDD)")


@given("o symbiota não consegue processar o prompt ou provider falha")
def symbiota_falha():
    pytest.skip("Aguardando implementação (TDD)")


@when("executo o passo marcado como HIL")
def executo_passo_hil():
    pytest.skip("Aguardando implementação (TDD)")


@then("recebo mensagem de fallback para intervenção humana")
def fallback_mensagem():
    pytest.skip("Aguardando implementação (TDD)")


@then("posso registrar manualmente a decisão para seguir o fluxo")
def registrar_manual():
    pytest.skip("Aguardando implementação (TDD)")
