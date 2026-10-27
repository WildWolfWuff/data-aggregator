import pytest
from pydantic import ValidationError

from data_aggregator.processing.script import ScriptDataProcessorConfig
from data_aggregator.processing.script.validation import DEFAULT_ALLOWED_MODULES

SCRIPT = "def aggregate_data(data):\n  return data\n"


def test_config_requires_exactly_one_origin() -> None:
  with pytest.raises(ValidationError):
    ScriptDataProcessorConfig()
  with pytest.raises(ValidationError):
    ScriptDataProcessorConfig(content=SCRIPT, source="https://example.com/s.py")


def test_allowed_modules_extend_defaults() -> None:
  config = ScriptDataProcessorConfig(content=SCRIPT, allowed_modules={"custom_module"})

  assert config.allowed_modules == DEFAULT_ALLOWED_MODULES | {"custom_module"}


def test_auth_requires_remote_source() -> None:
  with pytest.raises(ValidationError):
    ScriptDataProcessorConfig(content=SCRIPT, auth={"type": "token", "token": "t"})


def test_http_requires_opt_in() -> None:
  with pytest.raises(ValidationError):
    ScriptDataProcessorConfig(source="http://example.com/s.py")
  ScriptDataProcessorConfig(source="http://example.com/s.py", allow_http=True)
