# data-aggregator-provider-http

This package provides a HTTP data provider for the data-aggregator.

The following functionalities should be implemented:

- Provider configuration for HTTP server, source and target.
- The HTTP server should be configurable with the following options:
  - host:(port)
  - ssl (optional)
    - cert
    - key
    - etc..
  - authentication (optional)
- The source should be configurable with the following options:
  - path
  - method (GET, POST)
  - headers (optional, dict)
  - body (optional for POST, dict)
  - query parameters (optional, dict)
  - timeout (optional, default to 2 minutes)
  - content type (optional, map to pandas dataframe read functions)
  - json options
    - orient (optional, default to 'records')
- The target should be configurable with the following options:
  - path (source property of plugin base source configuration class)
  - method (GET, POST, PUT)
  - headers (optional)
  - timeout (optional, default to 2 minutes)