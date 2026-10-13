from pydantic import Field

from data_aggregator_core import (
  AggregatorSettingsBase,
)
from data_aggregator_provider_core.collector_configuration_base import CollectorConfigurationBase
from data_aggregator_provider_core.exporter_configuration_base import ExporterConfigurationBase


class AggregatorDataSettings(AggregatorSettingsBase):
  providers: dict[str, dict[str, object]] = Field(
    default={}, description="Configuration for data providers"
  )

  collectors: dict[str, object | CollectorConfigurationBase] = Field(
    default={}, description="Configuration for data collectors"
  )

  exporters: dict[str, object | ExporterConfigurationBase] = Field(
    default={}, description="Configuration for data exporters"
  )
