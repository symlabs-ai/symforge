import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

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


@pytest.fixture
def plugin_repo_hook(tmp_path: Path) -> Path:
    manifest = """\
id: hook_logger
name: Hook Logger
version: "0.1.0"
type: hook
entrypoint: plugin:on_event
permissions:
  network: false
  fs: []
  env: []
inputs:
  context: json
outputs:
  status: json
"""
    code = """\
def on_event(context):
    return {"status": "logged", "event": context.get("event")}
"""
    return _write_plugin(tmp_path / "repo_hook", manifest, code)


@pytest.fixture
def plugin_repo_generate(tmp_path: Path) -> Path:
    manifest = """\
id: generate_text
name: Generate Text
version: "0.1.0"
type: generate
entrypoint: plugin:generate
permissions:
  network: false
  fs: []
  env: []
inputs:
  payload: json
outputs:
  content: text
"""
    code = """\
def generate(payload):
    return {"content": f"hello {payload.get('name', 'user')}"}
"""
    return _write_plugin(tmp_path / "repo_generate", manifest, code)


@pytest.fixture
def plugin_repo_network(tmp_path: Path) -> Path:
    manifest = """\
id: network_plugin
name: Network Plugin
version: "0.1.0"
type: send
entrypoint: plugin:run
permissions:
  network: true
  fs: []
  env: []
"""
    code = """\
def run(payload):
    return {"status": "ok"}
"""
    return _write_plugin(tmp_path / "repo_network", manifest, code)


@given("que tenho um processo em execução com artefatos gerados", target_fixture="processo_em_execucao")
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


@given('que o plugin "send_email" está instalado', target_fixture="plugin_email_configurado")
@given("defini destinatário e assunto", target_fixture="plugin_email_configurado")
def plugin_email_configurado(plugin_manager: PluginManager, plugin_repo_send: Path) -> dict:
    plugin_manager.add_from_path(plugin_repo_send)
    return {"manager": plugin_manager, "payload": {"to": "user@example.com", "subject": "hi"}}


@when("executo o envio com o artefato atual", target_fixture="executo_envio")
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


@given('que o plugin "export_csv" está instalado', target_fixture="plugin_export_instalado")
def plugin_export_instalado(plugin_manager: PluginManager, plugin_repo_export: Path, processo_em_execucao: dict) -> dict:
    plugin_manager.add_from_path(plugin_repo_export)
    return {"manager": plugin_manager, "artefato": processo_em_execucao["artefato"]}


@when("executo o export do artefato Markdown", target_fixture="executo_export")
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


@given("que um plugin não declara permissões ou tem manifesto incorreto", target_fixture="plugin_manifesto_invalido")
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


@given('que o plugin "hook_logger" está instalado', target_fixture="plugin_hook_instalado")
def plugin_hook_instalado(plugin_manager: PluginManager, plugin_repo_hook: Path) -> dict:
    plugin_manager.add_from_path(plugin_repo_hook)
    return {"manager": plugin_manager}


@when("executo o hook com contexto do passo", target_fixture="executo_hook")
def executo_hook(plugin_hook_instalado: dict):
    manager: PluginManager = plugin_hook_instalado["manager"]
    result = manager.execute_hook("hook_logger", {"event": "step_completed"})
    plugin_hook_instalado["result"] = result
    return plugin_hook_instalado


@then("o hook registra o evento com sucesso")
def hook_registrado(executo_hook: dict):
    result = executo_hook["result"]
    assert result.get("status") == "logged"
    assert result.get("event") == "step_completed"


@given('que o plugin "generate_text" está instalado', target_fixture="plugin_generate_instalado")
def plugin_generate_instalado(plugin_manager: PluginManager, plugin_repo_generate: Path) -> dict:
    plugin_manager.add_from_path(plugin_repo_generate)
    return {"manager": plugin_manager, "payload": {"name": "Symforge"}}


@when("executo a geração com payload", target_fixture="executo_generate")
def executo_generate(plugin_generate_instalado: dict):
    manager: PluginManager = plugin_generate_instalado["manager"]
    payload = plugin_generate_instalado["payload"]
    result = manager.execute_generate("generate_text", payload)
    plugin_generate_instalado["result"] = result
    return plugin_generate_instalado


@then("o plugin retorna o conteúdo gerado")
def conteudo_gerado(executo_generate: dict):
    result = executo_generate["result"]
    assert "content" in result
    assert "Symforge" in result["content"]


@given("que um plugin solicita acesso de rede", target_fixture="plugin_rede")
def plugin_rede(plugin_repo_network: Path, plugin_manager: PluginManager) -> dict:
    return {"repo": plugin_repo_network, "manager": plugin_manager}


@when("tento instalá-lo em modo offline")
def instalo_plugin_rede(plugin_rede: dict):
    plugin_rede["error"] = None
    try:
        plugin_rede["manager"].add_from_path(plugin_rede["repo"])
    except ValueError as exc:
        plugin_rede["error"] = exc
    return plugin_rede


@then("o Symforge bloqueia o plugin por requerer rede")
def bloqueia_rede(plugin_rede: dict):
    assert plugin_rede["error"] is not None
