import pytest
from pytest_bdd import scenarios, given, when, then

pytestmark = pytest.mark.skip("BDD (plugins_no_code) pendente de implementação")

scenarios("../../specs/bdd/30_plugins/plugins_no_code.feature")


@given("tenho um processo em execução com artefatos gerados")
def processo_em_execucao():
    pytest.skip("Aguardando implementação (TDD)")


@when('adiciono o plugin "send_email" ao projeto')
def adiciono_plugin_send():
    pytest.skip("Aguardando implementação (TDD)")


@when('executo "symforge plugin list"')
def executo_plugin_list():
    pytest.skip("Aguardando implementação (TDD)")


@then('vejo o plugin instalado com tipo "send" e permissões declaradas')
def vejo_plugin_instalado():
    pytest.skip("Aguardando implementação (TDD)")


@given('o plugin "send_email" está instalado')
@given("defini destinatário e assunto")
def plugin_email_configurado():
    pytest.skip("Aguardando implementação (TDD)")


@when("executo o envio com o artefato atual")
def executo_envio():
    pytest.skip("Aguardando implementação (TDD)")


@then("o log registra sucesso e o destinatário recebe a mensagem")
def log_sucesso_envio():
    pytest.skip("Aguardando implementação (TDD)")


@given('o plugin "export_csv" está instalado')
def plugin_export_instalado():
    pytest.skip("Aguardando implementação (TDD)")


@when("executo o export do artefato Markdown")
def executo_export():
    pytest.skip("Aguardando implementação (TDD)")


@then("o arquivo CSV é gerado no path configurado")
def csv_gerado():
    pytest.skip("Aguardando implementação (TDD)")


@then("a CLI confirma o sucesso")
def cli_confirma_sucesso():
    pytest.skip("Aguardando implementação (TDD)")


@given("um plugin não declara permissões ou tem manifesto incorreto")
def plugin_manifesto_invalido():
    pytest.skip("Aguardando implementação (TDD)")


@when("tento instalá-lo")
def tento_instalar():
    pytest.skip("Aguardando implementação (TDD)")


@then("o Symforge bloqueia a instalação com mensagem clara de erro")
def bloqueio_manifesto():
    pytest.skip("Aguardando implementação (TDD)")
