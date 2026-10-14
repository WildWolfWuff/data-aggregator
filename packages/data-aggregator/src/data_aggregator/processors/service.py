import logging

import pandas as pd


async def process_data_async(
  data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
  logger = logging.getLogger(__name__)
  logger.info("Starting to process data asynchronously")

  # TODO: get the configured processor and run it with the provided data

  return pd.DataFrame()
