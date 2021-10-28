import dateutil
from elasticsearch import Elasticsearch, helpers
from .parseQueries import *
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import time


def extractElasticSearchData(taskid, from_timestamp, to_timestamp, cached, outputfile, settings, *args):
    """

    :param taskid: can be None
    :param from_timestamp: should be in a date format YYYY-MM-DDThh:mm:ss (you can obtain this format using the following function datetime.datetime(2018,6,13,3,18,19))
    :param to_timestamp: same as from_timestamp. these two parameters allows to retrieve queries in a specific period. They can be None
    :param cached: if True, we retrieve only the cached queries. Otherwise, we retrieve all not cached queries (disconn,processing error and rejected). This param can be None
    :param outputFile: if not None, the results will be saved in a parquet file with outputFile name
    :param args:  optional args, used for reporting the extraction status (Celery task object)
    :return:a data list containing all parsed queries
    """

    # connect es
    es = Elasticsearch([{'host': settings.es_server, 'port': settings.es_port}],
                       scheme="https", http_auth=(settings.es_user, settings.es_pswd))

    # prepare a query for searching inside the ES server
    my_query = {
        "query": {
            "bool": {
                "must": [
                ],
            }
        }
    }

    # define some additional parameters for saving the request parameters
    meta_data = {'data_since': None, 'data_to': None, 'data_taskid': None}

    # prepare the status message
    status_message = "Extracting data"

    # add to the query the following parameters if they are not None
    if from_timestamp != None and to_timestamp != None:
        meta_data['data_since'],  meta_data['data_to'] = from_timestamp, to_timestamp
        status_message += " - " + \
            str(from_timestamp) + " - " + str(to_timestamp)
        my_query['query']['bool']['must'].append(
            {'range': {'@timestamp': {"gte": from_timestamp, "lte": to_timestamp}}})
    if cached != None:
        my_query['query']['bool']['must'].append({'term': {'cached': cached}})
    if taskid != None:
        status_message += " - " + str(taskid)
        meta_data['data_taskid'] = taskid
        my_query['query']['bool']['must'].append({'term': {'taskid': taskid}})
    status_message += "... "

    # the extraction status
    state = None
    if args:
        state = args[0]
        resp = es.count(index=settings.frontier_index, body=my_query)
        total = resp['count']
        if total > settings.limit:
            total = settings.limit

    my_query["_source"] = [
        "taskid", "sqldb", "sqlowner", "sqlnodeid", "sqlnodefullpath",
        "sqlsin", "sqlunt", "sqltagid", "sqltagname", "cached", "disconn",
        "procerror", "rejected", "querytime", "dbtime", "queryiov", "@timestamp",
        "fsize", "frontierserver", 'sqlhash'
    ]

    print('final query body:', my_query)

    try:
        # scan from ES
        res = helpers.scan(es, query=my_query, index=settings.frontier_index)
        data = []
        counter = 0
        writer = None
        # scroll the results
        st = time.time()
        for r in res:
            counter += 1
            # stop when we reach the limit
            if counter > settings.limit:
                break
            if counter % 50000 == 0:
                st1 = time.time()
                print('data collection time for 50000 docs:', st1 - st)
                table = pd.DataFrame(data)
                table.rename(columns={'@timestamp': 'time', 'sqldb': 'db', 'sqlsin': 'since', 'sqlowner': 'schema', 'sqlunt': 'until',
                                      'sqlnodefullpath': 'nodefullpath', 'sqlnodeid': 'node_id', 'sqltagid': 'tag_id', 'sqltagname': 'tagname'}, inplace=True)
                convert_columns(table)
                writer = append_to_parquet_table(table, outputfile, writer)
                print('time to create and append to parquet file:',
                      time.time() - st1)
                data = []
                st = time.time()
            # update the extraction status
            if counter % 1000 and state:
                state.update_state(state='PROGRESS', meta={
                    '#Queries': counter, 'total': total, 'status': status_message})
            row = extract_query_fields(r['_source'], settings)
            if row:
                complete_row = {**r['_source'], **row, **meta_data}
                data.append(complete_row)

    except Exception as e:
        print("During scan: ", str(e))

    if data:
        table = pd.DataFrame(data)
        table.rename(
            columns={'@timestamp': 'time', 'sqldb': 'db', 'sqlsin': 'since', 'sqlowner': 'schema', 'sqlunt': 'until',
                     'sqlnodefullpath': 'nodefullpath', 'sqlnodeid': 'node_id', 'sqltagid': 'tag_id',
                     'sqltagname': 'tagname'}, inplace=True)
        convert_columns(table)
        writer = append_to_parquet_table(table, outputfile, writer)
    if writer:
        writer.close()
    if state:
        state.update_state(state='Task completed!', meta={
                           '#Queries': counter, 'total': total, 'status': "Extraction completed "})


def append_to_parquet_table(dataframe, filepath=None, writer=None):
    """Method writes/append dataframes in parquet format.

    This method is used to write pandas DataFrame as pyarrow Table in parquet format. If the methods is invoked
    with writer, it appends dataframe to the already written pyarrow table.

    :param dataframe: pd.DataFrame to be written in parquet format.
    :param filepath: target file location for parquet file.
    :param writer: ParquetWriter object to write pyarrow tables in parquet format.
    :return: ParquetWriter object. This can be passed in the subsequenct method calls to append DataFrame
        in the pyarrow Table
    """
    table = pa.Table.from_pandas(dataframe)
    if not writer:
        writer = pq.ParquetWriter(filepath, table.schema)
    writer.write_table(table=table)
    return writer


def saveInParquetFile(data, outputFile):
    """

    :param data: the elasticsearch data
    :param params: params['Task_id'], params['Since'], params['Until']
    :param outputFile: the file path
    :return:
    """
    df = pd.DataFrame(data)
    df.rename(columns={'@timestamp': 'time'}, inplace=True)
    convert_columns(df).to_parquet(outputFile)


def getDateTimeFromISO8601String(IOSstring):
    date = dateutil.parser.parse(IOSstring)
    return date


def sortEsData(data, key):
    """
    :param data: a list of dictionaries
    :param key: a string parameter
    :return: sort the input list based on the key in asc order

    """
    data.sort(key=lambda tuple: tuple[key])  # sort by key

# convert object columns to string except IOVs


def convert_columns(df):
    dtypes = df.dtypes
    for c in df.columns:
        newtype = dtypes[c]
        if dtypes[c] == 'object' or dtypes[c] == dict:
            newtype = 'str'
            if c == 'since' or c == 'until':
                newtype = 'int64'
            if c == 'tag_id':
                newtype = 'int64'
        df[c] = df[c].astype(newtype)
    return df
