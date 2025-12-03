"""
TDD Unit Tests for PluginManager application layer.

Tests cover:
- Plugin installation (add_from_path)
- Plugin listing
- Plugin execution (send/export/hook/generate)
- Manifest validation
- Permission validation
- Error handling
"""

import pytest
from pathlib import Path

from symforge.application.plugins.manager import PluginManager


def create_plugin_repo(
    tmp_path: Path,
    plugin_id: str = "test_plugin",
    plugin_type: str = "send",
    entrypoint: str = "plugin:run",
    permissions: dict | None = None,
    code: str | None = None,
) -> Path:
    """Helper to create a valid plugin repository structure."""
    repo = tmp_path / f"{plugin_id}_repo"
    repo.mkdir()

    if permissions is None:
        permissions = {"fs": [], "env": [], "network": False}

    manifest = {
        "id": plugin_id,
        "name": f"Test Plugin {plugin_id}",
        "version": "1.0.0",
        "type": plugin_type,
        "entrypoint": entrypoint,
        "permissions": permissions,
    }

    import yaml

    (repo / "plugin.yml").write_text(yaml.safe_dump(manifest), encoding="utf-8")

    if code is None:
        code = """
def run(payload):
    return {"status": "ok", "payload": payload}
"""

    (repo / "plugin.py").write_text(code, encoding="utf-8")

    return repo


@pytest.fixture
def plugins_root(tmp_path: Path) -> Path:
    return tmp_path / "plugins"


@pytest.fixture
def manager(plugins_root: Path) -> PluginManager:
    return PluginManager(plugins_root)


class TestPluginManagerCreation:
    """Tests for PluginManager initialization."""

    def test_manager_creates_plugins_directory(self, tmp_path: Path):
        plugins_root = tmp_path / "plugins"
        PluginManager(plugins_root)

        assert plugins_root.exists()
        assert plugins_root.is_dir()

    def test_manager_works_with_existing_directory(self, tmp_path: Path):
        plugins_root = tmp_path / "plugins"
        plugins_root.mkdir()

        PluginManager(plugins_root)

        assert plugins_root.exists()


class TestPluginAddFromPath:
    """Tests for add_from_path() installation."""

    def test_add_plugin_copies_to_plugins_root(
        self, manager: PluginManager, tmp_path: Path, plugins_root: Path
    ):
        repo = create_plugin_repo(tmp_path, plugin_id="my_plugin")

        manager.add_from_path(repo)

        installed = plugins_root / "my_plugin"
        assert installed.exists()
        assert (installed / "plugin.yml").exists()
        assert (installed / "plugin.py").exists()

    def test_add_plugin_without_manifest_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad_plugin"
        repo.mkdir()
        (repo / "plugin.py").write_text("def run(): pass")

        with pytest.raises(ValueError, match="Manifesto ou código"):
            manager.add_from_path(repo)

    def test_add_plugin_without_code_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad_plugin"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(yaml.safe_dump({"id": "test"}))

        with pytest.raises(ValueError, match="Manifesto ou código"):
            manager.add_from_path(repo)

    def test_add_plugin_replaces_existing(
        self, manager: PluginManager, tmp_path: Path, plugins_root: Path
    ):
        repo1 = create_plugin_repo(
            tmp_path, plugin_id="same_plugin", code="def run(p): return 'v1'"
        )
        manager.add_from_path(repo1)

        # Create second version
        repo2 = tmp_path / "same_plugin_v2"
        repo2.mkdir()
        import yaml

        (repo2 / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "id": "same_plugin",
                    "name": "V2",
                    "version": "2.0.0",
                    "type": "send",
                    "entrypoint": "plugin:run",
                    "permissions": {"fs": [], "env": [], "network": False},
                }
            )
        )
        (repo2 / "plugin.py").write_text("def run(p): return 'v2'")

        manager.add_from_path(repo2)

        # Verify replaced
        result = manager.execute_send("same_plugin", {})
        assert result == "v2"


