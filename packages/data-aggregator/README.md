# data-aggregator

Core runtime package for Data Aggregator.

The following functionalities should be implemented

- loading the provider plugins
- loading the data from the sources with the provided plugins
- loading the data processing
- execute the data processing
- Data processing with a provided python script file or script text in the configuration
- Data Processing with a provided duckdb sql script file or script text in the configuration
- Data Processing with a predefined function in the aggregator
  - pipe: take the first or named key from the loaded data and pass it to the output
  - merge: define a target source and merge the other source into the target source, defined by config
  - filter: like pipe  but with a static filter condition, defined by config (can be a config property of the pipe)
- store the processed data with the provided storage plugin
- the processing should be async

The aggregator flow is as follows:
- load the general configuration
- load all provided plugins
- for each source in the configuration:
  - try to load the plugin based on the provider type
  - load the provider configuration by the source provider type and name configuration
  - parse the provider configuration with the provider configuration class
  - parse the source configuration with the provider source configuration class
  - call the provider loader with the parsed source configuration, and provider configuration
  - store the loaded data in the memory
- pass the loaded data to the processor
  - if the processor is python, load the py script and execute it with the loaded data
  - if the processor is duckdb, load the sql script and execute it with the loaded data
  - if the processor is a predefined function, execute the configured function with the loaded data
- for each target in the configuration:
  - try to load the plugin based on the provider type
  - load the provider configuration by the target provider type and name configuration
  - parse the provider configuration with the provider configuration class
  - parse the target configuration with the provider target configuration class
  - call the provider store with the parsed target configuration, and provider configuration, and processed data
- if the aggregator messaging is configured, send a message that the aggregator has finished processing and store the data.

> Note: the messaging should be an optional module, that can be enabled and configured in the config.