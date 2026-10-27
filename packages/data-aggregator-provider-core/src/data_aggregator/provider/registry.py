import importlib
import importlib.metadata
from typing import Any

from pydantic import BaseModel, ValidationError

from data_aggregator.provider.config import (
  AggregatorProviderConfig,
  DataCoreConfig,
  DataProviderRefConfig,
  ProviderName,
  ProviderType,
)
from data_aggregator.provider.core import (
  ENTRY_POINT_GROUP,
  Capability,
  DataProvider,
  validate_provider_class,
)
from data_aggregator.provider.plugins import PluginLoadError, PluginsConfig, add_plugin_paths, install_plugins


class ProviderRegistry:
  """Discovers provider plugins and resolves provider references. Any problem aborts with PluginLoadError."""

  def __init__(self) -> None:
    self.classes: dict[str, type[DataProvider]] = {}
    self.sources: dict[str, str] = {}
    self.providers: dict[tuple[ProviderType, ProviderName], DataProvider] = {}

  @classmethod
  def load(cls, plugins: PluginsConfig) -> ProviderRegistry:
    install_plugins(plugins)
    add_plugin_paths(plugins)
    registry = cls()
    errors: list[str] = []
    for ep in importlib.metadata.entry_points(group=ENTRY_POINT_GROUP):
      if plugins.allowlist is not None and ep.name not in plugins.allowlist:
        continue
      registry._register(ep.load, f"entry point '{ep.name}'", errors, expected_type=ep.name)
    for path in plugins.import_paths:
      registry._register(lambda p=path: _import_path(p), f"import path '{path}'", errors)
    if errors:
      raise PluginLoadError(errors)
    return registry

  def _register(self, loader: Any, source: str, errors: list[str], expected_type: str | None = None) -> None:
    try:
      provider_cls = loader()
    except Exception as e:
      errors.append(f"{source}: failed to load: {e!r}")
      return
    problems = validate_provider_class(provider_cls)
    if not problems and expected_type and provider_cls.provider_type != expected_type:
      problems = [f"provider_type '{provider_cls.provider_type}' differs from entry point name '{expected_type}'"]
    if not problems and provider_cls.provider_type in self.classes:
      problems = [
        f"duplicate provider_type '{provider_cls.provider_type}' "
        f"(already from {self.sources[provider_cls.provider_type]})"
      ]
    if problems:
      errors.extend(f"{source}: {p}" for p in problems)
      return
    self.classes[provider_cls.provider_type] = provider_cls
    self.sources[provider_cls.provider_type] = source

  def resolve(self, config: AggregatorProviderConfig) -> dict[tuple[ProviderType, ProviderName], DataProvider]:
    """Validate provider configs and collector/exporter references, then instantiate used providers."""
    errors: list[str] = []
    for ptype, named in config.providers.items():
      cls = self.classes.get(ptype)
      if cls is None:
        errors.append(f"providers.{ptype}: no plugin provides this provider type")
        continue
      for name, raw in named.items():
        try:
          model = raw if isinstance(raw, cls.config_model) else cls.config_model.model_validate(raw)
          self.providers[ptype, name] = cls(name, model)
        except ValidationError as e:
          errors.append(f"providers.{ptype}.{name}: invalid config: {e}")

    for section, entries, cap in (
      ("collectors", config.collectors, Capability.COLLECT),
      ("exporters", config.exporters, Capability.EXPORT),
    ):
      for entry_name, raw in entries.items():
        try:
          data = raw.model_dump() if isinstance(raw, BaseModel) else raw
          ref = DataCoreConfig.model_validate(data).provider
        except ValidationError as e:
          errors.append(f"{section}.{entry_name}: invalid provider reference: {e}")
          continue
        assert isinstance(ref, DataProviderRefConfig)
        provider = self.providers.get((ref.type, ref.name))
        if provider is None:
          errors.append(f"{section}.{entry_name}: unknown provider '{ref.type}:{ref.name}'")
        elif cap not in provider.capabilities:
          errors.append(f"{section}.{entry_name}: provider '{ref.type}' cannot {cap}")
    if errors:
      raise PluginLoadError(errors)
    return self.providers


def _import_path(path: str) -> object:
  module, _, attr = path.partition(":")
  if not module or not attr:
    raise ValueError("expected 'module:Class'")
  return getattr(importlib.import_module(module), attr)
