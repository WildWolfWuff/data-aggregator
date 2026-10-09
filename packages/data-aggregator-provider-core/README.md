# data-aggregator-provider-core

Core provider interfaces for Data Aggregator.
A data provider is the interface to a data source or target. 
The base configuration of a provider defines the basic connection/location of a data source or target. 
Each provider can have a source and/or target configuration.
The source is the actual place on a provider where the data is loaded from. 
The target is the actual place on a provider where the data is saved to.

The provider configuration is separated into the actual provider configuration, 
a list of source configurations and a list of target configurations.

the source and target configuration are mapped to the provider configuration by a unique name, 
so a provider can have multiple sources and targets.
The plugin should be a generic abstract class that defines the interface for a provider.
A provider defines functions for loading and saving data.
The provider must also provide the configuration types for the provider, source and target configuration, 
so the aggregator can parse and validate the given configuration against the provider configuration.

The following functionalities should be provided by this package:
- Plugin should give the information about the provider:
  - name: unique name of the provider (provider type in the configuration)
  - version: version of the provider
  - description: description of the provider
  - capabilities: list of capabilities of the provider (like `load`, `save`, `check`)
  - the configuration classes for the settings parser
  - a Loader implementation of a loader of the provider (if the provider has the capability `load`)
  - a Saver implementation of a saver of the provider (if the provider has the capability `save`)
  - a Check implementation of a health check of the provider, this independent of any source or target (if the provider has the capability `check`)
- Definition of a `loader` interface (function) for loading data from a source (takes the source configuration and provider configuration | returns a pandas DataFrame)
- Definition of a `saver` interface (function) for saving data to a target (takes a pandas DataFrame, the target configuration and provider configuration | returns a save result)
- Definition of a `check` interface (function) for checking the health of the provider (takes the provider configuration | returns a boolean or a health check result)
- The loader and saver should be async functions.
- The base data provider configuration should have:
  - name: unique name of the provider (extracted from the configuration dict key in the specific provider type section)
  - health check definition (optional)
- Source and target configuration definition
- Both source and target configuration should have:
  - name: unique name of the source
  - provider: object or string reference to a provider in the provider config section (`type:name` or `{"type":"type", "name":"name"}`) 
  - columns: a list of columns to load from the source (optional, if not provided all columns should be loaded)
    - this can be a list of column names or a list of dictionaries with the following keys:
      - name: name of the column
      - type: type of the column (optional, if not provided the type should be inferred from the data)
    - short form with type `name:type`
- Source definition should have always:
  - source: the actual source location name (like a file path, url, table name, etc.)
  - rename: a dictionary of the columns original name to new name (optional)
  - index: list of columns to set as index (optional)
- Target definition should have always:
  -  target: the actual target location name (like a file path, url, table name, etc.)
  - mode: the mode to store the data (like `overwrite`, `append`)
  - distinct: boolean or string or list of string, distinct all or specific column or columns
- Errors for each provider will be handled by the aggregator loading and saving logic.