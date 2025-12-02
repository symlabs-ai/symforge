import pytest
from pytest_bdd import scenarios, given, when, then

pytestmark = pytest.mark.skip("BDD (init_processos) pendente de implementação")

scenarios("../../specs/bdd/10_forge_core/init_processos.feature")


@given('que escolho um processo disponível na biblioteca (ex.: ForgeProcess, BookForge, OpsForge)')
def escolho_processo():
    pytest.skip("Aguardando implementação (TDD)")


@when('executo "symforge init -p bookforge meu_projeto"')
def executo_init():
    pytest.skip("Aguardando implementação (TDD)")


@then("as pastas/arquivos requeridos são criados")
def estruturas_criadas():
    pytest.skip("Aguardando implementação (TDD)")


@then("o processo copiado fica pronto para uso no projeto")
def processo_pronto():
    pytest.skip("Aguardando implementação (TDD)")


@given("o projeto foi inicializado")
def projeto_inicializado():
    pytest.skip("Aguardando implementação (TDD)")


@when('executo "symforge validate process/PROCESS.yml --recursive"')
def executo_validate():
    pytest.skip("Aguardando implementação (TDD)")


@then("a validação passa e lista fases/artefatos esperados")
def validacao_passou():
    pytest.skip("Aguardando implementação (TDD)")


@given("editei o PROCESS.yml removendo uma fase obrigatória")
def process_invalido():
    pytest.skip("Aguardando implementação (TDD)")


@then("recebo erro apontando o campo faltante e sugestão de correção")
def erro_schema():
    pytest.skip("Aguardando implementação (TDD)")
