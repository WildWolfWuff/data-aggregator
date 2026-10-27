import sys
import zipfile
from pathlib import Path

import pytest

from data_aggregator.provider.config import PluginsConfig
from data_aggregator.provider.plugins import (
  INSTALL_MARKER,
  PluginLoadError,
  ProviderError,
  _core_constraints,
  _fingerprint,
  add_plugin_paths,
  install_plugins,
)


def _build_wheel(directory: Path) -> Path:
  wheel = directory / "wwplugin-1.0-py3-none-any.whl"
  info = "wwplugin-1.0.dist-info"
  with zipfile.ZipFile(wheel, "w") as z:
    z.writestr("wwplugin.py", "VALUE = 1\n")
    z.writestr(f"{info}/METADATA", "Metadata-Version: 2.1\nName: wwplugin\nVersion: 1.0\n")
    z.writestr(f"{info}/WHEEL", "Wheel-Version: 1.0\nGenerator: t\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
    z.writestr(f"{info}/RECORD", "")
  return wheel


def test_plugin_load_error_and_hierarchy() -> None:
  err = PluginLoadError(["a", "b"])
  assert isinstance(err, ProviderError)
  assert err.errors == ["a", "b"]
  assert "- a" in str(err)
  assert "- b" in str(err)


def test_core_constraints_pin_aggregator_packages() -> None:
  constraints = _core_constraints()
  assert "data-aggregator-provider-core==" in constraints.replace("_", "-").lower()


def test_fingerprint_changes_with_packages() -> None:
  assert _fingerprint(PluginsConfig(packages=["a"])) != _fingerprint(PluginsConfig(packages=["b"]))


def test_install_without_packages_is_noop(tmp_path: Path) -> None:
  install_plugins(PluginsConfig(install_dir=tmp_path / "x"))
  assert not (tmp_path / "x").exists()


def test_install_wheel_and_skip_when_unchanged(tmp_path: Path) -> None:
  target = tmp_path / "site"
  cfg = PluginsConfig(packages=[str(_build_wheel(tmp_path))], install_dir=target, no_index=True)
  install_plugins(cfg)
  assert (target / "wwplugin.py").exists()
  assert (target / INSTALL_MARKER).exists()

  (target / "wwplugin.py").unlink()
  install_plugins(cfg)
  assert not (target / "wwplugin.py").exists()


def test_install_failure_raises(tmp_path: Path) -> None:
  cfg = PluginsConfig(
    packages=[str(tmp_path / "missing-1.0-py3-none-any.whl")], install_dir=tmp_path / "s", no_index=True
  )
  with pytest.raises(PluginLoadError, match="installation failed"):
    install_plugins(cfg)
  assert not (tmp_path / "s" / INSTALL_MARKER).exists()


def test_add_plugin_paths(tmp_path: Path) -> None:
  install_dir = tmp_path / "site"
  plugin_dir = tmp_path / "mounted"
  install_dir.mkdir()
  plugin_dir.mkdir()
  (plugin_dir / "my_custom_test_plugin.py").write_text("VALUE = 2\n")
  before = list(sys.path)
  try:
    add_plugin_paths(PluginsConfig(install_dir=install_dir, plugin_dir=plugin_dir))
    assert str(install_dir) in sys.path
    import my_custom_test_plugin  # ty: ignore[unresolved-import]

    assert my_custom_test_plugin.VALUE == 2
  finally:
    sys.path[:] = before
    sys.modules.pop("my_custom_test_plugin", None)


def test_add_plugin_paths_ignores_missing(tmp_path: Path) -> None:
  before = list(sys.path)
  add_plugin_paths(PluginsConfig(install_dir=tmp_path / "nope"))
  assert sys.path == before
