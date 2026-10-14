import logging

import pandas as pd


async def export_data_async(data: pd.DataFrame):
  # TODO: load plugins for exporting data and call the export method for each export config key
  logger = logging.getLogger(__name__)
  logger.info("Starting to export data asynchronously")
  pass
