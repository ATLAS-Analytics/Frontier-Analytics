# Frontier Data

## Introduction
This package aims to extract and analyze ATLAS Frontier logging data stored in ElasticSearch servers. 

## Overview
This project contains different subpackages:

#### 1)- DataExtraction:
This package contains the following scripts:
- LoadEsData: for extracting Frontier logs from ElasticSearch server (specified in the configuration file).
- parseQueries: for completing logs data by adding the missing COOL parameters 


#### 2)- Config:
App configuration parameters.

##### COOLR script:
In order to keep COOLR file updated, this script allows the application to connect with COOLR service and extract the new COOL information.

#### 3)- CachingEfficiency:
In order to calculate the caching efficiency of Frontier system for a given folder, CachingEfficiency contains methods that compare between queries and extract the effective used payloads.

For further information about COOLR service, consult this page: https://gitlab.cern.ch/formica/coolR









