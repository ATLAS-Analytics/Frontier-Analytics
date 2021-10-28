# Frontier Analytics


## Introduction
This is a standalone application for monitoring ATLAS Frontier servers. This application allows experts to study the breaking points of ATLAS Frontier system by visualising and analyzing Frontier logging information stored in ElasticSearch chicago server.
For further information: 

“Frontier Kibana monitoring” twiki page: https://twiki.cern.ch/twiki/bin/view/AtlasComputing/FroNTier#Frontier_Kibana_Monitoring_Analy 

## Overview
This project is divided to three main components:

#### 1)- Back-end:
In order to study ATLAS Frontier system behaviour, the back-end application (Analytics project) goes through different stages:
- retrieve Frontier logging data from ElasticSearch Chicago server.
- Parse the different Frontier queries by using a COOLR static file containing the complementary data. 
- Calculate the caching efficiency for a given folder.

#### 2)- Flask REST Interface:
This project uses Flask/Celery technologies for running a REST web service. 

This service allows users to:
  - extract Frontier data and  save it into a parquet file in a shared storage space 
  - delete, download and upload a parquet file to the shared storage space 
  - visualize data using Plotly JS library (https://plot.ly/javascript/)
  - calculate the caching efficiency for a given parquet file and save the results in a CERN PostgresSQL DB instance 


To use the server locally, you need first to follow instructions under Analytics folder for running Celery server, then: 

Install Flask server requirements:

``` bash 
  pip install -r requirements.txt
``` 


In order to run the server, you need to:
  - create an ENV variable for indicating the settings file path:
``` bash
  export FrontierAnalyticsApp_SETTINGS=./settings.cfg
```
  - run Flask server :
``` bash
  python FrontierAnalyticsApp.py 
```

##### Flask configuration

you need to create a settings file "settings.cfg" to configure Flask server:

``` bash
    DEBUG = True
    SECRET_KEY = 
    UPLOAD_FOLDER = path to parquet directory
    ANALYTICS_CONFIG_FILE = path to Analytics config file
    STATUS = {'PENDING', 'PROGRESS'}

```


#### 3)- Front-end:
This is a Boostrap 4 template build with HTML/CSS, Jquery and JS. 
This template is based on SB Admin Dashborad model. 

Templates folder contains the HTML files and static folder contains CSS/JS files.



# To Do
* rework parseQueries.
   * for every row it checks twice if the coolr is on disk - completely remove it
   * everything that can be done in Pandas DataFrame should be done there.
