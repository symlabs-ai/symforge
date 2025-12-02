import pytest
from pytest_bdd import scenarios, given, when, then

pytestmark = pytest.mark.skip("BDD (processos_codigo) pendente de implementação")

scenarios("../../specs/bdd/10_forge_core/processos_codigo.feature")


@given("que existe um processo descrito em Markdown/YAML com artefatos obrigatórios")
@given("o arquivo passou por validação de schema")
def processo_validado():
    pytest.skip("Aguardando implementação (TDD)")


@when('executo "symforge start"')
def executo_start():
    pytest.skip("Aguardando implementação (TDD)")


@then("vejo a sessão criada com o fluxo carregado")
def sessao_criada():
    pytest.skip("Aguardando implementação (TDD)")


@then("a CLI lista os artefatos obrigatórios para o primeiro passo")
def lista_artefatos():
    pytest.skip("Aguardando implementação (TDD)")


@given("que falta um artefato obrigatório para o passo atual")
def falta_artefato():
    pytest.skip("Aguardando implementação (TDD)")


@then("a sessão fica em AWAITING_INPUT com a lista do que falta")
def awaiting_input():
    pytest.skip("Aguardando implementação (TDD)")


@then('a execução só prossegue após o artefato ser criado e "symforge resume" ser usado')
def resume_apos_criar():
    pytest.skip("Aguardando implementação (TDD)")


@given("que a sessão avançou e registrou versionamento por passo")
def sessao_versionada():
    pytest.skip("Aguardando implementação (TDD)")


@when('executo "symforge reset <passo>"')
def executo_reset():
    pytest.skip("Aguardando implementação (TDD)")


@then("o estado retorna ao passo anterior sem perder rastros")
def rollback_sucesso():
    pytest.skip("Aguardando implementação (TDD)")


@then("o histórico mantém o registro do reset")
def historico_reset():
    pytest.skip("Aguardando implementação (TDD)")


@given("que o passo solicitado para reset não possui versão registrada")
def passo_sem_versionamento():
    pytest.skip("Aguardando implementação (TDD)")


@then("recebo uma mensagem de erro clara")
def erro_reset():
    pytest.skip("Aguardando implementação (TDD)")


@then("a sessão permanece íntegra e continua no estado anterior")
def sessao_integra():
    pytest.skip("Aguardando implementação (TDD)")
