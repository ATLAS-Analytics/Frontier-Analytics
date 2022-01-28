from .Config.CoolrServices import *
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import sys
import pyarrow.parquet as pq


def uniqueQueries(data, db, schema, folder):
    """

    :param data: pandas df is a set of queries for a specific folder/tag
    :param db, schema: db and schema name
    :param folder: node name
    :param tag: tag name , can be None
    :return: a set of different COOL queries (with iovs != 0) ordered by iov_since vs the total number of queries for a given folder
    """
    # remove duplicates values and unused queries
    totalQueries = 0
    dictData = {}
    for item in data.itertuples():
        if (item.since != -1 and item.nodefullpath == folder and item.schema == schema and item.db == db):
            totalQueries += 1
            if (item.sqlhash, item.since, item.until) in dictData:
                value = dictData[(item.sqlhash, item.since, item.until)]
                if value.cached and not item.cached:
                    dictData[(item.sqlhash, item.since, item.until)] = item
            else:
                dictData[(item.sqlhash, item.since, item.until)] = item
    # sort the unique queries based on
    uniqueData = list(dictData.values())
    uniqueSortedQueries = sorted(uniqueData, key=lambda item: item.since)
    return uniqueSortedQueries, totalQueries


def extractPayload_brutForce(uniqueQueries, settings):
    """
      This is a brut force method for finding payloads
    :param uniqueQueries: an ordered list of unique queries
    :param settings : in order to define the coolr client
    :return: a list of the different payloads retrieved by these queries.
    """
    coolr = CoolrClient(settings)
    payloads = list()
    for query in uniqueQueries:
        payload = coolr.getPayloads(query.db, query.schema, query.nodefullpath, query.tagname, 'none',
                                    query.since, query.until)
        if payload not in payloads:
            payloads.append(payload)
    return payloads


def extractPayload(uniqueQueries, settings):
    """
    :param uniqueQueries:  a set of different COOL queries (with iovs != 0) for a given folder/tag ordered by iov_since
    :return: a dictionary where an item is: { payload_iov : [payload , the count of queries requesting this payload]}
    """

    # create a coolr client
    coolr = CoolrClient(settings)
    # { iov_range : {correspondent payload, the count of queries retrieving this payload}}
    payloadIOVs = dict()
    sizeOfPayload = 0
    for query in uniqueQueries:
        # use COOLR service to get the payloads
        if not payloadIOVs:
            payload = coolr.getPayloads(
                query.db, query.schema, query.nodefullpath, query.tagname, 'none', query.since, query.until)
            iov = extractIovs(payload)
            print("payload:", payload)
            print("iov", iov)
            payloadIOVs[iov] = [payload, 1]
            if query.fsize != 0:
                sizeOfPayload = query.fsize / (1024 ** 2)

        else:
            # if the query iov is included in iov( o: since max , 1: until min)
            if int(query.until) <= iov[1]:
                # this query request the same payload
                payloadIOVs[iov][1] += 1
                if query.fsize != 0:
                    sizeOfPayload = query.fsize / (1024 ** 2)
            else:
                payload = coolr.getPayloads(
                    query.db, query.schema, query.nodefullpath, query.tagname, 'none', query.since, query.until)
                iov = extractIovs(payload)
                if query.fsize != 0:
                    sizeOfPayload = query.fsize / (1024 ** 2)
                payloadIOVs[iov] = [payload, 1]

        if sizeOfPayload == 0:
            sizeOfPayload = sys.getsizeof(str(payload)) / (1024**2)

    return payloadIOVs, sizeOfPayload


def extractIovs(paylaod):
    """
    :param paylaod: this is a COOL payload
    :return: the max iov_since , the min iov until and the nax iov until for the different channels inside the payload
    """
    data_array = paylaod.data_array
    iov_since, iov_until, max_iov_until = (None, None, None)
    for item in data_array:
        for key, value in item.items():
            if not iov_since and not iov_until:
                iov_since = value[1]
                iov_until = value[2]
            else:
                if value[1] > iov_since:
                    iov_since = value[1]
                if value[2] < iov_until:
                    iov_until = value[2]
                else:
                    max_iov_until = value[2]
    return (iov_since, iov_until, max_iov_until)


