# coding: utf-8

from pymongo import MongoClient
from pprint import pprint

class BehaviorExtract(object):
    def __init__(self, dbaddr='localhost', dbport=27017, dbname='mws'):
        # MongoDB接続
        self.connect = MongoClient(dbaddr, dbport)
        # mws DBの取得
        self.db = self.connect.mws
        self.apirefs = list(self.db.apiref.find())[0] # MongoDBに合わせたjsonに変更する？


    def get_behavior(self):
        """
        辞書型のAPI Call情報を格納した配列を値とする辞書を返す。
        [ {'time': 1475696859.157233, 'apiname': 'NtClose', 'arguments': {'arg1': 'value1', ...}, 'status': 1, 'return_value': 0},
          {'time': 1475696859.251233, 'apiname': 'LdrGetDllHandle', 'arguments': {'arg1': 'value1', ...}, 'status': 1, 'return_value': 0}, ...]
        """

        # json1 collectionの取得
        col = self.db.json1 #test json

        # api callsの取得
        calls_path = "behavior.processes.calls"
        calls_all = []

        for i in col.find():
            data = i
        
            # for debug
            #pprint(i)
            #print data['behavior']['processes'][1]['calls'][0].keys()

            for process in data['behavior']['processes']:
                if not process['calls']: # callsになにも格納されていないとき
                    continue
                calls = process['calls']
                for call in calls:
                    calls_all.append({'time': call['time'],
                                      'category': call['category'],
                                      'apiname': call['api'],
                                      'apiurl': self.get_api_refurl(call['api']),
                                      'arguments': call['arguments'],
                                      'status': call['status'],
                                      'return_value': call['return_value']}
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

    def search_api(self, apiname):
        """
        DBから与えられたAPI名を抽出する。
        """
        pass
