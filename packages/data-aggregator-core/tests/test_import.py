import importlib


def test_package_is_importable() -> None:
  core = importlib.import_module("data_aggregator.core")

  assert core.__name__ == "data_aggregator.core"
  assert set(core.__all__) == {
    "AggregatorCollectorConfiguration",
    "AggregatorDataSettings",
    "AggregatorExporterConfiguration",
    "AggregatorProviderConfiguration",
    "AggregatorSettingsBase",
    "CollectorName",
    "DataCollectorConfigBase",
    "DataCoreConfig",
    "DataExporterConfigBase",
    "DataProviderConfigBase",
    "DataProviderRef",
    "DataProviderRefConfig",
    "ExporterName",
    "ProviderConfig",
    "ProviderName",
    "ProviderType",
  }
