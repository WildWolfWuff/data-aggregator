from data_aggregator.processing.service import execute_data_processing
from data_aggregator.provider import PluginLoadError, ProviderRegistry
from data_aggregator.settings import AggregatorSettings


async def execute_aggregator():
  try:
    settings = AggregatorSettings()

    registry = ProviderRegistry.load(settings.plugins)
    registry.resolve(settings)
    data = {}  # TODO: call the collectors based on the configurations
    print("Initialize Aggregator:", settings.name)  # TODO: convert to logging
    result = await execute_data_processing(data, settings)
    # TODO: call the exporters based on the configurations
    print("Aggregator executed", result)

  except PluginLoadError:
    raise
  except ValueError as e:
    print("Error initializing Aggregator:", e)
