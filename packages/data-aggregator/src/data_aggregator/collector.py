import logging

import pandas as pd


async def collect_data_async() -> dict[str, pd.DataFrame]:
  # TODO: load porvider plugins and loop through the defined data sources
  logger = logging.getLogger(__name__)
  logger.info("Starting to collect data asynchronously")
  return {}
