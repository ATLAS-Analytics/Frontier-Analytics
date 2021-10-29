from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify, make_response
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from Analytics.Plots import SparkSqlEngine as plot
from Analytics.FrontierData.Config import settings as set
from Analytics.FrontierData.CachingEfficiency import *
from Analytics.FrontierData.DataExtraction.parseQueries import *
from worker import celery
import os
import time
import random
import atexit
import json
from stat import S_ISREG, ST_CTIME, ST_MODE
from apscheduler.schedulers.background import BackgroundScheduler
import logging

'''
    Create and Configure the Flask app
    Declare the path to this file before running Flask by Initializing an ENV variable
         Linux : export FrontierAnalyticsApp_SETTINGS=/path/to/settings.cfg
         Windows : set FrontierAnalyticsApp_SETTINGS=/path/to/settings.cfg
'''

app = Flask(__name__)
app.config.from_envvar('FrontierAnalyticsApp_SETTINGS')
# Configure socket.io for clients notification
socketio = SocketIO(app)

app.logger.setLevel(logging.INFO)
app.logger.info("Starting web server")

'''
    Declare global variables
'''

# The path to parquet Files directory
global dirpath
dirpath = app.config['UPLOAD_FOLDER']

app.logger.info("Frontier analytics settings")
global settings
settings = set.Settings(app.config['ANALYTICS_CONFIG_FILE'])

app.logger.info("loaded settings.")

# Define background tasks status
global status
status = app.config['STATUS']

app.logger.info('creating sparksql engine')
# Create a spark engine for filtering data
global SparkSql
SparkSql = plot.SparkSqlEngine()
app.logger.info("Spark started.")

# the list of folders used to calculate the caching efficiency
global foldersListForCachingEfficiency
foldersListForCachingEfficiency = [
    ('CONDBR2', 'ATLAS_COOLOFL_PIXEL', '/PIXEL/PixCalib'),
    ('CONDBR2', 'ATLAS_COOLONL_SCT', '/SCT/DAQ/Config/Chip'),
    ('CONDBR2', 'ATLAS_COOLOFL_MDT', '/MDT/T0BLOB'),
    ('OFLP200', 'ATLAS_COOLOFL_RPC', '/RPC/TRIGGER/CM_THR_ETA')
]


'''
   Create a scheduler for updating COOLR static File 
'''
app.logger.info("scheduler for coolr")
scheduler = BackgroundScheduler()
coolr = CoolrClient(settings)

# hours = 168
scheduler.add_job(func=coolr.updateCoolrParquetFile,
                  trigger="interval", hours=168, args=[settings])
scheduler.start()
app.logger.info("scheduler started")

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

app.logger.info('actually starting')
"""
   ******************************  Routes to pages ****************************
"""

# Access the main page


@app.route('/index.html')
@app.route('/')
def main_page():
    # prepare the list of existing parquet Files
    parquetFiles = ParquetFilesList()
    return render_template('index.html', parquetFilesList=parquetFiles)


# Access the visualize page
@app.route('/Visualize')
def visualize_page():
    # prepare the list of existing parquet Files
    parquetFiles = ParquetFilesList()
    return render_template('visualize.html', parquetFilesList=parquetFiles)

# Access the plots page


@app.route('/Plots/<filename>')
def plots_page(filename):
    try:
        # find the parquet file path
        parquetFileName = filename + '.parquet'
        path = os.path.join(dirpath, parquetFileName)
        # read the parquet File in a SQL dataframe
        sprkDF = SparkSql.readParquetFileInSparkDataFrame(path)
        # generate a user ID
        user_id = random.randint(1, 100)
        # save the current spark dataframe for this user_id
        SparkSql.CurrentSparkDataFrames[user_id] = sprkDF
        # Convert coolr hashmap structure to JSON object
        CoolrData = ConvertCoolrHashMapToJson(settings.CoolrDataHashmap)
        return render_template('plots.html', SessionID=user_id, CoolrData=CoolrData)
    except Exception as error:
        httpcode, errortype = ('500', 'Internal Server Error')
        error = str(error)
        return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


# Access the caching efficiency
@app.route('/CachingEfficiency')
def caching_page():
    # read from ElasticSearch
    data = caching_efficiency_data(settings)
    return render_template('cachingEfficiency.html', caching_data=data)

