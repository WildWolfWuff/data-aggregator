import data_aggregator.provider as provider


def test_public_api_exported() -> None:
  assert set(provider.__all__) == {
    "PROVIDER_API_VERSION",
    "Capability",
    "DataProvider",
    "PluginLoadError",
    "PluginSpec",
    "PluginsConfig",
    "ProviderError",
    "ProviderRegistry",
    "validate_provider_class",
  }
  for name in provider.__all__:
    assert hasattr(provider, name)
