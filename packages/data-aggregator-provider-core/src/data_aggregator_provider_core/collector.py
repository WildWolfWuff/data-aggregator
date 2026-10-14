from abc import ABC, abstractmethod

from pandas import DataFrame

from .collector_configuration import CollectorConfigurationBase
from .provider_configuration import ProviderConfigurationBase


class Collector[P: ProviderConfigurationBase, S: CollectorConfigurationBase](ABC):
  @abstractmethod
  async def collect(self, provider: P, source: S) -> DataFrame:
    """Load the data described by `source` from the provider."""
