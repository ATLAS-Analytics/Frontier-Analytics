from pyspark.sql import SparkSession
import re



class SparkSqlEngine:
        """
        This class filter Frontier data using SparkSQL
        """

        def __init__(self):
            self.spark = SparkSession \
                        .builder \
                        .appName("Plots Functions") \
                        .config("spark.some.config.option", "some-value") \
                        .getOrCreate()
            self.sc = self.spark.sparkContext
            self.CurrentSparkDataFrames = {} # this is a hashmap for keeping trace of the current used sparkDataframe per user





        """
        ********************************  Functions for filtering data using SPARK SQL *********************************
        
        """

        def readParquetFileInSparkDataFrame(self,file_path):
            parquetDF = self.spark.read.parquet(file_path)
            return parquetDF

        def convertJsontoSpark(self,jsonObject):
            sprkRDD = self.sc.parallelize(jsonObject)
            sprkDF = self.spark.read.json(sprkRDD)
            return sprkDF

        def splitlistkeyscolumns(self, ll):
            """

            :param ll: a sql string containing columns
            :return: a list of the parameters
            """
            org = ll.split(',')
            col = []
            for item in org:
                if re.search(' as ',str(item)) :
                        l =str(item).split(' ')
                        sitem = (l)[2]
                        kitem = (l)[0]
                else :
                        sitem =str(item)
                        kitem = str(item)
                col.append([kitem.replace(' ',''),sitem.replace(' ','')])
            return col


        """
            sprk : spark dataframe containing data, it will be used as a SQL table
            xatt : x attributes(columns selected from sprk table) that will appear on the abscissa axis. In case xatt contains aggregation functions, these columns should be renamed ex : avg(querytime) as qtime 
            yatt : y attributes. If functions are used, the column must be renamed. ex: 
               yatt = node_id , schema , querytime/100 as qtime 
            each y attribute will be presented as trace 
            cond : a condition on x and y attributes 
        """

        def createSimplePlotData(self, sprk, xatt, yatt, cond):
            # find the name of x_axis
            x_columns = self.splitlistkeyscolumns(xatt)
            value = []
            for col in x_columns:
                value.append(str(col[1]))
            x_axis_name = '/'.join(value)

            # find the name of y_axis column
            y_column = self.splitlistkeyscolumns(yatt)
            y_axis_name = y_column[0][1]

            # define outputs
            x_axis = []
            y_axis = []
            output = {}

            # variables
            x_string, x_value = [], []

            # group by statement
            groupby = ','.join(value)

            # create a spark table
            sprk.createOrReplaceTempView("table")
            # Keep only xatt and yatt attributes based or not on conditions
            if cond:
                sprk_x = self.spark.sql("select  %s , %s from table where %s  group by %s" % (xatt, yatt, cond, groupby))
            else:
                sprk_x = self.spark.sql("select  %s , %s from table group by %s" % (xatt, yatt, groupby))

            # Find y and x values
            for row in sprk_x.rdd.collect():
                # extract x values
                for x_col in x_columns:
                    if type(row[x_col[1]]) == str:
                        x_string.append(row[x_col[1]])
                    else:
                        x_value = row[x_col[1]]  # in this case it should be one x column
                if x_string:
                    strr = '/'.join(x_string)
                    if "ATLAS_COOL" in strr:
                        strr = strr.replace('ATLAS_COOL', '')
                    if "CONDBR2/" in strr:
                        strr = strr.replace('CONDBR2/', '')
                    if "OFLP200/" in strr:
                        strr = strr.replace('OFLP200/', '')
                    if "COMP200/" in strr:
                        strr = strr.replace('COMP200/', '')
                    if "MONP200/" in strr:
                        strr = strr.replace('MONP200/', '')
                    x_axis.append(strr)
                else:
                    x_axis.append(x_value)
                x_string, x_value = [], []

                # extract y values (one column)
                y_axis.append(row[y_column[0][1]])

            output[x_axis_name] = x_axis
            output[y_axis_name] = y_axis
            return output


        """
        *****************************************  functions for filtering data for specific plots ****************************
        """


        def countQueriesPerCoolInstance(self, sprkDF, Task_id):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            data_cached = self.createSimplePlotData(sprkDF, 'db', 'count(*) as _count', cond + '  cached = true')
            data_notcached = self.createSimplePlotData(sprkDF, 'db', 'count(*) as _count', cond + '  cached = false')
            data_list = {'cached': data_cached, 'not_cached': data_notcached}
            return data_list


        def countNotCachedQueriesPerTypeForDB(self, sprkDF, Task_id, DB):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '

            data_disconn = self.createSimplePlotData(sprkDF, 'db', 'count(*) as _count', cond + ' disconn=true')
            data_not_cached_first_queries = self.createSimplePlotData(sprkDF, 'db', 'count(*) as _count', cond + ' cached=false and disconn=false and rejected=false and procerror=false')
            data_rejected = self.createSimplePlotData(sprkDF, 'db', 'count(*) as _count', cond + ' rejected=true')
            data_procerror = self.createSimplePlotData(sprkDF, 'db', 'count(*) as _count', cond + ' procerror=true')
            data_list = { 'disconn': data_disconn, ' first queries': data_not_cached_first_queries,  'rejected': data_rejected, 'procerror': data_procerror}
            return data_list


        def countQueriesPerSchema(self, sprkDF, Task_id, DB):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            data = self.createSimplePlotData(sprkDF, 'schema', 'count(*) as _count', cond + ' db = "' + DB + '"')
            return data


        def countCached_NotCachedQueriesPerSchemas(self, sprkDF, Task_id, DB):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            data_cached = self.createSimplePlotData(sprkDF, 'schema', 'count(*) as _count',
                                               cond + ' db = "' + DB + '" and cached = true')
            data_notcached = self.createSimplePlotData(sprkDF, 'schema', 'count(*) as _count',
                                                  cond + ' db = "' + DB + '" and cached = false')
            data_list = {'cached': data_cached, 'not_cached': data_notcached}
            return data_list

        def countNonPayloadQueriesPerSchema(self,sprkDF, Task_id, DB ):
            cond = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            data_payloads = self.createSimplePlotData(sprkDF, 'schema', 'count(*) as _count',
                                               cond + ' db = "' + DB + '" and since <> -1')
            data_nonpayloads = self.createSimplePlotData(sprkDF, 'schema', 'count(*) as _count',
                                                  cond + ' db = "' + DB + '" and since = -1')
            data_list = { 'non_payload': data_nonpayloads, ' payload': data_payloads}
            return data_list


        def countNonPayloadQueriesPerNode(self,sprkDF, Task_id, DB, schema ):
            cond = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            data_payloads = self.createSimplePlotData(sprkDF, 'nodefullpath', 'count(*) as _count',
                                               cond + ' db = "' + DB + '" and schema = "' + schema + '" and since <> -1')
            print('data_payloads:', data_payloads)
            data_nonpayloads = self.createSimplePlotData(sprkDF, 'nodefullpath', 'count(*) as _count',
                                                  cond + ' db = "' + DB + '" and schema = "' + schema + '" and since = -1')
            print('data_non_payloads', data_nonpayloads)
            data_list = { 'non_payload': data_nonpayloads, ' payload': data_payloads}
            return data_list


        def TimeDistribution(self, sprkDF, DB, Task_id):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '
            data_cached = self.createSimplePlotData(sprkDF,
                                               'from_unixtime(int(unix_timestamp(to_timestamp(time))/300)*300) as timestmp',
                                               'count(*) as _count', cond + ' cached=true')
            data_notcached = self.createSimplePlotData(sprkDF,
                                                  'from_unixtime(int(unix_timestamp(to_timestamp(time))/300)*300) as timestmp',
                                                  'count(*) as _count', cond + ' cached=false')
            data_list = {'cached': data_cached, 'not_cached': data_notcached}
            return data_list


        def countQueriesPerQueryTime(self, sprkDF, DB, Task_id):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '
            data_cached = self.createSimplePlotData(sprkDF, 'int(querytime/100)*100 as qtime', 'count(*) as _count',
                                               cond + ' cached = true')
            data_notcached = self.createSimplePlotData(sprkDF, 'int(querytime/100)*100 as qtime', 'count(*) as _count',
                                                  cond + '  cached = false')
            data_list = {'cached': data_cached, 'not_cached': data_notcached}
            return data_list


        def countQueriesPerDbTime(self, sprkDF, DB, Task_id):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '
            data_cached = self.createSimplePlotData(sprkDF, 'int(dbtime/100)*100 as _dbtime', 'count(*) as _count',
                                               cond + ' cached = true')
            data_notcached = self.createSimplePlotData(sprkDF, 'int(dbtime/100)*100 as _dbtime', 'count(*) as _count',
                                                  cond + '  cached = false')
            data_list = {'cached': data_cached, 'not_cached': data_notcached}
            return data_list


        def responseSizeDistribution(self, sprkDF, DB, Task_id):
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '

            # add new columns to this datframe
            data = self.createSimplePlotData(sprkDF, 'from_unixtime(int(unix_timestamp(to_timestamp(time))/300)*300) as timestmp',
                                        'sum(fsize/1024) as _sum', cond + ' cached=false')
            return data


        def queryPercentagePerSchema(self, sprkDF, DB, Task_id):
            # create a spark dataframe table
            sprkDF.createOrReplaceTempView("All")

            # create where statement
            where = ''
            statements = []
            if DB:
                statements.append('db ="' + DB + '" ')
            if Task_id:
                statements.append(' taskid =' + str(Task_id))
            if statements:
                where = 'and'.join(statements)
                where = 'where ' + where

            # add new columns
            df = self.spark.sql('select db , schema , count(*) as sc_count from All ' + where + ' group by db , schema')

            # create a table
            df.createOrReplaceTempView("table")

            # merge the new table with All to add the new column (total queries per db/schema) to All dataframe
            dfall = self.spark.sql(
                "select All.db , All.schema, taskid, cached , sc_count from All join table where All.db = table.db and All.schema = table.schema")

            # prepare plot data
            data_cached = self.createSimplePlotData(dfall, 'db, schema, sc_count', '(count(*)/sc_count)*100 as _count',
                                               ' cached = true')
            data_notcached = self.createSimplePlotData(dfall, 'db, schema, sc_count', '(count(*)/sc_count)*100 as _count',
                                                  '  cached = false')

            data_list = {'cached': data_cached, 'not_cached': data_notcached}
            return data_list


        def sizePercentagePerSchema(self, sprkDF, DB, Task_id):

            # create a spark dataframe table
            sprkDF.createOrReplaceTempView("All")
            # create where statement
            where = ''
            statements = []
            if DB:
                statements.append('db ="' + DB + '" ')
            if Task_id:
                statements.append(' taskid =' + str(Task_id))
            if statements:
                where = 'and'.join(statements)
                where = 'where ' + where

            # add new columns
            df = self.spark.sql('select db , sum(fsize)/1024 as total_fsize from All ' + where + ' group by db')

            # create a table
            df.createOrReplaceTempView("table")

            # merge the new table with All to add the new column (total queries per db/schema) to All dataframe
            dfall = self.spark.sql("select All.db , All.schema, taskid, fsize, cached ,total_fsize from All join table where All.db = table.db")

            # prepare condition
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '

            # prepare plot data
            data_notcached = self.createSimplePlotData(dfall, 'db, schema, total_fsize', '(sum(fsize)/(1024*total_fsize))*100 as _count', cond + ' cached = false')
            return data_notcached

        def HighQueryDistributionPerSchema(self,sprkDF, DB, Task_id):
            # create where statement
            where = ''
            statements = []
            if DB:
                statements.append('db ="' + DB + '" ')
            if Task_id:
                statements.append(' taskid =' + str(Task_id))
            if statements:
                where = 'and'.join(statements)
                where = 'where ' + where
            # create a spark dataframe table
            sprkDF.createOrReplaceTempView("All")
            # Get the list of schemas in this spark dataframe
            df_Schemas =  self.spark.sql('SELECT DISTINCT schema from All ' + where)
            # prepare output
            data_list = {}
            # defind high query condition
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '
            # for every schema, find the high query time and count them per time bins
            for schema in df_Schemas.rdd.collect():
                schema_name = schema['schema']
                data_list[schema_name] = self.createSimplePlotData(sprkDF,
                                          'from_unixtime(int(unix_timestamp(to_timestamp(time))/300)*300) as timestmp',
                                          'count(*) as _count', cond + ' querytime>=1000 and schema = "' + schema_name +'"')

            return data_list

        def HighQueryDistributionPerNode(self,sprkDF, DB, schema, Task_id):
            # create where statement
            where = ''
            statements = []
            if DB:
                statements.append('db ="' + DB + '" ')
            if Task_id:
                statements.append(' taskid =' + str(Task_id))
            if schema:
                statements.append(' schema ="' + schema + '" ')
            if statements:
                where = 'and'.join(statements)
                where = 'where ' + where
            # create a spark dataframe table
            sprkDF.createOrReplaceTempView("All")
            # Get the list of nodes in this spark dataframe for a diven db/schema
            df_Nodes =  self.spark.sql('SELECT DISTINCT nodefullpath from All ' + where)
            # prepare output
            data_list = {}
            # defind high query condition
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '
            if schema:
                cond += 'schema = "' + str(schema) + '" and '
            # for every schema, find the high query time and count them per time bins
            for node in df_Nodes.rdd.collect():
                node_name = node['nodefullpath']
                data_list[node_name] = self.createSimplePlotData(sprkDF,
                                          'from_unixtime(int(unix_timestamp(to_timestamp(time))/300)*300) as timestmp',
                                          'count(*) as _count', cond + ' querytime>=1000 and nodefullpath = "' + node_name +'"')

            return data_list

        def sizePercentagePerNode(self, sprkDF, DB, schema, Task_id):

            # create a spark dataframe table
            sprkDF.createOrReplaceTempView("All")
            # create where statement
            where = ''
            statements = [" nodefullpath <> 'None' "]
            if DB:
                statements.append(' db ="' + DB + '" ')
            if Task_id:
                statements.append(' taskid =' + str(Task_id))
            if schema:
                statements.append(' schema ="' + schema + '" ')
            if statements:
                where = 'and'.join(statements)
                where = 'where ' + where

            # add new columns
            df = self.spark.sql('select db ,schema, sum(fsize)/1024 as total_fsize from All ' + where + ' group by db, schema')

            # create a table
            df.createOrReplaceTempView("table")

            # merge the new table with All to add the new column (total queries per db/schema) to All dataframe
            dfall = self.spark.sql(
                "select All.db , All.schema, nodefullpath, taskid, fsize, cached ,total_fsize from All join table where All.db = table.db and All.schema = table.schema and All.nodefullpath <> 'None'")

            # prepare condition
            cond  = ''
            if Task_id:
                cond += 'taskid =' + str(Task_id) + ' and '
            if DB:
                cond += 'db = "' + str(DB) + '" and '
            if schema:
                cond += 'schema = "' + str(schema) + '" and '

            # prepare plot data
            data_notcached = self.createSimplePlotData(dfall, 'nodefullpath, total_fsize',
                                                       '(sum(fsize)/(1024*total_fsize))*100 as _count',
                                                       cond + ' cached = false')
            return data_notcached

        def queryPercentagePerNode(self, sprkDF, DB, schema, Task_id):
            # create a spark dataframe table
            sprkDF.createOrReplaceTempView("All")

            # create where statement
            where = ''
            statements = [" nodefullpath <> 'None' "]
            if DB:
                statements.append(' db ="' + DB + '" ')
            if schema:
                statements.append(' schema ="' + schema + '" ')
            if Task_id:
                statements.append(' taskid =' + str(Task_id))
            if statements:
                where = 'and'.join(statements)
                where = 'where ' + where

            # add new columns
            df = self.spark.sql('select db , schema , count(*) as sc_count from All ' + where + ' group by db , schema')

            # create a table
            df.createOrReplaceTempView("table")

            # merge the new table with All to add the new column (total queries per db/schema) to All dataframe
            dfall = self.spark.sql(
                "select All.db , All.schema, nodefullpath,  taskid, cached , sc_count from All join table where All.db = table.db and All.schema = table.schema and All.nodefullpath <> 'None'")

            # prepare plot data
            data_cached = self.createSimplePlotData(dfall, 'nodefullpath, sc_count', '(count(*)/sc_count)*100 as _count',
                                               ' cached = true')
            data_notcached = self.createSimplePlotData(dfall, 'nodefullpath, sc_count', '(count(*)/sc_count)*100 as _count',
                                                  '  cached = false')

            data_list = {'cached': data_cached, 'not_cached': data_notcached}

            return data_list
