"""Base interfaces for Data Aggregator provider plugins."""

from .collector import Collector
from .collector_configuration import CollectorConfigurationBase
from .exporter import Exporter, SaveResult
from .exporter_configuration import ExporterConfigurationBase
from .health_check import HealthChecker
from .health_check_configuration import HealthCheckConfiguration
from .provider_configuration import ProviderConfigurationBase
from .provider_plugin import ProviderPlugin
from .provider_reference import ProviderReference
from .settings import AggregatorDataSettings

__all__ = [
  "AggregatorDataSettings",
  "Collector",
  "CollectorConfigurationBase",
  "Exporter",
  "ExporterConfigurationBase",
  "HealthCheckConfiguration",
  "HealthChecker",
  "ProviderConfigurationBase",
  "ProviderPlugin",
  "ProviderReference",
  "SaveResult",
]