def calculateCachingEfficiency(parquetFile, Folders, settings):
    """
    :param parquetFile: containing parsed queries
    :param Folders: a list of tuples (db, schema, nodefullpath)
    :return: pandas df
    """
    # Outputs series
    results = {'folders': [], '#queries': [], '#uniqueQueries': [],
               '#Payloads': [], 'PayloadSize (MB)': []}
    # Read logs data
    #df = pd.read_parquet(parquetFile)
    df = pq.read_pandas(parquetFile, columns=['db', 'schema', 'nodefullpath', 'tagname',
                                              'since', 'until', 'fsize', 'sqlhash', 'cached']).to_pandas()
    # For every Folder , calculate caching efficiency
    for folder in Folders:
        db, schema, node = folder
        results['folders'].append(' , '.join(folder))
        # we need to keep only different queries
        uniquequeries, totalqueries = uniqueQueries(df, db, schema, node)
        results['#queries'].append(totalqueries)
        results['#uniqueQueries'].append(len(uniquequeries))
        # extract payloads using IOVs
        Payloads, size = extractPayload(uniquequeries, settings)
        results['#Payloads'].append(len(Payloads))
        results['PayloadSize (MB)'].append(size)
    return results


def caching_efficiency_data(settings):
    """
    extract caching efficiency data from  frontier/frontier_caching_efficiency index in ElasticSearch server
    :return:
    """
    # connect es
    es = Elasticsearch([{'host': settings.es_server, 'port': settings.es_port}],
                       scheme="https", http_auth=(settings.es_user, settings.es_pswd),
                       timeout=60, max_retries=10, retry_on_timeout=True)
    res = helpers.scan(es, query={}, index=settings.cachingEfficiency_index, timeout=30)
    output = []
    for r in res:
        output.append(r['_source'])
    return output


def write_caching_efficiency_data(df, data, settings, SparkSql):
    try:
        # connect to elasticsearch
        es = Elasticsearch([{'host': settings.es_server, 'port': settings.es_port}],
                           scheme="https", http_auth=(settings.es_user, settings.es_pswd),
                           timeout=60, max_retries=10, retry_on_timeout=True)
        # write the data into elastic search
        for i in range(len(data['folders'])):
            doc = {
                "folder": data['folders'][i],
                "payloadsize": data['PayloadSize (MB)'][i],
                "#queries": data['#queries'][i],
                "#differentqueries": data['#uniqueQueries'][i],
                "#differentpayloads": data['#Payloads'][i],
                "tag": getTagForFolder(df, data['folders'][i], SparkSql)
            }
            if data['Task_id'] != 'None':
                doc['taskid'] = data['Task_id']
            if data['Since'] != 'None' and data['Until'] != 'None':
                doc['from'], doc['to'] = data['Since'], data['Until']
            print('writing data to ES:', doc)
            res = es.index(index=settings.cachingEfficiency_index,
                           doc_type="_doc", body=doc)
    except Exception as error:
        raise error


def getTagForFolder(df, folder, SparkSql):
    folder_componenets = folder.split(' , ')
    db, schema, node = (
        folder_componenets[0], folder_componenets[1], folder_componenets[2])
    df.createOrReplaceTempView("table")
    sparkDF = SparkSql.spark.sql("select tagname from table where db = %s and schema = %s and nodefullpath = %s and tagname IS NOT NULL" % (
        '"' + db + '"', '"' + schema + '"', '"' + node + '"'))
    row = sparkDF.first()
    if len(row) != 0:
        return row['tagname']
    else:
        return None


def convertJsonToDictionary(data):
    """
    :param data: this is a caching efficiency dictionary in a string format
    :return: the python dictionary format of the data string
    """

    # this is the format of the output
    output = {"#Payloads": [], "#queries": [],
              "#uniqueQueries": [], "PayloadSize (MB)": [], "folders": []}
    # extract the string  main components
    data = data.strip('{}')
    componenets = data.split(',"')
    folders_value = ''
    for comp in componenets[4:]:
        if folders_value:
            folders_value += ',"'
        folders_value += comp
    componenets = componenets[:4] + [folders_value]
    # add the right values to the correpondant key
    for comp in componenets:
        elements = comp.split(':')
        key, value = elements[0].strip('"'), elements[1].strip('[]')
        if key == "folders":
            value = value.split('","')
            for val in value:
                val = val.strip('"')
                output["folders"].append(val)
        else:
            value = value.split(',')
            if key == "PayloadSize (MB)":
                output[key] = [float(val) for val in value]
            else:
                output[key] = [int(val) for val in value]
    return output
