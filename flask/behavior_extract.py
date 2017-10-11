# coding: utf-8

from pymongo import MongoClient
from pprint import pprint

class BehaviorExtract(object):
    def __init__(self, dbaddr='localhost', dbport=27017, dbname='mws'):
        # MongoDB接続
        self.connect = MongoClient(dbaddr, dbport)
        # mws DBの取得
        self.db = self.connect.mws


    def get_behavior(self):
        """
        timeをキー、API Call情報を格納した配列を値とする辞書を返す。
        ex)
        {1475696859.157233: [u'NtClose', {u'handle': u'0x00000074'}, 1, 0],
         1475696859.251233: [u'LdrGetDllHandle',
                            {u'module_address': u'0x00000000',
                             u'module_name': u'UnlockUntangling'},
                             0,
                             3221225781L],
        ...} 

        memo: 以下のようなリスト形式にしたほうがいいか？
        (timeは重複がありえるためキーとして扱えない)
        [ {'time': 1475696859.157233, 'apiname': 'NtClose', 'arguments': {'arg1': 'value1', ...}, 'status': 1, 'return_value': 0},
          {'time': 1475696859.251233, 'apiname': 'LdrGetDllHandle', 'arguments': {'arg1': 'value1', ...}, 'status': 1, 'return_value': 0}, ...]
        """

        # json1 collectionの取得
        col = self.db.json1 #test json

        # api callsの取得
        calls_path = "behavior.processes.calls"
        calls_all = []
        calls_dict = {}

        for i in col.find({}, {calls_path+".time":1, calls_path+".api":1, calls_path+".arguments":1, calls_path+".status":1, calls_path+".return_value":1, "behavior.processes.pid":1, "_id":0}):
            data = i
        
            # for debug
            #pprint(i)
            #print data['behavior']['processes'][1]['calls'][0].keys()

            for process in data['behavior']['processes']:
                if not process['calls']: # callsになにも格納されていないとき
                    continue
                calls = process['calls']
                for call in calls:
                    calls_dict[call['time']] = [call['api'], call['arguments'], call['status'], call['return_value']]

        return calls_dict
