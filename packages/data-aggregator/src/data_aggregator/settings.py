from data_aggregator.core.settings import AggregatorConfig, AggregatorSettingsBase
from data_aggregator.processing.config import AggregatorDataProcessingConfig
from data_aggregator.provider.config import (
  AggregatorProviderConfig,
)


class AggregatorSettings(
  AggregatorSettingsBase, AggregatorDataProcessingConfig, AggregatorConfig, AggregatorProviderConfig
):
  """
  TODO: add description for json schema
  """

  pass
