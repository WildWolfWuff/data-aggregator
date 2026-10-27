import asyncio
import builtins
from collections.abc import Callable
from typing import Any

import httpx2
import pandas as pd
from pydantic import FilePath, HttpUrl

from .auth import build_request_auth
from .config import ScriptDataProcessorConfig
from .errors import ScriptExecutionError, ScriptLoadError
from .validation import PROCESS_FUNCTION_NAME, validate_script

_SAFE_BUILTIN_NAMES = [
  "abs",
  "all",
  "any",
  "bool",
  "bytes",
  "dict",
  "divmod",
  "enumerate",
  "filter",
  "float",
  "frozenset",
  "int",
  "isinstance",
  "issubclass",
  "iter",
  "len",
  "list",
  "map",
  "max",
  "min",
  "next",
  "pow",
  "print",
  "range",
  "repr",
  "reversed",
  "round",
  "set",
  "slice",
  "sorted",
  "str",
  "sum",
  "tuple",
  "type",
  "zip",
  "ArithmeticError",
  "AttributeError",
  "Exception",
  "IndexError",
  "KeyError",
  "KeyboardInterrupt",
  "LookupError",
  "NotImplementedError",
  "RuntimeError",
  "StopIteration",
  "TypeError",
  "ValueError",
  "ZeroDivisionError",
  "True",
  "False",
  "None",
]


def _decode(raw: bytes, max_size: int) -> str:
  if len(raw) > max_size:
    raise ScriptLoadError(f"script exceeds {max_size} bytes")
  try:
    return raw.decode("utf-8")
  except UnicodeDecodeError as e:
    raise ScriptLoadError("script is not valid UTF-8") from e


async def _load_script_from_content(content: str, max_size: int = 1_000_000) -> str:
  if not content.strip():
    raise ScriptLoadError("script content is empty")
  return await asyncio.to_thread(_decode, content.encode(), max_size)


async def _load_script_from_remote(
  source: HttpUrl,
  config: ScriptDataProcessorConfig,
  transport: httpx2.AsyncBaseTransport | None = None,
) -> str:
  auth, headers = build_request_auth(config.auth)
  try:
    async with (
      httpx2.AsyncClient(
        timeout=config.timeout, follow_redirects=False, transport=transport, auth=auth, headers=headers
      ) as client,
      client.stream("GET", str(source)) as response,
    ):
      response.raise_for_status()
      body = bytearray()
      async for chunk in response.aiter_bytes():
        body += chunk
        if len(body) > config.max_size_bytes:
          raise ScriptLoadError(f"script exceeds {config.max_size_bytes} bytes")
  except httpx2.HTTPStatusError as e:
    raise ScriptLoadError(f"remote script request failed with status {e.response.status_code}") from e
  except httpx2.HTTPError as e:
    # Drop the original error, whose text may echo the request URL.
    raise ScriptLoadError(f"remote script request failed: {type(e).__name__}") from None
  return _decode(bytes(body), config.max_size_bytes)


async def _load_script_from_local(source: FilePath, max_size: int = 1_000_000) -> str:
  try:
    raw = await asyncio.to_thread(source.read_bytes)
  except OSError as e:
    raise ScriptLoadError(f"cannot read script file: {e.strerror}") from e
  return _decode(raw, max_size)


async def _load_script(config: ScriptDataProcessorConfig, transport: httpx2.AsyncBaseTransport | None = None) -> str:
  if config.content is not None:
    return await _load_script_from_content(config.content, config.max_size_bytes)
  if isinstance(config.source, HttpUrl):
    return await _load_script_from_remote(config.source, config, transport)
  if config.source is not None:
    return await _load_script_from_local(config.source, config.max_size_bytes)
  raise ScriptLoadError("no script source configured")


def _build_namespace(allowed_modules: frozenset[str]) -> dict[str, Any]:
  def guarded_import(name: str, globals=None, locals=None, fromlist=(), level=0):
    if level or name.split(".")[0] not in allowed_modules:
      raise ImportError(f"import of '{name}' is not allowed")
    return builtins.__import__(name, globals, locals, fromlist, level)

  safe = {n: getattr(builtins, n) for n in _SAFE_BUILTIN_NAMES}
  safe["__import__"] = guarded_import
  return {"__builtins__": safe, "__name__": "aggregator_script"}


def _compile_process(source: str, config: ScriptDataProcessorConfig) -> Callable[[dict[str, pd.DataFrame]], Any]:
  tree = validate_script(source, config.allowed_modules)
  namespace = _build_namespace(config.allowed_modules)
  try:
    exec(compile(tree, "<aggregator-script>", "exec"), namespace)
  except Exception as e:
    raise ScriptExecutionError(f"script failed to load: {type(e).__name__}: {e}") from e
  return namespace[PROCESS_FUNCTION_NAME]


type AggregateDataFunc = Callable[[dict[str, pd.DataFrame]], Any]


async def load_aggregate_data_script(
  config: ScriptDataProcessorConfig, transport: httpx2.AsyncBaseTransport | None = None
) -> AggregateDataFunc:
  source = await _load_script(config, transport)
  aggregate_data_func = _compile_process(source, config)
  return aggregate_data_func
