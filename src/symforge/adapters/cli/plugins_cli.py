from pathlib import Path
from typing import Any, Dict

from symforge.application.plugins.manager import PluginManager


class PluginsCLI:
    def __init__(self, workspace: Path):
        self.manager = PluginManager(workspace / "plugins")

    def add(self, repo_path: Path) -> None:
        self.manager.add_from_path(repo_path)

    def list(self) -> list[dict[str, Any]]:
        return self.manager.list_plugins()

    def send(self, plugin_id: str, payload: Dict[str, Any]) -> Any:
        return self.manager.execute_send(plugin_id, payload)

    def export(self, plugin_id: str, input_path: Path, output_path: Path | None = None) -> Any:
        return self.manager.execute_export(plugin_id, input_path, output_path)

    def hook(self, plugin_id: str, context: Dict[str, Any]) -> Any:
        return self.manager.execute_hook(plugin_id, context)

    def generate(self, plugin_id: str, payload: Dict[str, Any]) -> Any:
        return self.manager.execute_generate(plugin_id, payload)
