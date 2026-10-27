import httpx2
import pytest

from data_aggregator.processing.script import ScriptDataProcessorConfig, ScriptLoadError
from data_aggregator.processing.script.config import BasicAuthConfig, TokenAuthConfig
from data_aggregator.processing.script.script_loader import _load_script

SCRIPT = "def aggregate_data(data):\n  return data\n"


def _remote(handler, **kwargs) -> tuple[ScriptDataProcessorConfig, httpx2.MockTransport]:
  return ScriptDataProcessorConfig(source="https://example.com/s.py", **kwargs), httpx2.MockTransport(handler)


@pytest.mark.asyncio
async def test_remote_token_auth() -> None:
  seen = {}

  def handler(request: httpx2.Request) -> httpx2.Response:
    seen["auth"] = request.headers.get("authorization")
    return httpx2.Response(200, text=SCRIPT)

  config, transport = _remote(handler, auth=TokenAuthConfig(token="abc"))
  assert await _load_script(config, transport) == SCRIPT
  assert seen["auth"] == "Bearer abc"


@pytest.mark.asyncio
async def test_remote_custom_token_header() -> None:
  seen = {}

  def handler(request: httpx2.Request) -> httpx2.Response:
    seen["key"] = request.headers.get("x-api-key")
    return httpx2.Response(200, text=SCRIPT)

  config, transport = _remote(handler, auth=TokenAuthConfig(token="abc", header="X-Api-Key", scheme=None))
  await _load_script(config, transport)
  assert seen["key"] == "abc"


@pytest.mark.asyncio
async def test_remote_basic_auth() -> None:
  seen = {}

  def handler(request: httpx2.Request) -> httpx2.Response:
    seen["auth"] = request.headers.get("authorization")
    return httpx2.Response(200, text=SCRIPT)

  config, transport = _remote(handler, auth=BasicAuthConfig(username="u", password="p"))
  await _load_script(config, transport)
  assert seen["auth"] == "Basic dTpw"


@pytest.mark.asyncio
async def test_remote_error_status() -> None:
  config, transport = _remote(lambda r: httpx2.Response(401))
  with pytest.raises(ScriptLoadError, match="401"):
    await _load_script(config, transport)
