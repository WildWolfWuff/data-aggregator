from abc import ABC

from pydantic import BaseModel, Field


class CollectorConfigurationBase(BaseModel, ABC):
  name: str = Field(description="Collector name")
  source: str = Field(description="Data Source")
  provider: str = Field(description="Provider reference")
  columns: list[str] = Field(description="Columns for the collector")
  index: list[str] = Field(description="Index fields for the collector")
