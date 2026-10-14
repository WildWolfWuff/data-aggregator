from abc import ABC, abstractmethod
from enum import StrEnum

from .collector import Collector
from .collector_configuration import CollectorConfigurationBase
from .exporter import Exporter
from .exporter_configuration import ExporterConfigurationBase
from .health_check import HealthChecker
from .provider_configuration import ProviderConfigurationBase


class ProviderCapability(StrEnum):
  COLLECT = "collect"
  EXPORT = "export"
  CHECK = "check"


class ProviderPlugin[
  P: ProviderConfigurationBase,
  C: CollectorConfigurationBase,
  E: ExporterConfigurationBase,
](ABC):
  """Entry point of a provider; override the `create_*` hooks matching `capabilities`."""

  @property
  @abstractmethod
  def name(self) -> str:
    """Unique provider name, used as provider type in the configuration."""

  @property
  @abstractmethod
  def version(self) -> str: ...

  @property
  @abstractmethod
  def description(self) -> str: ...

  @property
  @abstractmethod
  def capabilities(self) -> frozenset[ProviderCapability]: ...

  @property
  @abstractmethod
  def provider_configuration_type(self) -> type[P]: ...

  @property
  @abstractmethod
  def collector_configuration_type(self) -> type[C] | None:
    return None

  @property
  @abstractmethod
  def exporter_configuration_type(self) -> type[E] | None:
    return None

  def create_collector(self) -> Collector[P, C]:
    raise NotImplementedError(f"Provider '{self.name}' does not support collecting")

  def create_exporter(self) -> Exporter[P, E]:
    raise NotImplementedError(f"Provider '{self.name}' does not support exporting")

  def create_checker(self) -> HealthChecker[P]:
    raise NotImplementedError(f"Provider '{self.name}' does not support health checks")
