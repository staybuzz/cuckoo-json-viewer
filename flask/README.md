# cuckoo-json-viewer

Cuckoo Sandboxで取得したjsonファイルに含まれるAP コール列をブラウザから見られるツールです。

### インストール
#### 必要なパッケージ
* mongodb
```
(Ubuntu) $ sudo apt install mongodb
```

* flask
* pymongo
```
$ pip install flask pymongo
```

#### jsonの読み込み
現時点ではjsonファイルを直接DBにimportする必要があります。

```
$ scripts/json_dbinsert.sh /path/to/cuckoo-report.json
```

API名とMSDNリファレンス辞書もDBにimportします。
```
$ scripts/dict_api_msdn.sh
```

### 使用方法
1. jsonファイルをDBにimport したのち、server.pyを実行します。
```
$ python server.py
```

2. ブラウザから`localhost:5000`へアクセスします。

### 機能
* トップページには全てのAPIコールが順次表示されます。
* カテゴリ名をクリックするとカテゴリでフィルタされます。
* テキストボックスではAPI名や引数の値について検索ができます。
  * テキストを空にして検索することで全てのAPIコールを表示します。
* テキストボックスに入力した状態でカテゴリ名をクリックすると、検索クエリとカテゴリの両方でフィルタします。
* API名をクリックすると、MSDNのリファレンスページ or Google検索画面に飛びます。
  * APIとMSDNのURLの辞書：`2017_api_list.json`。ここに含まれていないAPIはGoogle検索に飛びます。