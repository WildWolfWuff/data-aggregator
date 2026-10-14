from abc import ABC, abstractmethod
from typing import Annotated

from pandas import DataFrame
from pydantic import BaseModel, Field

from .exporter_configuration import ExporterConfigurationBase
from .provider_configuration import ProviderConfigurationBase


class SaveResult(BaseModel):
  rows: Annotated[int, Field(ge=0, description="Number of rows written to the target")]
  message: Annotated[str, Field(default="", description="Additional information about the save")]


class Exporter[P: ProviderConfigurationBase, T: ExporterConfigurationBase](ABC):
  @abstractmethod
  async def export(self, data: DataFrame, provider: P, target: T) -> SaveResult:
    """Save `data` to the location described by `target`."""
