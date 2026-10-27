import sys
import textwrap
import zipfile
from pathlib import Path

import pytest

from data_aggregator.provider.config import AggregatorProviderConfig, DataProviderConfigBase, PluginsConfig
from data_aggregator.provider.core import Capability, DataProvider
from data_aggregator.provider.plugins import PluginLoadError
from data_aggregator.provider.registry import ProviderRegistry, _import_path


class Cfg(DataProviderConfigBase):
  url: str


class Both(DataProvider):
  provider_type = "both"
  config_model = Cfg
  capabilities = frozenset({Capability.COLLECT, Capability.EXPORT})

  async def collect(self, collector):
    return [1]

  async def export(self, data, exporter):
    return None


class CollectOnly(DataProvider):
  provider_type = "src"
  config_model = Cfg
  capabilities = frozenset({Capability.COLLECT})

  async def collect(self, collector):
    return [1]


def _registry(*classes: type[DataProvider]) -> ProviderRegistry:
  registry = ProviderRegistry()
  for c in classes:
    registry.classes[c.provider_type] = c
  return registry


def _config(**kw) -> AggregatorProviderConfig:
  base = {"providers": {}, "collectors": {}, "exporters": {}, "plugins": {}}
  return AggregatorProviderConfig.model_validate({**base, **kw})


def test_resolve_ok() -> None:
  cfg = _config(
    providers={"both": {"a": {"url": "x"}}},
    collectors={"c": {"provider": "both:a"}},
    exporters={"e": {"provider": "both:a"}},
  )
  providers = _registry(Both).resolve(cfg)
  assert isinstance(providers[("both", "a")], Both)


def test_resolve_invalid_config() -> None:
  with pytest.raises(PluginLoadError, match="invalid config"):
    _registry(Both).resolve(_config(providers={"both": {"a": {}}}))


def test_resolve_unknown_provider_type() -> None:
  with pytest.raises(PluginLoadError, match="no plugin provides"):
    _registry().resolve(_config(providers={"ghost": {"a": {}}}))


def test_resolve_unknown_reference_and_capability_collects_all_errors() -> None:
  cfg = _config(
    providers={"src": {"a": {"url": "x"}}},
    exporters={"e": {"provider": "src:a"}},
    collectors={"c": {"provider": "nope:z"}},
  )
  with pytest.raises(PluginLoadError) as e:
    _registry(CollectOnly).resolve(cfg)
  assert len(e.value.errors) == 2
  assert any("cannot export" in m for m in e.value.errors)
  assert any("unknown provider" in m for m in e.value.errors)


def test_resolve_invalid_reference() -> None:
  with pytest.raises(PluginLoadError, match="invalid provider reference"):
    _registry(Both).resolve(_config(collectors={"c": {"provider": "bad"}}))


def test_import_path() -> None:
  assert _import_path("pathlib:Path") is Path
  with pytest.raises(ValueError, match="module:Class"):
    _import_path("nocolon")


def test_load_import_path_registers_provider(tmp_path: Path) -> None:
  (tmp_path / "wwimp.py").write_text(
    textwrap.dedent(
      """
      from data_aggregator.provider import Capability, DataProvider
      from data_aggregator.provider.config import DataProviderConfigBase

      class P(DataProvider):
        provider_type = "wwimp"
        config_model = DataProviderConfigBase
        capabilities = frozenset({Capability.COLLECT})

        async def collect(self, collector):
          return 1
      """
    )
  )
  sys.path.insert(0, str(tmp_path))
  try:
    registry = ProviderRegistry.load(PluginsConfig(import_paths=["wwimp:P"]))
    assert "wwimp" in registry.classes
    assert registry.sources["wwimp"] == "import path 'wwimp:P'"
    with pytest.raises(PluginLoadError, match="duplicate provider_type"):
      ProviderRegistry.load(PluginsConfig(import_paths=["wwimp:P", "wwimp:P"]))
  finally:
    sys.path.remove(str(tmp_path))
    sys.modules.pop("wwimp", None)


def test_load_errors_abort() -> None:
  with pytest.raises(PluginLoadError, match="failed to load"):
    ProviderRegistry.load(PluginsConfig(import_paths=["does.not.exist:X"]))
  with pytest.raises(PluginLoadError, match="not a DataProvider"):
    ProviderRegistry.load(PluginsConfig(import_paths=["pathlib:Path"]))


def _build_wheel(directory: Path, name: str = "wwplugin", entry_name: str | None = None) -> Path:
  wheel = directory / f"{name}-1.0-py3-none-any.whl"
  info = f"{name}-1.0.dist-info"
  code = (
    "from data_aggregator.provider import DataProvider, Capability\n"
    "from data_aggregator.provider.config import DataProviderConfigBase\n"
    "class P(DataProvider):\n"
    f"  provider_type = '{name}'\n  config_model = DataProviderConfigBase\n"
    "  capabilities = frozenset({Capability.COLLECT})\n"
    "  async def collect(self, collector):\n    return 1\n"
  )
  with zipfile.ZipFile(wheel, "w") as z:
    z.writestr(f"{name}.py", code)
    z.writestr(f"{info}/METADATA", f"Metadata-Version: 2.1\nName: {name}\nVersion: 1.0\n")
    z.writestr(f"{info}/WHEEL", "Wheel-Version: 1.0\nGenerator: t\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
    z.writestr(f"{info}/entry_points.txt", f"[data_aggregator.providers]\n{entry_name or name} = {name}:P\n")
    z.writestr(f"{info}/RECORD", "")
  return wheel


def test_load_installs_wheel_and_discovers_entry_point(tmp_path: Path) -> None:
  target = tmp_path / "site"
  cfg = PluginsConfig(packages=[str(_build_wheel(tmp_path))], install_dir=target, no_index=True)
  before = list(sys.path)
  try:
    assert "wwplugin" in ProviderRegistry.load(cfg).classes
    assert "wwplugin" not in ProviderRegistry.load(cfg.model_copy(update={"allowlist": []})).classes
  finally:
    sys.path[:] = before
    sys.modules.pop("wwplugin", None)


def test_entry_point_name_must_match_provider_type(tmp_path: Path) -> None:
  target = tmp_path / "site"
  wheel = _build_wheel(tmp_path, name="wwmismatch", entry_name="other")
  cfg = PluginsConfig(packages=[str(wheel)], install_dir=target, no_index=True)
  before = list(sys.path)
  try:
    with pytest.raises(PluginLoadError, match="differs from entry point name"):
      ProviderRegistry.load(cfg)
  finally:
    sys.path[:] = before
    sys.modules.pop("wwmismatch", None)
