import logging

from data_aggregator.collector import collect_data_async
from data_aggregator.exporter import export_data_async
from data_aggregator.processors import process_data_async
from data_aggregator.settings import AggregatorSettings


class Aggregator:
  def __init__(self):
    self.logger = logging.getLogger(__name__)
    self.settings = AggregatorSettings()

  async def execute(self):
    self.logger.info("Starting data aggregator '%s'", self.settings.name)
    self.logger.debug(self.settings.description)
    data = await collect_data_async()

    processed_data = await process_data_async(data)

    await export_data_async(processed_data)

    self.logger.info("App finished successfully")
