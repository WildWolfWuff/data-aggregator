import pytest

from data_aggregator.provider.config import DataCollectorConfigBase, DataExporterConfigBase, DataProviderConfigBase
from data_aggregator.provider.core import (
  PROVIDER_API_VERSION,
  Capability,
  DataProvider,
  validate_provider_class,
)


class Cfg(DataProviderConfigBase):
  url: str = ""


class Both(DataProvider):
  provider_type = "both"
  config_model = Cfg
  capabilities = frozenset({Capability.COLLECT, Capability.EXPORT})

  async def collect(self, collector):
    return [1]

  async def export(self, data, exporter):
    return None


class CollectOnly(DataProvider):
  provider_type = "src"
  config_model = Cfg
  capabilities = frozenset({Capability.COLLECT})

  async def collect(self, collector):
    return [1]


def test_valid_classes() -> None:
  assert validate_provider_class(Both) == []
  assert validate_provider_class(CollectOnly) == []


def test_not_a_provider() -> None:
  assert "not a DataProvider" in validate_provider_class(object)[0]
  assert (
    validate_provider_class(
      DataProvider(  # type: ignore[abstract]
        "n", Cfg()
      ).__class__
    )
    != []
  )


def test_missing_attributes() -> None:
  class Empty(DataProvider):
    pass

  errors = validate_provider_class(Empty)
  assert len(errors) == 3


def test_api_version_mismatch() -> None:
  class Old(CollectOnly):
    provider_type = "old"
    api_version = PROVIDER_API_VERSION + 1

  assert any("api_version" in e for e in validate_provider_class(Old))


def test_bad_config_model() -> None:
  class Bad(CollectOnly):
    provider_type = "bad"
    config_model = dict  # ty: ignore[invalid-assignment]

  assert any("config_model" in e for e in validate_provider_class(Bad))


def test_empty_capabilities() -> None:
  class NoCaps(CollectOnly):
    provider_type = "nocaps"
    capabilities = frozenset()

  assert any("non-empty" in e for e in validate_provider_class(NoCaps))


def test_declared_but_not_overridden() -> None:
  class Liar(CollectOnly):
    provider_type = "liar"
    capabilities = frozenset({Capability.COLLECT, Capability.EXPORT})

  assert any("does not override export" in e for e in validate_provider_class(Liar))


def test_overridden_but_not_declared() -> None:
  class Sneaky(Both):
    provider_type = "sneaky"
    capabilities = frozenset({Capability.COLLECT})

  assert any("does not declare 'export'" in e for e in validate_provider_class(Sneaky))


@pytest.mark.asyncio
async def test_default_methods_raise() -> None:
  provider = CollectOnly("n", Cfg())
  with pytest.raises(NotImplementedError):
    await provider.export(None, DataExporterConfigBase(provider="a:b"))
  assert await provider.collect(DataCollectorConfigBase(provider="a:b")) == [1]
  await provider.close()
