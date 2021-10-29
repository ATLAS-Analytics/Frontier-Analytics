from coolr.configuration import Configuration
import os
from coolr.api import NodesApi, TagsApi, PayloadsApi
from coolr import ApiClient, SchemasApi
import pandas as pd


class CoolrClient:
    """
    This Class is used for connecting with COOLR server and call its services
    """

    def __init__(self, settings):

        self._urlsrv = settings.coolr_server
        self._config = Configuration()
        self._config.host = self._urlsrv
        self._config.verify_ssl = True
        self._api = ApiClient(configuration=self._config)
        self._schemaapi = SchemasApi(self._api)

    def CoolrParameters(self, db, schema):
        """

        :return: COOL parameters (node_id, nodetime, nodefullpath, tag, tag_id, db, schema) for a given db/schema
        """
        argdic = {}
        argdic['schema'] = schema
        argdic['db'] = db
        coolrarr = []
        try:
            # retrieve the Nodes info
            nodes_api = NodesApi(api_client=self._api)
            resp = nodes_api.list_nodes(**argdic)

            if resp is not None:  # resp contains all nodes corresponding to a given db/schema
                for coolnode in resp:
                    nodefullpath = coolnode.node_fullpath
                    nodeiovbase = coolnode.node_iov_base
                    coolrrow = {'db': db, 'tag': 'none', 'node': nodefullpath, 'schema': schema, 'node_id': coolnode.node_id,
                                'tag_id': 0, 'nodetime': nodeiovbase}
                    # retrieve the tags info
                    tags_api = TagsApi(api_client=self._api)
                    argdic['node'] = nodefullpath
                    respt = tags_api.list_tags(**argdic)
                    if respt is not None and len(respt) > 0:  # respt contains all tags corresponding to a given db/schema/node
                        for cooltag in respt:
                            coolrrow = {'db': db, 'tag': 'none', 'node': nodefullpath, 'schema': schema, 'node_id': coolnode.node_id,
                                        'tag_id': 0, 'nodetime': nodeiovbase}
                            tag = cooltag.tag_name
                            tagid = cooltag.tag_id
                            coolrrow['tag'] = tag
                            coolrrow['tag_id'] = tagid
                            coolrarr.append(coolrrow)
                    else:
                        coolrarr.append(coolrrow)

        except Exception as e:
            print('Error in schema=%s,db=%s' % (schema, db))
            print(e)

        #print('Retrieved result:\n %s' % coolrarr)
        return coolrarr

    def get_schemas(self, db):
        """

        :return: a list of schemas for a given db
        """
        argdic = {}
        argdic['db'] = db
        try:
            resp = self._schemaapi.list_schemas(**argdic)
            return resp
        except Exception as e:
            print('Error in db=%s' % (db))
            print(e)

    def updateCoolrParquetFile(self, settings):
        """
            This function update the coolr parquet file periodically
        """
        print("I'm updating coolr parquet files")
        if os.path.exists(settings.coolr_file):
            print('file', settings.coolr_file, 'is there removing it.')
            os.remove(settings.coolr_file)
        # store coolr parameters in a list
        coolr_list = []
        dbs = settings.db_list

        for db in dbs:  # for every db
            schemas = self.get_schemas(db)  # get the list of schemas
            for schema in schemas:  # for every schema
                reslist = self.CoolrParameters(db, schema.schemaname)  # retrieve nodes/tags corresponding to the given db/schema
                coolr_list.extend(reslist)
            if len(coolr_list) > 0:
                # write coolr list in a parquet file
                df = pd.DataFrame(data=coolr_list)
                df.to_parquet(settings.coolr_file)
                settings.CoolrDataHashmap, settings.hashmapNodes, settings.hashmapTags, settings.hashmapNodesID, settings.hashmapTagsID = settings.CreateHashMapForCoolrFile()
            else:
                print('empty static file')
        print("Update done.")

    def getPayloads(self, db, schema, node, tag, nodetime, iov_since, iov_until):
        """
        :param schema:
        :param node:
        :param nodetime:
        :return: every payload has many channels with different iovs (NANO seconds difference). this method return a payload with the max iov_channel and the min max iov channel
        """
        payload_api = PayloadsApi(self._api)
        argdic = {'schema': schema, 'db': db, 'node': node, 'qrytype': nodetime, 'tag': tag, 'since': iov_since, 'until': iov_until}
        payload = payload_api.list_payloads_as_cool_json(**argdic)
        return payload
