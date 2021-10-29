import os
import dateutil.parser


def extract_query_fields(row, settings):
    """
        This function is used for completing COOL parameters.
        Input: the es row source
        Output: the COOL parameters (db,schema,node_id,nodefullpath,nodetime,tag_id,tagname,globaltagname,since,until)
    """
    # define the output
    rowdic = {
        'sqldb': None, 'sqltagid': 0, 'sqltagname': None, 'sqlnodefullpath': None,
        'sqlowner': None, 'sqlnodeid': -1, 'nodetime': None, 'sqlsin': -1, 'sqlunt': -1
    }
    # extract row values
    for key in row:
        if key != 'sqldb' and row[key]:
            rowdic[key] = row[key]

    for db in settings.db_list:
        if row['sqldb'] and db in row['sqldb']:
            rowdic['sqldb'] = row['sqldb'].split('_')[0]

    if not rowdic['sqldb'] or rowdic['sqldb'] == 'None':
        return None

    if rowdic['sqlnodeid'] == -1 or not rowdic['sqlnodefullpath']:
        rowdic['sqlnodeid'], rowdic['sqlnodefullpath'], rowdic['nodetime'] = getNodes(
            db=rowdic['sqldb'],
            schema=rowdic['sqlowner'],
            id=rowdic['sqlnodeid'],
            node=rowdic['sqlnodefullpath'],
            settings=settings)

    if rowdic['sqltagid'] == 0 or not rowdic['sqltagname']:
        rowdic['sqltagid'], rowdic['sqltagname'] = getTag(
            db=rowdic['sqldb'],
            schema=rowdic['sqlowner'],
            node=rowdic['sqlnodefullpath'],
            tagname=rowdic['sqltagname'],
            tag_id=rowdic['sqltagid'],
            settings=settings)
    return rowdic


def getTag(db, schema, tag_id, node, tagname, settings):
    """
    This function returns COOL Tags information
    :return: tag_id, tag_name
    """
    # skip not cool queries
    if db == None or schema == None or node == None:
        return tag_id, tagname
    # parse only queries with db exists in COOLR file
    if db not in settings.db_list:
        return tag_id, tagname
    # check if coolr file exists
    while not os.path.exists(settings.coolr_file):
        continue
    try:
        if tag_id != 0:
            tagname = settings.hashmapTagsID[(db, schema, node, tag_id)]
        else:
            # if we have the tagname value, we retrieve the tag_id value
            if tagname:
                tag_id = settings.hashmapTags[(db, schema, node, tagname)]
    except Exception as error:
        pass
    return tag_id, tagname


def getNodes(db, schema, node, id, settings):
    """
    This function returns COOL nodes information
    :return:
    """
    node_id = id
    nodefullpath = node
    nodetime = None
    # skip not cool queries
    if db == None or schema == None:
        return node_id, nodefullpath, nodetime
    # parse only queries with db exists in COOLR file
    if db not in settings.db_list:
        return node_id, nodefullpath, nodetime
    # check if the static file exists
    while not os.path.exists(settings.coolr_file):
        continue
    try:
        if id != -1:  # if we have the node_id and we want to get the corresponding nodefullpath and nodetime
            nodefullpath, nodetime = settings.hashmapNodesID[(db, schema, id)]
        else:
            # if we have the nodefullpath and we want to get the corresponding node_id and nodetime
            if node:
                node_id, nodetime = settings.hashmapNodes[(db, schema, node)]
    except Exception:
        pass
    return (node_id, nodefullpath, nodetime)


# convert ISO8601String to date
def getDateTimeFromISO8601String(IOSstring):
    date = dateutil.parser.parse(IOSstring)
    return date

# convert a date to unix time (like timestamp format)


def toUnixTime(adate):
    return adate.timestamp()
