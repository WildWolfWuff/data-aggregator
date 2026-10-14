from abc import ABC
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from data_aggregator_provider_core.column_definition import ColumnDefinition
from data_aggregator_provider_core.provider_reference import ProviderReference


class ExportMode(StrEnum):
  OVERWRITE = "overwrite"
  APPEND = "append"


class ExporterConfigurationBase(BaseModel, ABC):
  name: Annotated[str, Field(description="Exporter name")]
  target: Annotated[str, Field(description="Target for the exporter")]
  provider: Annotated[ProviderReference, Field(description="Provider reference")]
  mode: Annotated[ExportMode, Field(description="How the data is stored in the target")]
  distinct: Annotated[
    bool | str | list[str],
    Field(description="Distinct all rows, or only by the given column or columns"),
  ] = False
  columns: Annotated[
    list[ColumnDefinition] | None,
    Field(default=None, description="Columns for the exporter, all columns if unset"),
  ]
  index: Annotated[
    list[str],
    Field(description="Index fields for the exporter"),
  ] = []
