from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import simplejson as json
import datetime

app = Flask(__name__)

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
    jdata = read_json("testjson.json")
    return render_template('index.html',
                           message=jdata, title=title)

@app.route('/post', methods=['GET', 'POST'])
def post():
    title = "Sample"
    if request.method == 'POST':
    	jdata = read_json("testjson.json")
    	return render_template('index.html',
                           message=jdata, title=title)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True 
    app.run(host='0.0.0.0')