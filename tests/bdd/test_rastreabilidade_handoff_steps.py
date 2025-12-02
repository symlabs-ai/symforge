import pytest
from pytest_bdd import scenarios, given, when, then

pytestmark = pytest.mark.skip("BDD (rastreabilidade_handoff) pendente de implementação")

scenarios("../../specs/bdd/50_observabilidade/rastreabilidade_handoff.feature")


@given("existe uma sessão em execução com decisões e notas registradas")
def sessao_com_registros():
    pytest.skip("Aguardando implementação (TDD)")


@when('executo "symforge diagram process/PROCESS.yml -t flowchart"')
def executo_diagram():
    pytest.skip("Aguardando implementação (TDD)")


@then("é gerado um diagrama Mermaid sem divergências de nós ou artefatos")
def diagrama_ok():
    pytest.skip("Aguardando implementação (TDD)")


@then("a saída é salva no path configurado")
def diagrama_salvo():
    pytest.skip("Aguardando implementação (TDD)")


@when('executo "symforge handoff"')
def executo_handoff():
    pytest.skip("Aguardando implementação (TDD)")


@then("o handoff contém estado atual, decisões, notas e próximos passos")
def handoff_completo():
    pytest.skip("Aguardando implementação (TDD)")


@then("o arquivo é salvo no diretório de saída configurado")
def handoff_salvo():
    pytest.skip("Aguardando implementação (TDD)")


@given("o PROCESS contém um nó inválido")
def process_invalido():
    pytest.skip("Aguardando implementação (TDD)")


@when("executo o comando de diagrama")
def comando_diagrama():
    pytest.skip("Aguardando implementação (TDD)")


@then("recebo erro apontando o nó divergente")
def erro_no_divergente():
    pytest.skip("Aguardando implementação (TDD)")


@then("o diagrama não é gerado até corrigir o processo")
def diagrama_bloqueado():
    pytest.skip("Aguardando implementação (TDD)")
