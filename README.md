# Analytics

## Introduction
This project contains:

    -  "FrontierData" package that aims to extract and analyze ATLAS Frontier logging data stored in ElasticSearch servers. 
    -  "Plots" package that represents a set of filters (based on Spark SQL) for plotting data. 
    -   Celery service for running asynchronous tasks 


## Requirements 
This is a Python package that uses Python3.6+.
To install the required modules:

``` python
 pip install -r requirements.txt
```
You need to install coolr package, please follow the instructions in this page:
https://gitlab.cern.ch/formica/coolR/tree/master/coolR-client/python

Make sure you installed a Redis service on your machine and that it's running correctly.

## Configuration
For the first use, you need to create a configuration file. Please follow these steps:
``` python
    from FrontierData.Config import settings
    
    # define config parameters 
    coolr_file = path to coolr static file 
    ES_address = IP address of ES server 
    ES_port = ES server port
    ES_USER = ES user
    ES_PSWD = ES password
    ES_INDEX = frontier indices name
    ES_CachingEfficiency_Index = frontier caching efficiency index name
    COOLR_host = COOLR host name:port/
    limit_queries = 5000000
    db_instances = CONDBR2 OFLP200 COMP200  MONP200

    
    #create the config file 
    settings.createConfigFile(coolr_file_path,ElasticSearch_address,ElasticSearch_port, ES_user, ES_psswd, ES_index, ES_Caching_Efficiency, COOLR_host, max_queries,db_instances, config_path)
```
After this, you can configure your application by pointing your settings to this configuration file 

``` python
 stg = settings.Settings('./configuration.txt')
```

## FrontierData package installation
you can install 'FrontierData' package, using setuptools:

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

After you can import the following modules:

``` python
 import FrontierData
```

## Celery service 

Celery is a service used for running python asynchronous tasks. Flask can now hold multiple users requests since the long tasks are running in the background. 

The docker file contains the Celery deployment steps. This deployment is based on celery-python image pulled from: https://cloud.docker.com/u/millissa/repository/docker/millissa/celery-python

To run Celery locally, from this directory run the following command:


```sh
export CONFIG_FILE=PATH TO ANALYTICS CONFIG File 
celery -A celery_tasks worker --loglevel=info
```

