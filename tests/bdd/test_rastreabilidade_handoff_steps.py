import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from symforge.application.usecases.observability import ObservabilityUseCases
from symforge.domain.session import Session
from symforge.domain.states import SessionState

scenarios("../../specs/bdd/50_observabilidade/rastreabilidade_handoff.feature")


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def process_file(workspace: Path) -> Path:
    path = workspace / "process" / "PROCESS.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "nodes:\n"
        "  - id: start\n"
        "    type: start\n"
        "  - id: end\n"
        "    type: end\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def session_with_notes() -> Session:
    s = Session(id="s1", process_name="demo", state=SessionState.RUNNING)
    s.history.append("step1")
    s.history.append("decision:approved")
    return s


@pytest.fixture
def observability(workspace: Path) -> ObservabilityUseCases:
    return ObservabilityUseCases(workspace)


@given("que existe uma sessão em execução com decisões e notas registradas", target_fixture="sessao_com_registros")
def sessao_com_registros(session_with_notes: Session, process_file: Path, observability: ObservabilityUseCases):
    return {"session": session_with_notes, "process_file": process_file, "obs": observability}


@when('executo "symforge diagram process/PROCESS.yml -t flowchart"', target_fixture="executo_diagram")
def executo_diagram(sessao_com_registros: dict, workspace: Path):
    obs: ObservabilityUseCases = sessao_com_registros["obs"]
    process_file: Path = sessao_com_registros["process_file"]
    out = workspace / "diagram.md"
    obs.generate_diagram(process_file, out)
    sessao_com_registros["diagram_path"] = out
    return sessao_com_registros


@then("é gerado um diagrama Mermaid sem divergências de nós ou artefatos")
def diagrama_ok(executo_diagram: dict):
    diag = executo_diagram["diagram_path"]
    content = diag.read_text(encoding="utf-8")
    assert "flowchart" in content


@then("a saída é salva no path configurado")
def diagrama_salvo(executo_diagram: dict):
    assert executo_diagram["diagram_path"].exists()


@when('executo "symforge handoff"', target_fixture="executo_handoff")
def executo_handoff(sessao_com_registros: dict, workspace: Path):
    obs: ObservabilityUseCases = sessao_com_registros["obs"]
    session: Session = sessao_com_registros["session"]
    out = workspace / "handoff.md"
    obs.export_handoff(session, out)
    sessao_com_registros["handoff_path"] = out
    return sessao_com_registros


@then("o handoff contém estado atual, decisões, notas e próximos passos")
def handoff_completo(executo_handoff: dict):
    content = executo_handoff["handoff_path"].read_text(encoding="utf-8")
    assert "estado" in content.lower()
    assert "decision" in content.lower() or "decisão" in content.lower()


@then("o arquivo é salvo no diretório de saída configurado")
def handoff_salvo(executo_handoff: dict):
    assert executo_handoff["handoff_path"].exists()


@given("que o PROCESS contém um nó inválido", target_fixture="process_invalido")
def process_invalido(workspace: Path, observability: ObservabilityUseCases) -> dict:
    path = workspace / "process" / "PROCESS.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    # nó sem tipo
    path.write_text("nodes:\n  - id: start\n", encoding="utf-8")
    return {"process_file": path, "obs": observability}


@when("executo o comando de diagrama", target_fixture="comando_diagrama")
def comando_diagrama(process_invalido: dict, workspace: Path):
    obs: ObservabilityUseCases = process_invalido["obs"]
    process_file: Path = process_invalido["process_file"]
    out = workspace / "diagram_invalid.md"
    process_invalido["diagram_path"] = out
    try:
        obs.generate_diagram(process_file, out)
        process_invalido["error"] = None
    except Exception as exc:  # noqa: BLE001
        process_invalido["error"] = exc
    return process_invalido


@then("recebo erro apontando o nó divergente")
def erro_no_divergente(comando_diagrama: dict):
    assert comando_diagrama["error"] is not None


@then("o diagrama não é gerado até corrigir o processo")
def diagrama_bloqueado(comando_diagrama: dict):
    diag = comando_diagrama["diagram_path"]
    assert not diag.exists()
