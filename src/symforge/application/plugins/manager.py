import importlib.util
import shutil
from pathlib import Path
from typing import Any

import yaml


class PluginManager:
    """
    Gerencia plugins no-code (send/export/hook/generate) instalados localmente.
    Instala a partir de um repositório (pasta) com plugin.yml e plugin.py,
    valida manifesto e carrega entrypoints de forma offline.
    """

    ALLOWED_TYPES = {"send", "export", "hook", "generate"}

    def __init__(self, plugins_root: Path):
        self.plugins_root = plugins_root
        self.plugins_root.mkdir(parents=True, exist_ok=True)

    def add_from_path(self, repo_path: Path) -> None:
        manifest_path = repo_path / "plugin.yml"
        code_path = repo_path / "plugin.py"
        if not manifest_path.exists() or not code_path.exists():
            raise ValueError("Manifesto ou código do plugin ausente")

        manifest = self._load_manifest(manifest_path)
        self._validate_manifest(manifest)

        target = self.plugins_root / manifest["id"]
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(repo_path, target)

    def list_plugins(self) -> list[dict[str, Any]]:
        plugins: list[dict[str, Any]] = []
        for entry in self.plugins_root.iterdir():
            if not entry.is_dir():
                continue
            manifest_path = entry / "plugin.yml"
            if not manifest_path.exists():
                continue
            manifest = self._load_manifest(manifest_path)
            plugins.append(
                {
                    "id": manifest.get("id"),
                    "type": manifest.get("type"),
                    "permissions": manifest.get("permissions", {}),
                }
            )
        return plugins

    def execute_send(self, plugin_id: str, payload: dict[str, Any]) -> Any:
        manifest, module = self._load_plugin(plugin_id)
        if manifest["type"] != "send":
            raise ValueError("Plugin não é do tipo send")
        func = self._resolve_entrypoint(manifest, module)
        return func(payload)

    def execute_export(self, plugin_id: str, input_path: Path, output_path: Path | None = None) -> Any:
        manifest, module = self._load_plugin(plugin_id)
        if manifest["type"] != "export":
            raise ValueError("Plugin não é do tipo export")
        func = self._resolve_entrypoint(manifest, module)
        if output_path:
            return func(input_path, output_path=output_path)
        return func(input_path)

    def execute_hook(self, plugin_id: str, context: dict[str, Any]) -> Any:
        manifest, module = self._load_plugin(plugin_id)
        if manifest["type"] != "hook":
            raise ValueError("Plugin não é do tipo hook")
        func = self._resolve_entrypoint(manifest, module)
        return func(context)

    def execute_generate(self, plugin_id: str, payload: dict[str, Any]) -> Any:
        manifest, module = self._load_plugin(plugin_id)
        if manifest["type"] != "generate":
            raise ValueError("Plugin não é do tipo generate")
        func = self._resolve_entrypoint(manifest, module)
        return func(payload)

    def _load_manifest(self, manifest_path: Path) -> dict[str, Any]:
        return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}

    def _validate_manifest(self, manifest: dict[str, Any]) -> None:
        required = ["id", "name", "version", "type", "entrypoint"]
        for key in required:
            if not manifest.get(key):
                raise ValueError(f"Manifesto inválido: campo obrigatório {key} faltando")
        if manifest["type"] not in self.ALLOWED_TYPES:
            raise ValueError("Tipo de plugin inválido")
        if ":" not in manifest["entrypoint"]:
            raise ValueError("Entrypoint deve ser no formato module:function")

    def _load_plugin(self, plugin_id: str) -> tuple[dict[str, Any], Any]:
        plugin_dir = self.plugins_root / plugin_id
        manifest_path = plugin_dir / "plugin.yml"
        code_path = plugin_dir / "plugin.py"
        if not manifest_path.exists() or not code_path.exists():
            raise ValueError("Plugin não instalado")
        manifest = self._load_manifest(manifest_path)
        self._validate_manifest(manifest)
        module = self._import_module(code_path, f"plugin_{plugin_id}")
        return manifest, module

    def _import_module(self, code_path: Path, module_name: str):
        spec = importlib.util.spec_from_file_location(module_name, code_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Não foi possível carregar módulo em {code_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _resolve_entrypoint(self, manifest: dict[str, Any], module: Any):
        entry = manifest["entrypoint"]
        mod_name, func_name = entry.split(":", 1)
        if mod_name != "plugin":
            raise ValueError("Entrypoint deve referenciar module 'plugin'")
        func = getattr(module, func_name, None)
        if func is None:
            raise ValueError("Função de entrypoint não encontrada")
        return func
