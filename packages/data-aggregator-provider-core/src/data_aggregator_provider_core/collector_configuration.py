from abc import ABC
from typing import Annotated

from pydantic import BaseModel, Field

from data_aggregator_provider_core.column_definition import ColumnDefinition
from data_aggregator_provider_core.provider_reference import ProviderReference


class CollectorConfigurationBase(BaseModel, ABC):
  name: Annotated[str, Field(description="Collector name")]
  source: Annotated[str, Field(description="Data Source")]
  provider: Annotated[str | ProviderReference, Field(description="Provider reference")]
  columns: (
    Annotated[list[str | ColumnDefinition], Field(description="Column definition")] | None
  ) = None
  rename: (
    Annotated[dict[str, str], Field(description="Original column name to new column name")] | None
  ) = None
  index: (
    Annotated[
      list[str | ColumnDefinition],
      Field(description="Index fields for the collector"),
    ]
    | None
  ) = None
