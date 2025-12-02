import sys
from pathlib import Path

import pytest
from pytest_bdd import scenarios, given, when, then

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from symforge.application.plugins.manager import PluginManager

scenarios("../../specs/bdd/30_plugins/plugins_no_code.feature")


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def plugin_manager(workspace: Path) -> PluginManager:
    return PluginManager(workspace / "plugins")


@pytest.fixture
def ctx() -> dict:
    return {}


def _write_plugin(repo: Path, manifest: str, code: str) -> Path:
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "plugin.yml").write_text(manifest, encoding="utf-8")
    (repo / "plugin.py").write_text(code, encoding="utf-8")
    return repo


@pytest.fixture
def plugin_repo_send(tmp_path: Path) -> Path:
    manifest = """\
id: send_email
name: Send Email
version: "0.1.0"
type: send
entrypoint: plugin:send_email
permissions:
  network: false
  fs: []
  env: []
inputs:
  payload: json
outputs:
  status: json
"""
    code = """\
def send_email(payload):
    return {"status": "sent", "to": payload.get("to")}
"""
    return _write_plugin(tmp_path / "repo_send", manifest, code)


@pytest.fixture
def plugin_repo_export(tmp_path: Path) -> Path:
    manifest = """\
id: export_csv
name: Export CSV
version: "0.1.0"
type: export
entrypoint: plugin:export_csv
permissions:
  network: false
  fs: []
  env: []
inputs:
  input_path: path
outputs:
  output_path: path
"""
    code = """\
def export_csv(input_path, output_path=None):
    # dummy conversion
    from pathlib import Path
    out = Path(output_path or str(input_path) + ".csv")
    out.write_text("col1\\nvalue", encoding="utf-8")
    return {"output_path": str(out)}
"""
    return _write_plugin(tmp_path / "repo_export", manifest, code)


@pytest.fixture
def plugin_repo_invalid(tmp_path: Path) -> Path:
    manifest = "id: invalid\n"  # faltam campos obrigatórios
    code = "def run():\n    return {}\n"
    return _write_plugin(tmp_path / "repo_invalid", manifest, code)


@given("tenho um processo em execução com artefatos gerados")
def processo_em_execucao(workspace: Path) -> dict:
    artefato = workspace / "artefato.md"
    artefato.write_text("# artefato", encoding="utf-8")
    return {"workspace": workspace, "artefato": artefato}


@when('adiciono o plugin "send_email" ao projeto')
def adiciono_plugin_send(plugin_manager: PluginManager, plugin_repo_send: Path, ctx: dict):
    plugin_manager.add_from_path(plugin_repo_send)
    ctx["manager"] = plugin_manager
    return ctx


@when('executo "symforge plugin list"')
def executo_plugin_list(ctx: dict):
    manager: PluginManager = ctx["manager"]
    ctx["plugins"] = manager.list_plugins()
    return ctx


@then('vejo o plugin instalado com tipo "send" e permissões declaradas')
def vejo_plugin_instalado(ctx: dict):
    plugins = ctx["plugins"]
    assert any(p["id"] == "send_email" and p["type"] == "send" for p in plugins)
    for p in plugins:
        if p["id"] == "send_email":
            assert "permissions" in p


@given('o plugin "send_email" está instalado')
@given("defini destinatário e assunto")
def plugin_email_configurado(plugin_manager: PluginManager, plugin_repo_send: Path) -> dict:
    plugin_manager.add_from_path(plugin_repo_send)
    return {"manager": plugin_manager, "payload": {"to": "user@example.com", "subject": "hi"}}


@when("executo o envio com o artefato atual")
def executo_envio(plugin_email_configurado: dict):
    manager: PluginManager = plugin_email_configurado["manager"]
    payload = plugin_email_configurado["payload"]
    result = manager.execute_send("send_email", payload)
    plugin_email_configurado["result"] = result
    return plugin_email_configurado


@then("o log registra sucesso e o destinatário recebe a mensagem")
def log_sucesso_envio(executo_envio: dict):
    result = executo_envio["result"]
    assert result.get("status") == "sent"
    assert result.get("to") == executo_envio["payload"]["to"]


@given('o plugin "export_csv" está instalado')
def plugin_export_instalado(plugin_manager: PluginManager, plugin_repo_export: Path, processo_em_execucao: dict) -> dict:
    plugin_manager.add_from_path(plugin_repo_export)
    return {"manager": plugin_manager, "artefato": processo_em_execucao["artefato"]}


@when("executo o export do artefato Markdown")
def executo_export(plugin_export_instalado: dict, workspace: Path):
    manager: PluginManager = plugin_export_instalado["manager"]
    artefato: Path = plugin_export_instalado["artefato"]
    out_path = workspace / "artefato.csv"
    result = manager.execute_export("export_csv", artefato, output_path=out_path)
    plugin_export_instalado["result"] = result
    plugin_export_instalado["output_path"] = out_path
    return plugin_export_instalado


@then("o arquivo CSV é gerado no path configurado")
def csv_gerado(executo_export: dict):
    out_path: Path = executo_export["output_path"]
    assert out_path.exists()


@then("a CLI confirma o sucesso")
def cli_confirma_sucesso(executo_export: dict):
    result = executo_export["result"]
    assert "output_path" in result


@given("um plugin não declara permissões ou tem manifesto incorreto")
def plugin_manifesto_invalido(plugin_repo_invalid: Path) -> dict:
    return {"repo": plugin_repo_invalid}


@when("tento instalá-lo")
def tento_instalar(plugin_manifesto_invalido: dict, plugin_manager: PluginManager):
    plugin_manifesto_invalido["manager"] = plugin_manager
    return plugin_manifesto_invalido


@then("o Symforge bloqueia a instalação com mensagem clara de erro")
def bloqueio_manifesto(plugin_manifesto_invalido: dict):
    manager: PluginManager = plugin_manifesto_invalido["manager"]
    with pytest.raises(ValueError):
        manager.add_from_path(plugin_manifesto_invalido["repo"])
