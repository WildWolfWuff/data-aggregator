# Data Aggregator

This project is a generic table data processing tool.

Aggregators should be able to be chained together to create a data processing pipeline.

The aggregator can load data from different sources, process them with a given script (python/sql) or simple built-in functions and store them to one or more target destinations.
The data processing can be extended by plugins and the data loading and saving can be extended by data provider plugins.

The script looks like
```python
def process(data: dict[str, pandas.DataFrame]) -> pandas.DataFrame:
  # process the data and return the result
  return data["source1"].merge(data["source2"], on="id")
```
The script gets a dictionary with the loaded data from the sources and should return a single pandas DataFrame with the processed data.
The keys in the data dictionary are the names of the sources that are defined in the configuration.

configuration example:
```yaml
aggregator: "name.of.my.aggregator"
providers:
  http: # type of the provider
    source1:
      source: "https://example.com/data1.csv"
      format: "csv"
    source2:
      source: "https://example.com/data2.json"
      format: "json"
  sql: # type of the provider
    ms_sql_source: # name of the provider
      source: "my_table" 
      connection_string: "mssql+pyodbc://user:password@localhost"
    target: # name of the provider
      target: "my_table"
      connection_string: "postgresql://user:password@localhost"
api:
  auth:
    type: "oauth"
  # other api configurations
```

## Features

**Core**
- Generic data processing based on a given script (python / sql)
- Extendable processing with plugins
- Extendable data loading and saving by data provider plugins (include basic plugins for http, sql, local files or static values)
- User-friendly configuration by yaml/json files, environment variable or cli arguments
- open telemetry support (tracing, metrics, logging)

**Additional**
- Container support, run the Aggregator as a Docker container
- Data-Api: Provide the calculated data by a REST or dynamic grpc streaming api
- Feature flag support: Enable or disable features by configuration
- Messaging support: Send messages to a message broker (like mqtt, kafka, rabbitmq)
  - Startup and shutdown messages to indicate the status of the aggregator (every mode)
  - Send messages to a message broker when the data is processed and stored (every mode)
  - Receive messages from a other completed aggregator run that triggers the current aggregator run for chain aggregators together (server mode). 


## Plugins

Data providers are plugins that can collect and/or export data. See
[packages/data-aggregator-provider-core/README.md](packages/data-aggregator-provider-core/README.md) for how to
implement, install and configure them.

## Project structure

The repository is a `uv` workspace. Each package in `packages/` has its own
`pyproject.toml` and can be built independently.

source files:

- `packages/data-aggregator/`: core runtime
- `packages/data-aggregator-cli/`: CLI entry point
- `packages/data-aggregator-core/`: shared code for other packages
- `packages/data-aggregator-provider-core/`: base provider interfaces
- `packages/data-aggregator-provider-sql/`: SQL data provider
- `packages/data-aggregator-provider-http/`: HTTP data provider
- `packages/data-aggregator-provider-file/`: local file data provider

additional files:
- `.github/workflows/`: CI/CD pipelines (TODO: add CI/CD pipelines)
- `docs/`: documentation (TODO: add documentation)
- `.devcontainer/`: development container configuration (TODO: add dev container support)

## Development

Install all workspace packages into the development environment and run the CLI:

```sh
uv sync --all-packages
uv run --package data-aggregator-cli data-aggregator
```
## Development

Tooling (Ruff, ty, pytest, pre-commit) is configured once in the root `pyproject.toml` and applies to all packages in `packages/`.

```shell
uv sync                    # installs workspace packages and dev tools
uv run pre-commit install  # install the git hooks
uv run ruff check .        # lint
uv run ruff format .       # format
uv run ty check            # type check
uv run pytest              # unit tests (packages/*/tests)
uv run pre-commit run --all-files  # run hooks on all files
```
