from abc import ABC

from pydantic import BaseModel, Field


class ExporterConfigurationBase(BaseModel, ABC):
  name: str = Field(description="Exporter name")
  target: str = Field(description="Target for the exporter")
  provider: str = Field(description="Provider reference")
  columns: list[str] = Field(description="Columns for the exporter")
  index: list[str] = Field(description="Index fields for the exporter")
