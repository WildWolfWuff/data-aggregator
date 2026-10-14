from typing import Annotated

from pydantic import Field

from data_aggregator_core import (
  AggregatorSettingsBase,
)

from .collector_configuration import CollectorConfigurationBase
from .exporter_configuration import ExporterConfigurationBase


class AggregatorDataSettings(AggregatorSettingsBase):
  providers: Annotated[
    dict[str, dict[str, object]], Field(description="Configuration for data providers")
  ]

  collectors: Annotated[
    dict[str, object | CollectorConfigurationBase],
    Field(description="Configuration for data collectors"),
  ]

  exporters: Annotated[
    dict[str, object | ExporterConfigurationBase],
    Field(description="Configuration for data exporters"),
  ]
