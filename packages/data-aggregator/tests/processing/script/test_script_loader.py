import httpx2
import pytest

from data_aggregator.processing.script import ScriptDataProcessorConfig, ScriptLoadError
from data_aggregator.processing.script.script_loader import _load_script

SCRIPT = "def aggregate_data(data):\n  return data\n"


@pytest.mark.asyncio
async def test_local_file(tmp_path) -> None:
  path = tmp_path / "s.py"
  path.write_text(SCRIPT)
  assert await _load_script(ScriptDataProcessorConfig(source=path)) == SCRIPT


def _remote(handler, **kwargs) -> tuple[ScriptDataProcessorConfig, httpx2.MockTransport]:
  return ScriptDataProcessorConfig(source="https://example.com/s.py", **kwargs), httpx2.MockTransport(handler)


@pytest.mark.asyncio
async def test_remote_oversized() -> None:
  config, transport = _remote(lambda r: httpx2.Response(200, text="x" * 100), max_size_bytes=10)
  with pytest.raises(ScriptLoadError):
    await _load_script(config, transport)


@pytest.mark.asyncio
async def test_remote_redirect_not_followed() -> None:
  config, transport = _remote(lambda r: httpx2.Response(302, headers={"location": "https://evil.example/"}))
  with pytest.raises(ScriptLoadError):
    await _load_script(config, transport)