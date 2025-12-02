from pathlib import Path

REQUIRED_PATHS = [
    Path("process/PROCESS.yml"),
]


def init_process(process_name: str, target_dir: Path) -> None:
    """
    Inicializa estrutura básica para um processo (técnico ou não técnico).
    Cria pastas/arquivos requeridos mínimos.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    for rel in REQUIRED_PATHS:
        full = target_dir / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        if not full.exists():
            full.write_text(f"# PROCESS for {process_name}\n", encoding="utf-8")
