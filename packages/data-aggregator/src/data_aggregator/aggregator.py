from data_aggregator.core import AggregatorSettingsBase


def execute_aggregator():
  try:
    settings = AggregatorSettingsBase()
    print("Initialize Aggregator:", settings.name)

    print("Aggregator executed")
  except ValueError as e:
    print("Error initializing Aggregator:", e)
