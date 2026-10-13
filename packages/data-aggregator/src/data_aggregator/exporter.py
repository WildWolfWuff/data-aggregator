import logging

import pandas as pd


async def export_data_async(data: pd.DataFrame):
  logger = logging.getLogger(__name__)
  logger.info("Starting to export data asynchronously")
  pass
