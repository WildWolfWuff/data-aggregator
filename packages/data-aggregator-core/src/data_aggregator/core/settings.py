import re
from collections.abc import Generator, Sequence
from os import environ
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import (
  BaseSettings,
  CliSettingsSource,
  JsonConfigSettingsSource,
  PydanticBaseSettingsSource,
  SettingsConfigDict,
  TomlConfigSettingsSource,
  YamlConfigSettingsSource,
)

AGGREGATOR_ENV_PREFIX = "AGGREGATOR_"

DEFAULT_SETTINGS_CONFIG = {
  "env_prefix": AGGREGATOR_ENV_PREFIX,
  "cli_parse_args": True,
  "secrets_dir": ("/var/run", "/run/secrets"),
}


def build_config_file_names(file_extension: str, test_aggregator_name: str = "") -> Generator[Path]:
  """Build possible config file names based on the file extension and aggregator name.

  Args:
      file_extension (str): The file extension for the config files (e.g., "yaml", "json").
      test_aggregator_name (str, optional): The aggregator name to use for testing purposes.
      Defaults to an empty string.

  Yields:
      Path: The possible config file paths.
  """
  aggregator_name = environ.get("AGGREGATOR_NAME", test_aggregator_name)
  aggregator_name = aggregator_name.replace(r"\.?aggregator", "") if aggregator_name else aggregator_name

  for config_dir in (Path.cwd(), Path("~/.config/aggregator"), Path("/etc/aggregator")):
    paths = [config_dir / f"aggregator.{file_extension}"]
    if aggregator_name:
      paths += [
        config_dir / f"{aggregator_name}.aggregator.{file_extension}",
        config_dir / f"{aggregator_name.replace('.', '/')}.aggregator.{file_extension}",
      ]
    yield from (p for p in paths if p.exists())


POSIBLE_CONFIG_FILE_NAMES_YAML: Sequence[Path] = list(build_config_file_names("yaml")) + list(
  build_config_file_names("yml")
)
POSIBLE_CONFIG_FILE_NAMES_JSON: Sequence[Path] = list(build_config_file_names("json"))
POSIBLE_CONFIG_FILE_NAMES_TOML: Sequence[Path] = list(build_config_file_names("toml"))

# aggregator names: name.space.ag_name
AGGREGATOR_NAME_REGEX = re.compile(r"^(?P<name>(?:(?:\w+\.)*(?:\w+)))$")
"""
Regular expression to match an aggregator name in the format 'namespace.name'. 
Use . to create namespace hierarchy.
"""

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
      m = AGGREGATOR_PROVIDER_REF_REGEX.match(v)
      if not m:
        raise ValueError("Invalid provider string format, expected 'type:name'")
      g = m.groupdict()
      return DataProviderRefConfig(**g)
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


class DataExporterConfigBase(BaseModel):
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


class AggregatorSettingsBase(BaseSettings):
  model_config = SettingsConfigDict(**DEFAULT_SETTINGS_CONFIG)

  @classmethod
  def settings_customise_sources(
    cls,
    settings_cls: type[BaseSettings],
    init_settings: PydanticBaseSettingsSource,
    env_settings: PydanticBaseSettingsSource,
    dotenv_settings: PydanticBaseSettingsSource,
    file_secret_settings: PydanticBaseSettingsSource,
  ) -> tuple[PydanticBaseSettingsSource, ...]:
    return (
      init_settings,
      env_settings,
      dotenv_settings,
      file_secret_settings,
      CliSettingsSource(settings_cls),
      YamlConfigSettingsSource(settings_cls, yaml_file=POSIBLE_CONFIG_FILE_NAMES_YAML, deep_merge=True),
      JsonConfigSettingsSource(settings_cls, json_file=POSIBLE_CONFIG_FILE_NAMES_JSON, deep_merge=True),
      TomlConfigSettingsSource(
        settings_cls,
        toml_file=POSIBLE_CONFIG_FILE_NAMES_TOML,
        toml_table_header=("aggregator",),
        deep_merge=True,
      ),
    )

  name: Annotated[str, Field(description="The name of the aggregator")]
  description: Annotated[str, Field(default="", description="Description of the aggregator purpose")]

  @field_validator("name")
  def validate_name(cls, value: str) -> str:
    """Validate the aggregator name against the expected format."""
    m = AGGREGATOR_NAME_REGEX.match(value)
    if not m:
      raise ValueError(f"Invalid aggregator name: {value}")
    return str(m.group("name"))


class AggregatorDataSettings(AggregatorSettingsBase):
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
