# coding: utf-8

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug import secure_filename
from behavior_extract import BehaviorExtract


app = Flask(__name__)
be = BehaviorExtract()

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
