  # data-aggregator-server

This package provide a service to run the data-aggregator as a server. 

The following functionalities should be implemented:

- Health check endpoints to check the status of the service
- Provide the calculated data by a REST or dynamic grpc streaming api
- Authentication support for the api endpoints
  - simple api key authentication
  - oauth2 authentication
- Docker support, run the Aggregator as a Docker container
- Endpoint to trigger the data processing
