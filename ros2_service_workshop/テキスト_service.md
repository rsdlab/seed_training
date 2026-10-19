# ROS2 Jazzy 講習 — Service通信 実装課題

## 📌 この課題で学ぶこと

| 概念 | 内容 |
|------|------|
| **Service** | 「リクエストを送ったら必ずレスポンスが返る」双方向の同期通信 |
| **Server** | リクエストを受け取り、処理してレスポンスを返す側 |
| **Client** | リクエストを送り、レスポンスを受け取る側 |
| **サービス型** | リクエストとレスポンスの型を定義したもの（今回は `AddTwoInts`）|
| **Future** | 非同期処理の「結果が入る予約済みの箱」。完了するまで待って取り出す |

### Topic と Service の違い

```
【Topic通信】 一方向・非同期・継続的
  Publisher ──(データを垂れ流す)──► Subscriber
  例: センサー値を常に配信する

【Service通信】 双方向・同期・1回ずつ
  Client ──(リクエスト)──► Server
  Client ◄──(レスポンス)── Server
  例: 「計算して」と頼んで結果を受け取る
```

---

## 🗂 ディレクトリ構成

```
ros2_service_workshop/
├── exercise/                            ← 【あなたが編集するフォルダ】
│   ├── package.xml
│   ├── setup.py
│   ├── setup.cfg
│   ├── resource/ros2_service_sample
│   └── ros2_service_sample/
│       ├── __init__.py
│       ├── server_node.py              ← Server 実装課題
│       └── client_node.py             ← Client 実装課題
│
└── answer/                             ← 【完成版（最後まで詰まったら参照）】
    └── ros2_service_sample/
        ├── server_node.py
        └── client_node.py
```

---

## 🔧 事前準備：ワークスペースへのコピーとビルド

```bash
# exercise フォルダをワークスペースに配置
cp -r exercise ~/ros2_ws/src/ros2_service_sample

# ビルド
cd ~/ros2_ws
colcon build --packages-select ros2_service_sample

# 環境の読み込み（毎回新しいターミナルを開いたあとに必要）
source install/setup.bash
```

> 💡 コードを編集するたびに `colcon build` → `source install/setup.bash` を実行してください。

---

## 📌 使用するサービス型：AddTwoInts

今回は ROS2 標準の `example_interfaces/srv/AddTwoInts` を使います。

```
# リクエスト（Clientが送る）
int64 a
int64 b
---
# レスポンス（Serverが返す）
int64 sum
```

型の定義を確認するには:
```bash
ros2 interface show example_interfaces/srv/AddTwoInts
```

---

## 📝 課題 1：Server を実装する

### ファイル
`exercise/ros2_service_sample/server_node.py`

### 目標
`a` と `b` を受け取り、`sum = a + b` を返す Service Server を完成させる。

### TODO 一覧

| # | 場所 | やること |
|---|------|---------|
| (1) | `__init__` の先頭 | `super().__init__()` でノード名を設定 |
| (2) | `__init__` | `create_service()` で Service Server を作成 |
| (3) | `add_two_ints_callback` | `response.sum` に計算結果をセット |
| (4) | `add_two_ints_callback` | `response` を return |

### API リファレンス

```python
# Service Server 作成
self.srv = self.create_service(
    サービス型,        # 例: AddTwoInts
    'サービス名',      # 例: 'add_two_ints'
    コールバック関数   # 例: self.add_two_ints_callback
)

# コールバック関数のシグネチャ
def add_two_ints_callback(self, request, response):
    # request.a, request.b にクライアントからの値が入っている
    response.sum = request.a + request.b
    return response  # ← 必ず return が必要！
```

### 動作確認

```bash
# ターミナル1：Server を起動
ros2 run ros2_service_sample service_server

# 期待されるログ:
# [INFO] Serverノードを起動しました。リクエストを待機中...
# （Clientからリクエストが来ると）
# [INFO] リクエスト受信: a=3, b=5 → sum=8
```

---

## 📝 課題 2：Client を実装する

### ファイル
`exercise/ros2_service_sample/client_node.py`

### 目標
Server に `a=3, b=5` のリクエストを送り、`sum=8` の結果を受け取って表示する Client を完成させる。

### TODO 一覧

| # | 場所 | やること |
|---|------|---------|
| (1) | `__init__` の先頭 | `super().__init__()` でノード名を設定 |
| (2) | `__init__` | `create_client()` で Service Client を作成 |
| (3) | `send_request` | `Request` オブジェクトを作成し `a`, `b` をセット |
| (4) | `send_request` | `call_async()` でリクエストを送信 |
| (5) | `send_request` | `future.result()` を return |

### API リファレンス

```python
# Service Client 作成
self.client = self.create_client(
    サービス型,   # 例: AddTwoInts
    'サービス名'  # 例: 'add_two_ints'
)

# リクエストの作成と送信
request = AddTwoInts.Request()
request.a = 3
request.b = 5

future = self.client.call_async(request)          # 非同期送信
rclpy.spin_until_future_complete(self, future)    # 完了まで待機
result = future.result()                           # 結果の取得
# result.sum に答えが入っている
```

### 動作確認

```bash
# ターミナル1：先に Server を起動しておく
ros2 run ros2_service_sample service_server

# ターミナル2：Client を起動
ros2 run ros2_service_sample service_client

# 期待されるログ（ターミナル2）:
# [INFO] Clientノードを起動しました
# [INFO] 結果受信: 3 + 5 = 8
```

---

## 🔍 デバッグ用コマンド集

```bash
# サービス一覧の表示
ros2 service list

# サービスの型を確認
ros2 service type /add_two_ints

# サービス型の定義を表示
ros2 interface show example_interfaces/srv/AddTwoInts

# コマンドラインから手動でリクエストを送る（Serverの動作確認に使える）
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 10, b: 20}"

# ノード一覧
ros2 node list

# ノードの詳細（どのサービスを提供/利用しているか）
ros2 node info /minimal_server
ros2 node info /minimal_client
```

---

## ✅ チェックリスト

- [ ] `service_server` を起動するとリクエスト待機のログが表示される
- [ ] `service_client` を起動すると `3 + 5 = 8` が表示される
- [ ] `ros2 service list` に `/add_two_ints` が表示される
- [ ] `ros2 service call` コマンドでも正しい結果が返る
- [ ] Client は送信後に自動で終了する（Server は Ctrl+C まで動き続ける）
