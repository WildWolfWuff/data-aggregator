# data-aggregator-provider-sql

This package provides a SQL data provider for the data-aggregator.

The following functionalities should be implemented:

- Provider configuration for SQL server, source and target.
- The Connection string can be provided as a connection string or as a dictionary with the following keys:
  - driver
  - server
  - database
  - username
  - password
  - port (optional, try to get the port by the driver if not provided)
- The password must be handled securely
- Use odbc
- Loading the data from a SQL source
- Storing the data to a SQL target
- The data should be loaded and stored as a pandas dataframe
- Asynchronous support for loading and storing the data
- Ths source configuration should extend the base with:
  - condition: Optional sql condition to filter the data ( a where clause, with or without the where keyword)
  - orderby: Optional sql order by clause (with or without the order by keyword)
  - distinct: Optional boolean to indicate if select distinct or not
- Loader must only use select statements to load the data.
- 
Test scenarios should include:

Support of different SQL drivers, including but not limited to:
- Microsoft SQL Server
- PostgreSQL
- MySQL
- Oracle
- SQLite
- Generic ODBC driver

Use test containers for testing the different sql drivers and databases.
