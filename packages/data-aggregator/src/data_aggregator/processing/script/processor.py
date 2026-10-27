"""
Script data processor for handling python scripts.
That can be sourced from a URL or a local file, or provided as direct content.
The script must have a function named process that takes a dictionary of DataFrames and returns a DataFrame.

Scripts are statically validated and run with restricted builtins, which is defence in depth and not a sandbox.
"""

import asyncio
import inspect

import pandas as pd

from .config import ScriptDataProcessorConfig
from .errors import ScriptExecutionError
from .script_loader import load_aggregate_data_script
from .validation import PROCESS_FUNCTION_NAME


async def process_data(
  data: dict[str, pd.DataFrame],
  config: ScriptDataProcessorConfig,
) -> pd.DataFrame:
  aggregate_data_func = await load_aggregate_data_script(config)

  try:
    result = await (
      aggregate_data_func(data)
      if inspect.iscoroutinefunction(aggregate_data_func)
      else asyncio.to_thread(aggregate_data_func, data)
    )
  except Exception as e:
    raise ScriptExecutionError(f"script failed: {type(e).__name__}: {e}") from e
  if not isinstance(result, pd.DataFrame):
    raise ScriptExecutionError(f"'{PROCESS_FUNCTION_NAME}' must return a DataFrame, got {type(result).__name__}")
  return result
