from collections.abc import Generator, Sequence
from os import environ
from pathlib import Path

from pydantic import Field
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

# AGGREGATOR_NAME_REGEX = re.compile(r"\.?aggregator", re.IGNORECASE)


def build_config_file_names(file_extension: str, test_aggregator_name: str = "") -> Generator[Path]:
  """Build possible config file names based on the file extension and aggregator name.

  Args:
      file_extension (str): The file extension for the config files (e.g., "yaml", "json").
      test_aggregator_name (str, optional): The aggregator name to use for testing purposes. Defaults to "".

  Yields:
      Path: The possible config file paths.
  """
  aggregator_name = environ.get("AGGREGATOR_NAME", test_aggregator_name)
  aggregator_name = (
    aggregator_name.replace(r"\.?aggregator", "") if aggregator_name else aggregator_name
  )

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
      YamlConfigSettingsSource(
        settings_cls, yaml_file=POSIBLE_CONFIG_FILE_NAMES_YAML, deep_merge=True
      ),
      JsonConfigSettingsSource(
        settings_cls, json_file=POSIBLE_CONFIG_FILE_NAMES_JSON, deep_merge=True
      ),
      TomlConfigSettingsSource(
        settings_cls,
        toml_file=POSIBLE_CONFIG_FILE_NAMES_TOML,
        toml_table_header=("aggregator",),
        deep_merge=True,
      ),
    )

  name: str = Field(description="The name of the aggregator")
  description: str = Field(default="", description="Description of the aggregator purpose")
