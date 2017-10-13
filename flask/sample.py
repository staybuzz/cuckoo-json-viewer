from flask import Flask, render_template, request, redirect, url_for
import simplejson as json
import datetime
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

@app.route('/')
def index():
    title = "Sample"
    jdata = be.get_behavior()
    return render_template('index.html',
                           message=jdata, title=title)

@app.route('/search', methods=['GET', 'POST'])
def search():
    title = "Sample"
    jdata = be.search_api(request.args.get('query'), request.args.get('category'))
    return render_template('index.html',
                       message=jdata, title=title)

if __name__ == '__main__':
    app.debug = True 
    app.run(host='0.0.0.0')