# Access the calculator page for caching efficiency


@app.route('/calculateCachingEfficiency')
def calculate_Caching_page():
    # prepare the list of existing parquet Files
    parquetFiles = ParquetFilesList()
    # Convert coolr hashmap structure to JSON object
    CoolrData = ConvertCoolrHashMapToJson(settings.CoolrDataHashmap)
    return render_template('calculate_caching_Efficiency.html', CoolrData=CoolrData, parquetFilesList=parquetFiles, foldersList=foldersListForCachingEfficiency)


# no route
@app.errorhandler(404)
def page_not_found(e):
    httpcode, errortype = ('404', 'PAGE NOT FOUND')
    return render_template('Errors.html', Httperror=httpcode, errorType=errortype)


"""
 *************************************
  section1:   Discover page methods 
 *************************************
"""


"""
  1- Extract ElasticSearch data. This task may take several minutes, that's why we use Celery to ensure an asynchro execution fot this task
"""

# load Frontier data


@app.route('/loadData', methods=['POST', 'GET'])
def load_data():
    if request.method == 'POST':
        try:
            param = request.form
            validatedparam = validateInput(param)
            # run and report the progress
            task = celery.send_task('tasks.extract', args=[
                                    validatedparam, app.config['UPLOAD_FOLDER']])
            resp = make_response(
                redirect(url_for('main_page', _external=True, _scheme='https')))
            app.logger.info('loadData task id: ' + task.id)
            resp.set_cookie('task_id', task.id)
            # get the extraction status
            return resp, 202, {'Location': url_for('taskstatus', task_id=task.id, _external=True, _scheme='https')}
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error) + \
                ". Check input parameters or ElasticSearch connection"
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/stopLoadData', methods=['POST', 'GET'])
def stop_load_data():
    if request.method == 'POST':
        try:
            task = request.form['task_id']
            celery.send_task('tasks.stop', args=[task])
            resp = make_response(
                redirect(url_for('main_page', _external=True, _scheme='https')))
            resp.set_cookie('task_id', '')
            return redirect(url_for('main_page', _external=True, _scheme='https'))
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error) + \
                ". Check input parameters or ElasticSearch connection"
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/status/<task_id>')
def taskstatus(task_id):
    #task = extractESdata.AsyncResult(task_id)
    task = celery.AsyncResult(task_id)
    app.logger.info("task status: " + task.state)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            '#Queries': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state == 'PROGRESS' or task.state == 'Task completed!':
        response = {
            'state': task.state,
            '#Queries': task.info.get('#Queries', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
    elif task.state == 'FAILURE':
        # something went wrong in the background job
        response = {
            'state': task.state,
            '#Queries': 0,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    else:
        response = {
            'state': task.state,
            'status': "task succeeded"}
    return jsonify(response)


@app.route('/ExtractingProgress', methods=['GET', 'POST'])
def extractionStillRunning():
    if request.method == 'POST':
        try:
            task = request.form['task_id']
            if task:
                #result = extractESdata.AsyncResult(task)
                result = celery.AsyncResult(task)
                app.logger.info("extracting progress: " + result.state)
                if result.state in status:
                    app.logger.info('task: ' + str(task))
                    app.logger.warn(
                        url_for('taskstatus', task_id=task, _external=True, _scheme='https'))
                    return redirect(url_for('main_page', _external=True, _scheme='https')), 202, {'Location': url_for('taskstatus', task_id=task, _external=True, _scheme='https')}
                else:
                    app.logger.info('task: ' + str(task) + ' ' + result.state)
                    resp = make_response(
                        redirect(url_for('main_page', _external=True, _scheme='https')))
                    resp.set_cookie('task_id', '')
                    return resp
            return redirect(url_for('main_page', _external=True, _scheme='https'))
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


"""
 2- Manage the parquet Files Directory 
"""


@app.route('/deleteParquet')
def deleteParquetFile():
    try:
        parquetFileName = request.args.get('parquetFileName') + '.parquet'
        path = os.path.join(dirpath, parquetFileName)
        os.remove(path)
        app.logger.info('I deleted the file: ' + path)
        # run celery task to notify all users that a file is deleted
        return redirect(url_for('main_page', _external=True, _scheme='https'))
    except Exception as error:
        httpcode, errortype = ('500', 'Internal Server Error')
        error = str(error)
        return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/downloadParquet')
def downloadParquetFile():
    app.logger.info('downloading file.')
    try:
        parquetFileName = request.args.get('parquetFileName') + '.parquet'
        path = os.path.join(dirpath, parquetFileName)
        return send_file(path, as_attachment=True)
    except Exception as error:
        httpcode, errortype = ('500', 'Internal Server Error')
        error = str(error)
        return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


"""
 3- Upload a parquet File 
"""


@app.route('/uploadParquet', methods=['POST', 'GET'])
def uploadParquetFile():
    app.logger.info('uploading file.')
    try:
        if request.method == 'POST':
            parquetFile = request.files['parquetFileName']
            filename = secure_filename(parquetFile.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            parquetFile.save(path)
            return redirect(url_for('main_page', _external=True, _scheme='https'))
    except Exception as error:
        httpcode, errortype = ('500', 'Internal Server Error')
        error = str(error)
        return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


"""
 4- app Configuration 
"""


@app.route('/config', methods=['POST', 'GET'])
def configApp():
    if request.method == 'POST':
        try:
            param = request.form
            # change the setting parameters
            if param['ES_host']:
                settings.es_server = param['ES_host']
            if param['ES_port']:
                settings.es_port = param['ES_port']
            if param['COOLR_server']:
                settings.coolr_server = param['COOLR_server']
            if param['limit']:
                settings.limit = param['limit']
            if param['ES_frontier_index']:
                settings.frontier_index = param['ES_frontier_index']
            if param['ES_caching_index']:
                settings.cachingEfficiency_index = param['ES_caching_index']
            set.createConfigFile(settings.coolr_file, settings.es_server, settings.es_port, settings.es_user, settings.es_pswd, settings.frontier_index,
                                 settings.cachingEfficiency_index, settings.coolr_server, settings.limit, settings.db_list, app.config['ANALYTICS_CONFIG_FILE'])
            # get the extraction status
            return redirect(url_for('main_page', _external=True, _scheme='https'))
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error) + \
                ". Check input parameters or ElasticSearch connection"
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


"""
  5- Sockets 
"""


@socketio.on('connect')
def test_connect():
    app.logger.info('Client Connected')


@socketio.on('disconnect')
def test_disconnect():
    app.logger.info('Client disconnected')


@socketio.on('updateParquetDirectoryEvent')
def handle_updateParquetDirectory_event():
    app.logger.info('updateParquetDirectoryEvent')
    emit('refreshPage', broadcast=True)


@socketio.on_error()
def error_handler(e):
    pass


"""
 *************************************  section2:   Plots page methods 
 *************************************
"""


def loadPlotsData(path):
    df = plot.readParquetFileInSparkDataFrame(path)
    plots_data = {}
    db = 'CONDBR2'
    task_id = None
    plots_data['size%Schema'] = plot.sizePercontagePerSchema(df, db, task_id)
    return plots_data


@app.route('/Plots/countPerDb', methods=['POST', 'GET'])
def countPerDbs():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            # get the corresponding spark dataframe
            app.logger.info('user:')
            app.logger.info(user)
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.countQueriesPerCoolInstance(sprkDF, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/countNotCachedForDb', methods=['POST', 'GET'])
def countNotCachedForDb():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            app.logger.info('task:')
            app.logger.info(task_id)
            data = SparkSql.countNotCachedQueriesPerTypeForDB(
                sprkDF, task_id, DB)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/countQueriesPerSchema', methods=['POST', 'GET'])
def countQueriesPerSchema():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.countQueriesPerSchema(sprkDF, task_id, DB)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/countNonPayloadPerSchema', methods=['POST', 'GET'])
def NonPayloadQueriesPerSchema():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.countNonPayloadQueriesPerSchema(
                sprkDF, task_id, DB)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/countNonPayloadPerNode', methods=['POST', 'GET'])
def NonPayloadQueriesPerNode():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            schema = param['schema']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.countNonPayloadQueriesPerNode(
                sprkDF, task_id, DB, schema)
            app.logger.info('lol')
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/queryPercentagePerSchema', methods=['POST', 'GET'])
def queryPercentagePerSchema():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.queryPercentagePerSchema(sprkDF, DB, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/queryPercentagePerNode', methods=['POST', 'GET'])
def queryPercentagePerNode():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            schema = param['schema']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.queryPercentagePerNode(sprkDF, DB, schema, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/countQueriesPerQueryTime', methods=['POST', 'GET'])
def countQueriesPerQueryTime():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.countQueriesPerQueryTime(sprkDF, DB, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/countQueriesPerDbTime', methods=['POST', 'GET'])
def countQueriesPerDbTime():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.countQueriesPerDbTime(sprkDF, DB, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/TimeDistribution', methods=['POST', 'GET'])
def TimeDistribution():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.TimeDistribution(sprkDF, DB, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/responseSizeDistribution', methods=['POST', 'GET'])
def responseSizeDistribution():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.responseSizeDistribution(sprkDF, DB, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/sizePercentagePerSchema', methods=['POST', 'GET'])
def sizePercentagePerSchema():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.sizePercentagePerSchema(sprkDF, DB, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/sizePercentagePerNode', methods=['POST', 'GET'])
def sizePercentagePerNode():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            schema = param['schema']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.sizePercentagePerNode(sprkDF, DB, schema, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/HighQueryDistPerSchema', methods=['POST', 'GET'])
def HighQueryDistPerSchema():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.HighQueryDistributionPerSchema(sprkDF, DB, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/HighQueryDistPerNode', methods=['POST', 'GET'])
def HighQueryDistPerNode():
    if request.method == 'POST':
        try:
            param = request.form
            # get the request parameters
            user = param['userID']
            task_id = param['task']
            DB = param['db']
            schema = param['schema']
            # get the corresponding spark dataframe
            sprkDF = SparkSql.CurrentSparkDataFrames[int(user)]
            # filter data for the plot
            data = SparkSql.HighQueryDistributionPerNode(
                sprkDF, DB, schema, task_id)
            return jsonify(data)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/Plots/deleteSession', methods=['POST', 'GET'])
def deleteSession():
    if request.method == 'POST':
        try:
            param = request.form
            SparkSql.CurrentSparkDataFrames.pop(param['userID'])
            return jsonify({})
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


"""
 *************************************  section 3:   Caching Efficiency page methods 
 *************************************
"""


@app.route('/calculateCachingEfficiency/addCachingEfficiencyFolder', methods=['POST', 'GET'])
def addCachingEfficiencyFolder():
    if request.method == 'POST':
        try:
            param = request.form
            folder = (param['db'], param['schema'], param['node'])
            foldersListForCachingEfficiency.append(folder)
            app.logger.info(foldersListForCachingEfficiency)
            return jsonify(foldersListForCachingEfficiency)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/calculateCachingEfficiency/removeCachingEfficiencyFolder', methods=['POST', 'GET'])
def deleteCachingEfficiencyFolder():
    if request.method == 'POST':
        try:
            param = request.form
            folder = (param['db'], param['schema'], param['node'])
            if folder in foldersListForCachingEfficiency:
                foldersListForCachingEfficiency.remove(folder)
            return jsonify(foldersListForCachingEfficiency)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/calculateCachingEfficiency/calculate')
def calculate_caching_efficiency():
    try:
        folders = request.args.get('folders')
        parquetFile = request.args.get('parquet_file') + '.parquet'
        path = os.path.join(dirpath, parquetFile)
        foldersList = extractFolders(folders)
        #results = calculateCachingEfficiency(path,foldersList,settings)
        task = celery.send_task(
            'tasks.caching_efficiency', args=[path, foldersList])
        task_id = task.id
        data = {'task_id': task_id}
        return jsonify(data)
    except Exception as error:
        httpcode, errortype = ('500', 'Internal Server Error')
        error = str(error)
        return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/calculateCachingEfficiency/calculate_status', methods=['POST', 'GET'])
def calculate_caching_efficiency_status():
    if request.method == 'POST':
        try:
            param = request.form
            task = celery.AsyncResult(param['task_id'])
            results = {}
            if task.state == "SUCCESS":
                results = task.get()
            response = {
                'state': task.state,
                'results': results,
            }
            return jsonify(response)
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/stopCalculating', methods=['POST', 'GET'])
def stop_calculating_caching_efficiency():
    if request.method == 'POST':
        try:
            task = request.form['task_id']
            celery.send_task('tasks.stop', args=[task])
            return jsonify('success')
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error) + \
                ". Check input parameters or ElasticSearch connection"
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


@app.route('/CachingEfficiency/storeCachingEfficiency', methods=['POST', 'GET'])
def writeElasticSearch():
    if request.method == 'POST':
        try:
            # get file and data
            param = request.form
            file, data = (param['file_name'],
                          convertJsonToDictionary(param['data']))
            # find the parquet file path
            file_path = os.path.join(dirpath, file + ".parquet")
            # read the parquet file in a spark dataframe
            sparkDF = SparkSql.readParquetFileInSparkDataFrame(file_path)
            df = sparkDF.first()
            # get info about the file creation : task_id or time_range
            if df['data_taskid'] != 'None':
                task_id = int(df['data_taskid'])
            else:
                task_id = df['data_taskid']
            data['Task_id'], data['Since'], data['Until'] = task_id, df['data_since'], df['data_to']
            # save data into Elasticsearch
            write_caching_efficiency_data(sparkDF, data, settings, SparkSql)
            return jsonify("success")
        except Exception as error:
            httpcode, errortype = ('500', 'Internal Server Error')
            error = str(error)
            return render_template('Errors.html', Httperror=httpcode, error=error, errorType=errortype)


"""
  General Functions used for validate and check the input/output 
"""


def getTagForFolder(df, folder):
    folder_componenets = folder.split(' , ')
    db, schema, node = (
        folder_componenets[0], folder_componenets[1], folder_componenets[2])
    tag = df['tagname'].where(df['nodefullpath'] == node)
    return tag[0]


def extractFolders(folders):
    """
     convert a string of folders to a list of tuples (db , schema, node)
    :param folders: a string containing folders db-schema-node seperated by ,
    :return:  a list of tuples (db , schema, node)
    """
    output = []
    folderList = folders.split('-')
    for folder in folderList:
        folderComponents = folder.split(',')
        output.append(
            (folderComponents[0], folderComponents[1], folderComponents[2]))
    return output


def validateInput(input):
    '''
       check and validate data recieved from a form
    :param input: form parameters for extracting ES data
    :return: validated data parameters
    '''
    output = {}
    if not input['Task_id']:
        output['Task_id'] = None
    else:
        output['Task_id'] = input['Task_id']
    if input['Cached'] == "Cached Queries":
        output['Cached'] = True
    elif input['Cached'] == "Not Cached Queries":
        output['Cached'] = False
    else:
        output['Cached'] = None
    if not input['Since']:
        output['Since'] = None
    else:
        output['Since'] = input['Since']
    if not input['Until']:
        output['Until'] = None
    else:
        output['Until'] = input['Until']
    output['parquetname'] = input['parquetName']
    return output


def ParquetFilesList():
    '''

    :return: read the list of parquet files in a listdire shared storage
    '''
    # get all entries in the directory w/ stats/ size
    entries = (fn for fn in os.listdir(dirpath))
    entries = ((fn, os.stat(os.path.join(dirpath, fn)), os.path.getsize(os.path.join(dirpath, fn)) / 1024 ** 2) for fn
               in entries)
    # leave only regular files, insert creation date
    parquetFiles = [(fn.replace('.parquet', ''), (time.ctime(stat[ST_CTIME])), size) for fn, stat, size in entries if
                    (S_ISREG(stat[ST_MODE]) and ".parquet" in fn)]
    return parquetFiles


def ConvertCoolrHashMapToJson(hashmap):
    '''
      convert a hashmap to Json object
    :param hashmap:  { 'db" : { 'schema' : set(nodes) ,....}
    :return: json object
    '''
    if not hashmap:
        raise TypeError
    output = {}
    for db, item in hashmap.items():
        elem = {}
        for schema, nodes in item.items():
            elem[schema] = list(nodes)
        output[db] = elem
    return json.dumps(output)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
