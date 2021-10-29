import pyarrow.parquet as pq
from .CoolrServices import *


class Settings:

    def __init__(self, path):

        # read config file and extract {ES_address, coolr_file, limit_queries,coolr_server address, db_instances}
        settings_parameters = self.readInputConfig(path)

        # coolr_file : is a static file used for saving COOl parameters
        self.coolr_file = settings_parameters['coolr_file']

        # set elasticsearch server address
        self.es_server = settings_parameters['ES_address']
        self.es_port = int(settings_parameters['ES_port'])

        # set elasticsearch user and password
        self.es_user = settings_parameters['ES_USER']
        self.es_pswd = settings_parameters['ES_PSWD']

        # set elqsticsearch caching efficiency index
        self.cachingEfficiency_index = settings_parameters['ES_CachingEfficiency_Index']

        # set elasticsearch index
        self.frontier_index = settings_parameters['ES_INDEX']

        # set COOLR host address
        self.coolr_server = settings_parameters['COOLR_host']

        # spark session variables
        #self.spark = SparkSession.builder.master("local[*]").appName("FrontierAnalytics").config("spark.some.config.option","some-value").getOrCreate()

        # the maximum number of queries that can be retrieved at once from ES server
        self.limit = int(settings_parameters['limit_queries'])

        # extract db_instances
        self.db_list = settings_parameters["db_instances"]

        # save the coolr file in hashmap structures
        self.CoolrDataHashmap, self.hashmapNodes, self.hashmapTags, self.hashmapNodesID, self.hashmapTagsID = self.CreateHashMapForCoolrFile()

    def readInputConfig(self, path):
        """
        This method import the configuation parameters from a config file
        :param config_file:
        :return: a dictionary of settings parameters
        """
        output_parameters = {}
        lines = [line.strip('\n') for line in open(path)]
        for line in lines:
            if line is not None:
                params = line.split(' = ')
                output_parameters[params[0]] = params[1]
        if 'db_instances' in output_parameters:
            db_instances = output_parameters['db_instances'].split()
            output_parameters['db_instances'] = db_instances
        return output_parameters

    def CreateHashMapForCoolrFile(self):
        """
        This method save the coolr file structure in a set of different hashmaps
        :return:  hashmapNodes, hashmapTags, hashmapNodesID, hashmapTagsID
        """
        print('Checking if the coolr file is in', self.coolr_file)
        if not os.path.exists(self.coolr_file):
            print('Not found. Reloading it.')
            client = CoolrClient(self)
            client.updateCoolrParquetFile(self)
        CoolrDataHashmap = {}
        hashmapNodesID = dict()
        hashmapTagsID = dict()
        hashmapNodes = dict()
        hashmapTags = dict()
        table = pq.read_table(self.coolr_file)
        pandas_df = table.to_pandas()
        dbs = set()
        db_schemas = set()
        for index, row in pandas_df.iterrows():
            if not row['db'] in dbs:
                dbs.add(row['db'])
                CoolrDataHashmap[row['db']] = {}
            if not (row['db'], row['schema']) in db_schemas:
                db_schemas.add((row['db'], row['schema']))
                CoolrDataHashmap[row['db']][row['schema']] = set()
            CoolrDataHashmap[row['db']][row['schema']].add(row['node'])
            hashmapNodes[(row['db'], row['schema'], row['node'])
                         ] = (row['node_id'], row['nodetime'])
            hashmapNodesID[(row['db'], row['schema'], row['node_id'])] = (
                row['node'], row['nodetime'])
            hashmapTagsID[(row['db'], row['schema'], row['node'],
                           row['tag_id'])] = row['tag']
            hashmapTags[(row['db'], row['schema'], row['node'],
                         row['tag'])] = row['tag_id']
        return CoolrDataHashmap, hashmapNodes, hashmapTags, hashmapNodesID, hashmapTagsID


def createConfigFile(coolr_file_path, ElasticSearch_address, ElasticSearch_port,  ElasticSearch_user, ElasticSearch_pswd, ElasticSearch_index, ElasticSearch_caching_index,  COOLR_host, max_queries,
                     db_instances, path):
    """
      create  a configuration file containing:
        coolr_file = Analytics/FrontierData/Files/coolr_all.parquet
        ES_address = es-data11.mwt2.org
        ES_port = 9200
        ES_USER = kibana user account
        ES_PSWD = Kibana user password
        ES_INDEX = Kibana index to use
        ES_CachingEfficiency_Index = ElasticSearch caching efficiency index
        COOLR_host = http://atlasfrontier08.cern.ch:8000/coolrapi
        limit_queries = 5000000
        db_instances = CONDBR2 OFLP200
    """
    config = {
        'coolr_file': coolr_file_path,
        'ES_address': ElasticSearch_address,
        'ES_port': ElasticSearch_port,
        'ES_USER': ElasticSearch_user,
        'ES_PSWD': ElasticSearch_pswd,
        'ES_INDEX': ElasticSearch_index,
        'ES_CachingEfficiency_Index': ElasticSearch_caching_index,
        'COOLR_host': COOLR_host,
        'limit_queries': max_queries,
        'db_instances': ' '.join(db_instances)
    }
    file = open(path, 'w+')
    for key, value in config.items():
        file.write(str(key) + ' = ' + str(value) + '\n')
    file.close()
