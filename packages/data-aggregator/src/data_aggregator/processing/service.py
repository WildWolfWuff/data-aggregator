from collections.abc import Callable
from types import CoroutineType
from typing import Any

from pandas import DataFrame

from .config import AggregatorDataProcessingConfig
from .script.config import ScriptDataProcessorConfig


async def execute_data_processing(
  data: dict[str, DataFrame], processing_config: AggregatorDataProcessingConfig
) -> DataFrame:
  processing_func: (
    Callable[[dict[str, DataFrame], ScriptDataProcessorConfig], CoroutineType[Any, Any, DataFrame]] | None
  ) = None
  if isinstance(processing_config.processing, ScriptDataProcessorConfig):
    from .script.processor import process_data

    processing_func = process_data

  # TODO: add other processors here based on the configuration type

  if processing_func is None:
    raise ValueError("Unsupported processing configuration type")
  return await processing_func(data, processing_config.processing)
