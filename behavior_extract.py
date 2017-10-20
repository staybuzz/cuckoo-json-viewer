# coding: utf-8

from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
import bson
import json
import hashlib

class BehaviorExtract(object):
    def __init__(self, dbaddr='localhost', dbport=27017, dbname='mws'):
        # MongoDB接続
        self.connect = MongoClient(dbaddr, dbport)
        # mws DBの取得
        self.db = self.connect.mws
        self.apirefs = list(self.db.apiref.find())[0] # MongoDBに合わせたjsonに変更する？


    def get_jsonlist(self):
        col = self.db['filelist']
        jsonlist = col.find({})
        return jsonlist


    def get_jsonname(self, jsonid):
        col = self.db['filelist']
        jsonlist = list(col.find({'id': jsonid}))
        if jsonlist:
            return jsonlist[0]['filename']
        else:
            return "Sample"


    def get_processinfo(self, jsonid):
        col = self.db[jsonid]
        res = col.find({}, {"behavior.processes.pid":1, "behavior.processes.process_name":1}) # pidはunicode型
        res = list(res)[0]['behavior']['processes']
        return res


    def import_json(self, req_json, jsonname):
        try:
            jdata = json.load(req_json)
            jsonid = hashlib.md5(json.dumps(jdata, sort_keys=True)).hexdigest()[0:16]
            if not list(self.db['filelist'].find({'id': jsonid})): # 同じjsonファイル既にが読み込まれているか確認
                self.db[jsonid].insert_one(jdata)

            samplehash = jdata['target']['file']['sha256']
            date = datetime.now().isoformat()
            self.db['filelist'].insert_one({'id': jsonid,
                                            'filename': jsonname,
                                            'samplehash': samplehash,
                                            'time': date})

            return (jsonid, True)

        except: # if error
            import traceback
            traceback.print_exc()
            return (None, False)

    def get_behavior(self, jsonid, pid=0):
        """
        辞書型のAPI Call情報を格納した配列を値とする辞書を返す。
        [ {'time': 1475696859.157233, 'apiname': 'NtClose', 'arguments': {'arg1': 'value1', ...}, 'status': 1, 'return_value': 0},
          {'time': 1475696859.251233, 'apiname': 'LdrGetDllHandle', 'arguments': {'arg1': 'value1', ...}, 'status': 1, 'return_value': 0}, ...]
        """

        # TODO エラー処理
        col = self.db[jsonid]

        # api callsの取得
        calls_all = []

        if pid:
            # 第一引数でpid検索し、第二引数ではprocessesリストから該当の要素のみを取り出す
            data = col.find({"behavior.processes.pid": int(pid)}, {"behavior.processes.$":1})
            data = list(data)[0]
        else:
            data =  col.find()
            data = list(data)[0]

        # for debug
        #pprint(i)
        #print data['behavior']['processes'][1]['calls'][0].keys()

        for process in data['behavior']['processes']:
            if not process['calls']: # callsになにも格納されていないとき
                continue
            calls = process['calls']
            pid = process['pid']
            pname = process['process_name']
            for call in calls:
                calls_all.append({'time': datetime.fromtimestamp(call['time']),
                                  'category': call['category'],
                                  'apiname': call['api'],
                                  'apiurl': self.get_api_refurl(call['api']),
                                  'arguments': call['arguments'],
                                  'status': call['status'],
                                  'return_value': call['return_value'],
                                  'pid': pid,
                                  'process_name': pname}
                                )

        return calls_all

    def get_api_refurl(self, apiname):
        """
        与えられたAPI名のMSDNリファレンスへのURLを返す。
        手元の辞書になければgoogle検索URLを返す。
        """
        if (apiname in self.apirefs) and (self.apirefs[apiname]):
            return self.apirefs[apiname]
        else:
            return "https://www.google.com/search?q=%s" % apiname


    def search_api(self, jsonid, query='', categoryname='', pid=0):
        """
        与えられたAPI名と引数を検索する。
        """
        # TODO: ちゃんとMongoDBのクエリから取得できるようにしたい

        calls = self.get_behavior(jsonid, pid)

        results = []
        append = results.append # あらかじめappend()を呼び出してオーバーヘッドを抑える
        if query:
            # API名と引数を対象に検索
            for call in calls:
                res = []

                # API名
                if query.lower() in call['apiname'].lower():
                    append(call)

                # 引数
                num_types = [int, float, bson.int64.Int64]
                for k,v in call['arguments'].items():
                    if type(v) is dict: # 引数の中にさらにdictがある場合
                        vl = list(v.values())
                        vl = list(map(lambda x: str(x) if type(x) in num_types else x, vl))
                        v = '|'.join(vl)
                    elif type(v) in num_types:
                        v = str(v)

                    if query.lower() in v.lower():
                        append(call)
                        break

        if categoryname:
            if results:
                results = [call for call in results if categoryname.lower() == call['category'].lower()]
            else:
                results = [call for call in calls if categoryname.lower() == call['category'].lower()]

        if (not query) and (not categoryname):
            return calls

        return results

    def get_behavior_summary(self, jsonid):
        col = self.db[jsonid]
        b_sum = col.find({}, {"behavior.summary":1, "_id":0})
        b_sum = list(b_sum)[0]['behavior']['summary']
        pprint(b_sum)

        return b_sum
