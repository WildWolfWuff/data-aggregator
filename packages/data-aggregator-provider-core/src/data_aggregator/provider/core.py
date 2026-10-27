from abc import ABC
from enum import StrEnum
from typing import Any, ClassVar

from data_aggregator.provider.config import (
  DataCollectorConfigBase,
  DataExporterConfigBase,
  DataProviderConfigBase,
)

PROVIDER_API_VERSION = 1
"""Version of the provider interface; bump on breaking changes."""

ENTRY_POINT_GROUP = "data_aggregator.providers"
"""Entry point group plugins use to register their DataProvider class."""


class Capability(StrEnum):
  COLLECT = "collect"
  EXPORT = "export"


class DataProvider(ABC):
  """Base class for data provider plugins.

  Subclasses declare ``provider_type``, ``config_model``, ``api_version`` and ``capabilities``
  and override ``collect`` and/or ``export`` accordingly.
  """

  provider_type: ClassVar[str]
  config_model: ClassVar[type[DataProviderConfigBase]]
  api_version: ClassVar[int] = PROVIDER_API_VERSION
  capabilities: ClassVar[frozenset[Capability]]

  def __init__(self, name: str, config: DataProviderConfigBase) -> None:
    self.name = name
    self.config = config

  async def collect(self, collector: DataCollectorConfigBase) -> Any:
    raise NotImplementedError(f"Provider '{self.provider_type}' cannot collect")

  async def export(self, data: Any, exporter: DataExporterConfigBase) -> None:
    raise NotImplementedError(f"Provider '{self.provider_type}' cannot export")

  async def close(self) -> None:  # noqa: B027
    """Release resources held by the provider."""


def validate_provider_class(cls: object) -> list[str]:
  """Return the contract violations of a plugin class (empty if valid). Usable as plugin contract test."""
  if not (isinstance(cls, type) and issubclass(cls, DataProvider)):
    return [f"{cls!r} is not a DataProvider subclass"]
  errors: list[str] = []
  for attr in ("provider_type", "config_model", "capabilities"):
    if not hasattr(cls, attr):
      errors.append(f"{cls.__name__}: missing '{attr}'")
  if errors:
    return errors
  if cls.api_version != PROVIDER_API_VERSION:
    errors.append(f"{cls.__name__}: api_version {cls.api_version} != supported {PROVIDER_API_VERSION}")
  if not (isinstance(cls.config_model, type) and issubclass(cls.config_model, DataProviderConfigBase)):
    errors.append(f"{cls.__name__}: config_model must subclass DataProviderConfigBase")
  caps = cls.capabilities
  if not caps or not all(isinstance(c, Capability) for c in caps):
    errors.append(f"{cls.__name__}: capabilities must be a non-empty set of Capability")
    return errors
  for cap, method in ((Capability.COLLECT, "collect"), (Capability.EXPORT, "export")):
    overridden = getattr(cls, method) is not getattr(DataProvider, method)
    if cap in caps and not overridden:
      errors.append(f"{cls.__name__}: declares '{cap}' but does not override {method}()")
    if cap not in caps and overridden:
      errors.append(f"{cls.__name__}: overrides {method}() but does not declare '{cap}'")
  return errors
