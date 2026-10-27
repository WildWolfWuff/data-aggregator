import pandas as pd
import pytest

from data_aggregator.processing.script import (
  ScriptDataProcessorConfig,
  ScriptExecutionError,
  ScriptValidationError,
  process_data,
)

SCRIPT = """
import pandas as pd

def aggregate_data(data):
  return pd.concat(data.values(), ignore_index=True)
"""

DATA = {"a": pd.DataFrame({"x": [1]}), "b": pd.DataFrame({"x": [2]})}


@pytest.mark.asyncio
async def test_process_sync_content() -> None:
  result = await process_data(DATA, ScriptDataProcessorConfig(content=SCRIPT))
  assert result["x"].tolist() == [1, 2]


@pytest.mark.asyncio
async def test_process_async_content() -> None:
  script = "async def aggregate_data(data):\n  return data['a']\n"
  result = await process_data(DATA, ScriptDataProcessorConfig(content=script))
  assert result["x"].tolist() == [1]


@pytest.mark.asyncio
async def test_script_mutates_input_frames() -> None:
  data = {"a": pd.DataFrame({"x": [1]}), "b": pd.DataFrame({"x": [2]})}
  script = "def aggregate_data(data):\n  data['a']['x'] = 99\n  return data['a']\n"
  await process_data(data, ScriptDataProcessorConfig(content=script))
  assert data["a"]["x"].tolist() == [99]


@pytest.mark.asyncio
async def test_runtime_import_guard() -> None:
  script = "import pandas\ndef aggregate_data(d):\n  import os\n  return d\n"
  with pytest.raises(ScriptValidationError):
    await process_data(DATA, ScriptDataProcessorConfig(content=script))


@pytest.mark.asyncio
async def test_non_dataframe_result() -> None:
  with pytest.raises(ScriptExecutionError):
    await process_data(DATA, ScriptDataProcessorConfig(content="def aggregate_data(d):\n  return 1\n"))


@pytest.mark.asyncio
async def test_script_exception_wrapped() -> None:
  with pytest.raises(ScriptExecutionError):
    await process_data(DATA, ScriptDataProcessorConfig(content="def aggregate_data(d):\n  return 1 / 0\n"))
