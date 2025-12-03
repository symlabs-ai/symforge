import argparse
import json
import sys
from pathlib import Path

from symforge.adapters.cli.plugins_cli import PluginsCLI
from symforge.adapters.cli.runtime_cli import RuntimeCLI
from symforge.application.usecases.init_process import init_process
from symforge.application.usecases.validation import ValidateUseCases


def _workspace(path_str: str | None) -> Path:
    return Path(path_str).resolve() if path_str else Path.cwd()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="symforge")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Inicializa estrutura de processo")
    init_cmd.add_argument("-p", "--process", required=True, help="Nome do processo base")
    init_cmd.add_argument("target", help="Diretório de destino")

    validate_cmd = sub.add_parser("validate", help="Valida PROCESS.yml")
    validate_cmd.add_argument("process_path", help="Caminho para PROCESS.yml")
    validate_cmd.add_argument("--recursive", action="store_true", help="Validar artefatos referenciados")

    start_cmd = sub.add_parser("start", help="Inicia sessão de processo")
    start_cmd.add_argument("--process", required=True, help="Nome do processo")
    start_cmd.add_argument("--required", nargs="*", default=[], help="Artefatos obrigatórios")
    start_cmd.add_argument("--workspace", help="Diretório de trabalho (default: cwd)")
    start_cmd.add_argument("--auto-commit", action="store_true", help="Auto-commit Git por step")

    resume_cmd = sub.add_parser("resume", help="Retoma sessão aguardando input")
    resume_cmd.add_argument("session_id")
    resume_cmd.add_argument("--workspace", help="Diretório de trabalho (default: cwd)")
    resume_cmd.add_argument("--auto-commit", action="store_true", help="Auto-commit Git por step")

    reset_cmd = sub.add_parser("reset", help="Reseta sessão para passo anterior")
    reset_cmd.add_argument("session_id")
    reset_cmd.add_argument("step_id")
    reset_cmd.add_argument("--workspace", help="Diretório de trabalho (default: cwd)")
    reset_cmd.add_argument("--auto-commit", action="store_true", help="Auto-commit Git por step")

    decide_cmd = sub.add_parser("decide", help="Registra decisão HIL")
    decide_cmd.add_argument("session_id")
    decide_cmd.add_argument("decision", help="Decisão a registrar")
    decide_cmd.add_argument("--workspace", help="Diretório de trabalho (default: cwd)")
    decide_cmd.add_argument("--auto-commit", action="store_true", help="Auto-commit Git por step")

    status_cmd = sub.add_parser("status", help="Exibe status da sessão")
    status_cmd.add_argument("session_id")
    status_cmd.add_argument("--workspace", help="Diretório de trabalho (default: cwd)")

    pause_cmd = sub.add_parser("pause", help="Pausa sessão e gera handoff")
    pause_cmd.add_argument("session_id")
    pause_cmd.add_argument("--workspace", help="Diretório de trabalho (default: cwd)")

    complete_cmd = sub.add_parser("complete", help="Completa sessão e gera handoff final")
    complete_cmd.add_argument("session_id")
    complete_cmd.add_argument("--workspace", help="Diretório de trabalho (default: cwd)")

    plugin_cmd = sub.add_parser("plugin", help="Gerencia plugins")
    plugin_sub = plugin_cmd.add_subparsers(dest="plugin_command", required=True)
    plugin_add = plugin_sub.add_parser("add")
    plugin_add.add_argument("repo_path")
    plugin_sub.add_parser("list")
    plugin_send = plugin_sub.add_parser("send")
    plugin_send.add_argument("plugin_id")
    plugin_send.add_argument("payload_json")
    plugin_export = plugin_sub.add_parser("export")
    plugin_export.add_argument("plugin_id")
    plugin_export.add_argument("input_path")
    plugin_export.add_argument("--output")
    plugin_hook = plugin_sub.add_parser("hook")
    plugin_hook.add_argument("plugin_id")
    plugin_hook.add_argument("context_json")
    plugin_gen = plugin_sub.add_parser("generate")
    plugin_gen.add_argument("plugin_id")
    plugin_gen.add_argument("payload_json")

    args = parser.parse_args(argv)

    if args.command == "init":
        target = Path(args.target).resolve()
        init_process(args.process, target)
        print(f"[symforge] init concluído em {target}")
        return 0

    if args.command == "validate":
        validator = ValidateUseCases()
        process_path = Path(args.process_path).resolve()
        result = validator.validate_process(process_path, recursive=args.recursive)
        if result.is_valid:
            phases = result.details.get("phases", [])
            print(f"[symforge] PROCESS.yml ok | fases: {len(phases)}")
            return 0
        print(f"[symforge] validação falhou: {', '.join(result.errors)}", file=sys.stderr)
        return 1

    if args.command in {"start", "resume", "reset", "decide", "status", "pause", "complete"}:
        workspace = _workspace(getattr(args, "workspace", None))
        auto_commit = getattr(args, "auto_commit", False)
        runtime_cli = RuntimeCLI(workspace, auto_commit=auto_commit)
        if args.command == "start":
            session_id = runtime_cli.start(args.process, args.required)
            print(session_id)
            return 0
        if args.command == "resume":
            state = runtime_cli.resume(args.session_id)
            print(state)
            return 0
        if args.command == "reset":
            state = runtime_cli.reset(args.session_id, args.step_id)
            print(state)
            return 0
        if args.command == "decide":
            state = runtime_cli.decide(args.session_id, args.decision)
            print(state)
            return 0
        if args.command == "status":
            status = runtime_cli.status(args.session_id)
            print(json.dumps(status, indent=2))
            return 0
        if args.command == "pause":
            handoff_path = runtime_cli.pause(args.session_id)
            print(f"[symforge] sessão pausada | handoff: {handoff_path}")
            return 0
        if args.command == "complete":
            handoff_path = runtime_cli.complete(args.session_id)
            print(f"[symforge] sessão concluída | handoff: {handoff_path}")
            return 0

    if args.command == "plugin":
        workspace = Path.cwd()
        manager = PluginsCLI(workspace)
        if args.plugin_command == "add":
            manager.add(Path(args.repo_path).resolve())
            print("[symforge] plugin instalado")
            return 0
        if args.plugin_command == "list":
            plugins = manager.list()
            print(json.dumps(plugins, indent=2))
            return 0
        if args.plugin_command == "send":
            payload = json.loads(args.payload_json)
            result = manager.send(args.plugin_id, payload)
            print(json.dumps(result))
            return 0
        if args.plugin_command == "export":
            input_path = Path(args.input_path).resolve()
            output_path = Path(args.output).resolve() if args.output else None
            result = manager.export(args.plugin_id, input_path, output_path)
            print(json.dumps(result))
            return 0
        if args.plugin_command == "hook":
            ctx = json.loads(args.context_json)
            result = manager.hook(args.plugin_id, ctx)
            print(json.dumps(result))
            return 0
        if args.plugin_command == "generate":
            payload = json.loads(args.payload_json)
            result = manager.generate(args.plugin_id, payload)
            print(json.dumps(result))
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