class TestPluginListPlugins:
    """Tests for list_plugins()."""

    def test_list_empty_when_no_plugins(self, manager: PluginManager):
        plugins = manager.list_plugins()

        assert plugins == []

    def test_list_returns_installed_plugins(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo1 = create_plugin_repo(tmp_path, plugin_id="plugin_a", plugin_type="send")
        repo2 = create_plugin_repo(tmp_path, plugin_id="plugin_b", plugin_type="export")
        manager.add_from_path(repo1)
        manager.add_from_path(repo2)

        plugins = manager.list_plugins()

        assert len(plugins) == 2
        ids = {p["id"] for p in plugins}
        assert ids == {"plugin_a", "plugin_b"}

    def test_list_includes_type_and_permissions(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="test",
            plugin_type="hook",
            permissions={"fs": ["./data"], "env": ["HOME"], "network": False},
        )
        manager.add_from_path(repo)

        plugins = manager.list_plugins()

        assert plugins[0]["type"] == "hook"
        assert plugins[0]["permissions"]["fs"] == ["./data"]
        assert plugins[0]["permissions"]["env"] == ["HOME"]


class TestPluginExecuteSend:
    """Tests for execute_send()."""

    def test_execute_send_calls_entrypoint(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="sender",
            plugin_type="send",
            code='def run(payload): return {"sent": payload["message"]}',
        )
        manager.add_from_path(repo)

        result = manager.execute_send("sender", {"message": "hello"})

        assert result == {"sent": "hello"}

    def test_execute_send_wrong_type_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(tmp_path, plugin_id="exporter", plugin_type="export")
        manager.add_from_path(repo)

        with pytest.raises(ValueError, match="não é do tipo send"):
            manager.execute_send("exporter", {})

    def test_execute_send_nonexistent_plugin_raises_error(
        self, manager: PluginManager
    ):
        with pytest.raises(ValueError, match="Plugin não instalado"):
            manager.execute_send("nonexistent", {})


class TestPluginExecuteExport:
    """Tests for execute_export()."""

    def test_execute_export_calls_entrypoint(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="csv_export",
            plugin_type="export",
            code='def run(input_path, output_path=None): return str(input_path)',
        )
        manager.add_from_path(repo)

        result = manager.execute_export("csv_export", Path("/tmp/input.md"))

        assert result == "/tmp/input.md"

    def test_execute_export_with_output_path(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="csv_export",
            plugin_type="export",
            code='def run(input_path, output_path=None): return f"{input_path}:{output_path}"',
        )
        manager.add_from_path(repo)

        result = manager.execute_export(
            "csv_export", Path("/input.md"), Path("/output.csv")
        )

        assert "input.md" in result
        assert "output.csv" in result


class TestPluginExecuteHook:
    """Tests for execute_hook()."""

    def test_execute_hook_calls_entrypoint(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="logger",
            plugin_type="hook",
            code='def run(context): return {"logged": context["event"]}',
        )
        manager.add_from_path(repo)

        result = manager.execute_hook("logger", {"event": "step_completed"})

        assert result == {"logged": "step_completed"}

    def test_execute_hook_wrong_type_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(tmp_path, plugin_id="sender", plugin_type="send")
        manager.add_from_path(repo)

        with pytest.raises(ValueError, match="não é do tipo hook"):
            manager.execute_hook("sender", {})


class TestPluginExecuteGenerate:
    """Tests for execute_generate()."""

    def test_execute_generate_calls_entrypoint(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="text_gen",
            plugin_type="generate",
            code='def run(payload): return f"Generated: {payload[\'prompt\']}"',
        )
        manager.add_from_path(repo)

        result = manager.execute_generate("text_gen", {"prompt": "Hello world"})

        assert result == "Generated: Hello world"

    def test_execute_generate_wrong_type_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(tmp_path, plugin_id="sender", plugin_type="send")
        manager.add_from_path(repo)

        with pytest.raises(ValueError, match="não é do tipo generate"):
            manager.execute_generate("sender", {})


class TestManifestValidation:
    """Tests for manifest validation."""

    def test_manifest_missing_id_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "name": "Test",
                    "version": "1.0.0",
                    "type": "send",
                    "entrypoint": "plugin:run",
                    "permissions": {"fs": [], "env": [], "network": False},
                }
            )
        )
        (repo / "plugin.py").write_text("def run(p): pass")

        with pytest.raises(ValueError, match="id faltando"):
            manager.add_from_path(repo)

    def test_manifest_missing_type_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "id": "test",
                    "name": "Test",
                    "version": "1.0.0",
                    "entrypoint": "plugin:run",
                    "permissions": {"fs": [], "env": [], "network": False},
                }
            )
        )
        (repo / "plugin.py").write_text("def run(p): pass")

        with pytest.raises(ValueError, match="type faltando"):
            manager.add_from_path(repo)

    def test_manifest_invalid_type_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "id": "test",
                    "name": "Test",
                    "version": "1.0.0",
                    "type": "invalid_type",
                    "entrypoint": "plugin:run",
                    "permissions": {"fs": [], "env": [], "network": False},
                }
            )
        )
        (repo / "plugin.py").write_text("def run(p): pass")

        with pytest.raises(ValueError, match="Tipo de plugin inválido"):
            manager.add_from_path(repo)

    def test_manifest_invalid_entrypoint_format_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "id": "test",
                    "name": "Test",
                    "version": "1.0.0",
                    "type": "send",
                    "entrypoint": "run",  # Missing module:
                    "permissions": {"fs": [], "env": [], "network": False},
                }
            )
        )
        (repo / "plugin.py").write_text("def run(p): pass")

        with pytest.raises(ValueError, match="Entrypoint deve ser"):
            manager.add_from_path(repo)


