from data_aggregator.processing.service import execute_data_processing
from data_aggregator.settings import AggregatorSettings


async def execute_aggregator():
  try:
    settings = AggregatorSettings()

    data = {}  # TODO: call the collectors based on the configurations
    print("Initialize Aggregator:", settings.name)  # TODO: convert to logging
    result = await execute_data_processing(data, settings)
    # TODO: call the exporters based on the configurations
    print("Aggregator executed", result)
  except ValueError as e:
    print("Error initializing Aggregator:", e)
