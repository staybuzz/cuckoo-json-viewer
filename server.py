# coding: utf-8

from flask import Flask, render_template, request, redirect, url_for, abort
import simplejson as json
import datetime
from werkzeug import secure_filename
from behavior_extract import BehaviorExtract


app = Flask(__name__)
be = BehaviorExtract()

def read_json(filename):
    f = open(filename, 'r')
    jsonData = json.load(f)

    f.close()

    len_processes = len(jsonData['behavior']['processes'])
    json_dic={}
    for i in range(0,len_processes):
        tmp_ctr = len(jsonData['behavior']['processes'][i]['calls'])
        for j in range(0,tmp_ctr):
            resizedata = [jsonData['behavior']['processes'][i]['calls'][j]['api'],jsonData['behavior']['processes'][i]['calls'][j]['arguments'],jsonData['behavior']['processes'][i]['calls'][j]['status'],jsonData['behavior']['processes'][i]['calls'][j]['return_value']]
            time = converttime(jsonData['behavior']['processes'][i]['calls'][j]['time'])
            json_dic[str(time)]=resizedata

    return json_dic

def converttime(unixtime):
    time = datetime.datetime.fromtimestamp(unixtime)
    return time

@app.route('/favicon.ico')
def favicon():
    abort(404)

@app.route('/')
def upload_json(status=''):
    title = "cuckoo-json-viewer"
    jsonlist = be.get_jsonlist()
    return render_template('import.html',
                           message=jsonlist, title=title, status=status)

@app.route('/<jsonid>')
def index(jsonid):
    jdata = be.get_behavior(jsonid)
    return render_template('index.html',
                           message=jdata, title=be.get_jsonname(jsonid), jsonid=jsonid)

@app.route('/<jsonid>/search', methods=['GET'])
def search(jsonid):
    jdata = be.search_api(jsonid, request.args.get('query'), request.args.get('category'))
    return render_template('index.html',
                       message=jdata, title=be.get_jsonname(jsonid), jsonid=jsonid)

@app.route('/import', methods=['POST'])
def json_import():
    f = request.files['jsonfile']
    fname = secure_filename(f.filename)
    jsonid, ret = be.import_json(f.stream, fname)
    if ret:
        return redirect(url_for('index', jsonid=jsonid))
    else:
        return redirect(url_for('upload_json', status='ng'))


if __name__ == '__main__':
    app.debug = True 
    app.run(host='0.0.0.0')
