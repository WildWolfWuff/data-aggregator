# data-aggregator-core

Contains shared code for the data-aggregator and all plugins.

The following functionalities should be provided by this package:

- Provide the basic configuration that is used by every package in the data-aggregator workspace
  - loading the configuration from yaml/json file, environment variable or cli arguments (use pydantic for configuration definition)
  - basic configuration like: aggregator name, version
  - Secret management for sensitive configuration values (like passwords, api keys, etc.)
- Monitoring support for the data-aggregator and the plugins (use opentelemetry)
  - tracing
  - metrics
  - logging
