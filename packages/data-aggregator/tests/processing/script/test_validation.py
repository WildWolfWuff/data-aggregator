import pytest

from data_aggregator.processing.script import ScriptValidationError
from data_aggregator.processing.script.validation import validate_script


@pytest.mark.parametrize(
  "script",
  [
    "import os\ndef aggregate_data(d):\n  return d",
    "from sys import path\ndef aggregate_data(d):\n  return d",
    "import os.path as p\ndef aggregate_data(d):\n  return d",
    "import subprocess\ndef aggregate_data(d):\n  return d",
    "def aggregate_data(d):\n  return __import__('os')",
    "def aggregate_data(d):\n  exec('1')\n  return d",
    "def aggregate_data(d):\n  return d.__class__",
    "import requests\ndef aggregate_data(d):\n  return d",
    "def other(d):\n  return d",
    "def aggregate_data(a, b):\n  return a",
    "def aggregate_data(:",
  ],
)
def test_validation_rejects(script: str) -> None:
  with pytest.raises(ScriptValidationError):
    validate_script(script)
