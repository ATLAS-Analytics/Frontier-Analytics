# App Configuration 

## Configuration File
The configuration file allows users to set the application parameters values. These parameters are:  
- ElasticSearch server host address and port
- ElasticSearch user and password for authentification
- ElasticSearch Frontier and caching efficiency indices
- Coolr static file path used for parsing queries
- The maximum number of queries to retrieve at once from ElasticSearch server

## Settings Class
The configuration parameters are used in different modules by instantiating Settings class. 