class TestPermissionValidation:
    """Tests for permission validation."""

    def test_manifest_missing_permissions_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "id": "test",
                    "name": "Test",
                    "version": "1.0.0",
                    "type": "send",
                    "entrypoint": "plugin:run",
                    # No permissions
                }
            )
        )
        (repo / "plugin.py").write_text("def run(p): pass")

        with pytest.raises(ValueError, match="permissions ausente"):
            manager.add_from_path(repo)

    def test_network_permission_true_raises_error_offline_mode(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "id": "test",
                    "name": "Test",
                    "version": "1.0.0",
                    "type": "send",
                    "entrypoint": "plugin:run",
                    "permissions": {"fs": [], "env": [], "network": True},
                }
            )
        )
        (repo / "plugin.py").write_text("def run(p): pass")

        with pytest.raises(ValueError, match="network não é permitida"):
            manager.add_from_path(repo)

    def test_fs_permission_not_list_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = tmp_path / "bad"
        repo.mkdir()
        import yaml

        (repo / "plugin.yml").write_text(
            yaml.safe_dump(
                {
                    "id": "test",
                    "name": "Test",
                    "version": "1.0.0",
                    "type": "send",
                    "entrypoint": "plugin:run",
                    "permissions": {"fs": "./data", "env": [], "network": False},
                }
            )
        )
        (repo / "plugin.py").write_text("def run(p): pass")

        with pytest.raises(ValueError, match="fs deve ser lista"):
            manager.add_from_path(repo)


class TestPluginEdgeCases:
    """Edge cases and error handling."""

    def test_entrypoint_function_not_found_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="bad_entry",
            plugin_type="send",
            entrypoint="plugin:nonexistent_function",
            code="def run(p): pass",
        )
        manager.add_from_path(repo)

        with pytest.raises(ValueError, match="Função de entrypoint não encontrada"):
            manager.execute_send("bad_entry", {})

    def test_entrypoint_wrong_module_raises_error(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="bad_module",
            plugin_type="send",
            entrypoint="other:run",
            code="def run(p): pass",
        )
        manager.add_from_path(repo)

        with pytest.raises(ValueError, match="Entrypoint deve referenciar module"):
            manager.execute_send("bad_module", {})

    def test_plugin_with_unicode_content(
        self, manager: PluginManager, tmp_path: Path
    ):
        repo = create_plugin_repo(
            tmp_path,
            plugin_id="unicode_plugin",
            plugin_type="send",
            code='def run(payload): return {"msg": "Olá, mundo! 你好"}',
        )
        manager.add_from_path(repo)

        result = manager.execute_send("unicode_plugin", {})

        assert result["msg"] == "Olá, mundo! 你好"
