import pandas as pd
import pytest

from data_aggregator.processing.config import AggregatorDataProcessingConfig
from data_aggregator.processing.script.config import ScriptDataProcessorConfig
from data_aggregator.processing.service import execute_data_processing


@pytest.mark.asyncio
async def test_execute_data_processing_with_script() -> None:
  data = {"source": pd.DataFrame({"value": [1, 2]})}
  config = AggregatorDataProcessingConfig(
    processing=ScriptDataProcessorConfig(
      content="def aggregate_data(data):\n  return data['source'].assign(value=data['source']['value'] * 2)\n"
    )
  )

  result = await execute_data_processing(data, config)

  assert result["value"].tolist() == [2, 4]
