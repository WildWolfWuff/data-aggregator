from data_aggregator.core.settings import AggregatorConfig, AggregatorSettingsBase
from data_aggregator.processing.config import AggregatorDataProcessingConfig


class AggregatorSettings(AggregatorSettingsBase, AggregatorDataProcessingConfig, AggregatorConfig):
  """
  TODO: add description for json schema
  """

  pass
