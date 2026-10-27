import re
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

AGGREGATOR_PROVIDER_REF_REGEX = re.compile(r"^(?P<type>[^:]+):(?P<name>.+)$")
"""Regular expression to match an aggregator provider reference in the format 'type:name'."""

type ProviderType = str
"""Type of the data provider."""

type ProviderName = str
"""Name of the data provider."""


class DataProviderConfigBase(BaseModel):
  """Base class for data provider configuration."""

  pass


class DataProviderRefConfig(BaseModel):
  """
  Configuration for a data provider reference.
  This can be used to reference a data provider by its type and name.
  """

  type: Annotated[
    ProviderType,
    Field(description="The type of the data provider"),
  ]
  name: Annotated[
    ProviderName,
    Field(description="The name of the data provider"),
  ]


type DataProviderRef = str | DataProviderRefConfig
"""Data provider reference type alias."""


class DataCoreConfig(BaseModel):
  provider: Annotated[
    DataProviderRef,
    Field(description="The reference to the data provider"),
  ]

  @field_validator("provider")
  def validate_provider(cls, v: DataProviderRef) -> DataProviderRefConfig:
    if isinstance(v, str):
      if m := AGGREGATOR_PROVIDER_REF_REGEX.match(v):
        g = m.groupdict()
        return DataProviderRefConfig(**g)
      raise ValueError("Invalid provider string format, expected 'type:name'")
    return v


class DataCollectorConfigBase(DataCoreConfig):
  """Base class for data collector configuration."""

  source: Annotated[
    str,
    Field(
      default="",
      description="The source for the data collector; defaults to the name of the source if empty",
    ),
  ]


class DataExporterConfigBase(DataCoreConfig):
  """Base class for data exporter configuration."""

  target: Annotated[
    str,
    Field(
      default="",
      description="The target for the data exporter; defaults to the name of the target if empty",
    ),
  ]


type ProviderConfig = object | DataProviderConfigBase

type AggregatorProviderConfiguration = dict[ProviderType, dict[ProviderName, ProviderConfig]]

type CollectorName = str
"""Aggregator collector name alias."""
type AggregatorCollectorConfiguration = dict[CollectorName, object | DataCollectorConfigBase]

type ExporterName = str
"""Aggregator exporter name alias."""
type AggregatorExporterConfiguration = dict[ExporterName, object | DataExporterConfigBase]


class PluginSpec(BaseModel):
  """A plugin package to install: a requirement, local wheel path or URL, optionally hash pinned."""

  name: Annotated[str, Field(description="Requirement (name==1.0), wheel path or URL")]
  sha256: Annotated[str | None, Field(default=None, description="Expected sha256 of the artifact")]


class PluginsConfig(BaseModel):
  packages: Annotated[list[PluginSpec], Field(default_factory=list, description="Plugins installed at startup")]
  install_dir: Annotated[
    Path, Field(default=Path("/plugins/site-packages"), description="Target directory for installed plugins")
  ]
  plugin_dir: Annotated[
    Path | None, Field(default=None, description="Additional directory with ready-to-use plugin packages")
  ]
  index_url: Annotated[str | None, Field(default=None, description="Alternative package index")]
  no_index: Annotated[bool, Field(default=False, description="Do not use an index (offline installs)")]
  find_links: Annotated[list[str], Field(default_factory=list, description="Locations to search for wheels")]
  import_paths: Annotated[
    list[str], Field(default_factory=list, description="Explicit 'module:Class' provider classes")
  ]
  allowlist: Annotated[
    list[str] | None, Field(default=None, description="If set, only these entry point names are loaded")
  ]

  @field_validator("packages", mode="before")
  @classmethod
  def _coerce_specs(cls, v: object) -> object:
    if isinstance(v, list):
      return [{"name": i} if isinstance(i, str) else i for i in v]
    return v


class AggregatorProviderConfig(BaseModel):
  providers: Annotated[
    AggregatorProviderConfiguration,
    Field(description="The providers configuration"),
  ]
  collectors: Annotated[
    AggregatorCollectorConfiguration,
    Field(description="The collectors configuration"),
  ]
  exporters: Annotated[
    AggregatorExporterConfiguration,
    Field(description="The exporters configuration"),
  ]

  plugins: Annotated[
    PluginsConfig,
    Field(default_factory=PluginsConfig, description="The plugins configuration"),
  ]
