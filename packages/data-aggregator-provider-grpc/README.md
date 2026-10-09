# data-aggregator-provider-grpc

This package provides a gRRPC provider for the data-aggregator.

The following functionalities should be implemented:

- Get the calculated data by a gRPC streaming api or default gRPC api
- Define the gRPC service message in the configuration file (source and target)
- The defined gRPC should be parsed and used to generate the gRPC service on the fly
