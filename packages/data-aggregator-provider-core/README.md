# data-aggregator-provider-core

Provider interface and plugin loading for the Data Aggregator.

A **data provider** is a plugin that can collect data from a source, export data to a target, or both.
Plugin authors only depend on this package.

## Concepts

| Term | Meaning |
|---|---|
| provider type | Identifier of a plugin (`DataProvider.provider_type`), e.g. `http` |
| provider name | A configured instance of a type, e.g. `source1` |
| reference | `type:name`, used by collectors and exporters to select a provider instance |
| capability | `Capability.COLLECT`, `Capability.EXPORT` or both |

## Implementing a plugin

A plugin is a normal Python package that provides one `DataProvider` subclass and registers it as an entry point.

### 1. Provider class

```python
# my_plugin/provider.py
import pandas as pd

from data_aggregator.provider import Capability, DataProvider
from data_aggregator.provider.config import (
  DataCollectorConfigBase,
  DataExporterConfigBase,
  DataProviderConfigBase,
)


class CsvConfig(DataProviderConfigBase):
  """Validated provider configuration (`providers.csv.<name>` in the aggregator config)."""

  directory: str


class CsvProvider(DataProvider):
  provider_type = "csv"
  config_model = CsvConfig
  capabilities = frozenset({Capability.COLLECT, Capability.EXPORT})

  config: CsvConfig

  async def collect(self, collector: DataCollectorConfigBase) -> pd.DataFrame:
    return pd.read_csv(f"{self.config.directory}/{collector.source}")

  async def export(self, data: pd.DataFrame, exporter: DataExporterConfigBase) -> None:
    data.to_csv(f"{self.config.directory}/{exporter.target}", index=False)

  async def close(self) -> None:
    """Optional: release connections, file handles, ..."""
```

Rules (checked at startup by `validate_provider_class`):

- `provider_type`, `config_model` and `capabilities` are required; `api_version` defaults to the current interface version.
- `config_model` must subclass `DataProviderConfigBase`.
- `capabilities` must not be empty. Declare `COLLECT` only if you override `collect()`, and `EXPORT` only if you override `export()`.
- `provider_type` must be unique across all loaded plugins and equal to the entry point name.

You can use the same check in your plugin's own tests:

```python
from data_aggregator.provider import validate_provider_class
from my_plugin.provider import CsvProvider


def test_contract():
  assert validate_provider_class(CsvProvider) == []
```

### 2. Register the entry point

```toml
# pyproject.toml of the plugin
[project]
name = "my-plugin"
version = "1.0.0"
dependencies = ["data-aggregator-provider-core", "pandas"]

[project.entry-points."data_aggregator.providers"]
csv = "my_plugin.provider:CsvProvider"   # name must equal provider_type
```

### 3. Build

```sh
uv build --wheel      # creates dist/my_plugin-1.0.0-py3-none-any.whl
```

## Installing plugins

The aggregator loads plugins at startup. Choose any of the options below.

### Option A: install at startup (`plugins.packages`)

List the packages in the aggregator configuration. They are installed into `install_dir` with `uv pip install --target`
(`pip` is the fallback) and are skipped on later starts as long as the plugin configuration is unchanged.

```yaml
plugins:
  install_dir: /plugins/site-packages   # must be writable
  packages:
    - my-plugin==1.0.0                                   # from an index
    - /plugins/wheels/other_plugin-2.0.0-py3-none-any.whl # local wheel
    - requirement: https://example.com/third-2.0.0-py3-none-any.whl
      sha256: 0123abcd...                                 # optional integrity pin
  # index_url: https://pypi.example.com/simple
  # offline installs:
  # no_index: true
  # find_links: [/plugins/wheels]
```

The installed `data-aggregator*` packages are used as constraints, so a plugin can not replace the core packages.
If any package fails to install, the aggregator aborts.

### Option B: mounted plugin directory (`plugins.plugin_dir`)

A directory with ready-to-use packages (including `*.dist-info`, e.g. created by `pip install --target`) that is added
to the import path. Nothing is installed.

```yaml
plugins:
  plugin_dir: /plugins/ready
```

### Option C: explicit import path (`plugins.import_paths`)

For quick local experiments; the module must be importable.

```yaml
plugins:
  import_paths:
    - my_plugin.provider:CsvProvider
```

### Option D: bake into the image

```dockerfile
FROM data-aggregator
RUN pip install my-plugin==1.0.0
```

### Restrict loaded plugins

```yaml
plugins:
  allowlist: [csv, http]   # entry point names; other installed plugins are ignored
```

## Using a plugin

Configure provider instances under `providers.<type>.<name>`, then reference them as `type:name` from collectors and
exporters. Settings are read from `aggregator.yaml` (working directory, `~/.config/aggregator`, `/etc/aggregator`),
JSON/TOML files, environment variables with the `AGGREGATOR_` prefix, or CLI arguments.

```yaml
name: my.aggregator

plugins:
  packages:
    - /plugins/wheels/my_plugin-1.0.0-py3-none-any.whl

providers:
  csv:                      # provider type
    local:                  # provider name -> reference "csv:local"
      directory: /data

collectors:
  customers:
    provider: csv:local
    source: customers.csv

exporters:
  result:
    provider:
      type: csv             # long form of "csv:local"
      name: local
    target: result.csv
```

Startup validation (the aggregator stops with a list of all problems if any check fails):

- plugin import errors, interface violations, `api_version` mismatches or duplicate provider types
- failed package installation
- provider settings that do not match the plugin's `config_model`
- references to unknown providers
- a collector that uses a provider without `COLLECT`, or an exporter that uses a provider without `EXPORT`

## Running in a container

```sh
docker run \
  -v ./aggregator.yaml:/etc/aggregator/aggregator.yaml:ro \
  -v ./wheels:/plugins/wheels:ro \
  -v plugin-cache:/plugins/site-packages \
  data-aggregator
```

- Mount a writable volume at `install_dir` so installed plugins survive restarts.
- For air-gapped environments put the wheels (and their dependencies) in a mounted directory and set
  `no_index: true` with `find_links`.
- Plugins run in the aggregator process with its permissions. Only install plugins you trust, prefer pinned versions
  and `sha256` pins, mount plugin directories read-only and run the container as a non-root user.
