import pytest
from pydantic import ValidationError

from data_aggregator.provider.config import (
  AggregatorProviderConfig,
  DataCollectorConfigBase,
  DataCoreConfig,
  DataExporterConfigBase,
  DataProviderRefConfig,
)


def test_provider_ref_string_is_parsed() -> None:
  cfg = DataCoreConfig(provider="http:main")
  assert cfg.provider == DataProviderRefConfig(type="http", name="main")


def test_provider_ref_object_is_kept() -> None:
  cfg = DataCoreConfig(provider={"type": "http", "name": "main"})
  assert cfg.provider == DataProviderRefConfig(type="http", name="main")


def test_provider_ref_invalid_string() -> None:
  with pytest.raises(ValidationError, match="type:name"):
    DataCoreConfig(provider="invalid")


def test_collector_source_defaults_to_empty() -> None:
  assert DataCollectorConfigBase(provider="a:b").source == ""


def test_exporter_requires_provider() -> None:
  with pytest.raises(ValidationError):
    DataExporterConfigBase()  # ty: ignore[missing-argument]
  exporter = DataExporterConfigBase(provider="a:b")
  assert exporter.target == ""


def test_aggregator_provider_config() -> None:
  cfg = AggregatorProviderConfig.model_validate(
    {"providers": {"a": {"b": {"x": 1}}}, "collectors": {}, "exporters": {}, "plugins": {}}
  )
  assert cfg.providers["a"]["b"] == {"x": 1}
