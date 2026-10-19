# ROS2 Jazzy 講習 — Topic通信 実装課題

## 📌 この課題で学ぶこと

| 概念 | 内容 |
|------|------|
| **Node** | ROS2の基本実行単位。1つのプログラム = 1つのノード |
| **Topic** | ノード間でメッセージをやり取りする名前付き通信チャネル |
| **Publisher** | トピックへメッセージを **送信** する役割 |
| **Subscriber** | トピックからメッセージを **受信** する役割 |
| **メッセージ型** | 送受信するデータの型（今回は `std_msgs/String`） |

---

## 🗂 ディレクトリ構成

```
ros2_topic_workshop/
├── exercise/                        ← 【あなたが編集するフォルダ】
│   ├── package.xml
│   ├── setup.py
│   ├── setup.cfg
│   ├── resource/ros2_topic_sample
│   └── ros2_topic_sample/
│       ├── __init__.py
│       ├── publisher_node.py        ← Publisher 実装課題
│       └── subscriber_node.py       ← Subscriber 実装課題
│
└── answer/                          ← 【完成版（最後まで詰まったら参照）】
    └── ros2_topic_sample/
        ├── publisher_node.py
        └── subscriber_node.py
```

---

## 🔧 事前準備：ワークスペースへのコピーとビルド

```bash
# exercise フォルダをワークスペースに配置
cp -r exercise ~/ros2_ws/src/ros2_topic_sample

# ビルド
cd ~/ros2_ws
colcon build --packages-select ros2_topic_sample

# 環境の読み込み（毎回新しいターミナルを開いたあとに必要）
source install/setup.bash
```

> 💡 コードを編集するたびに `colcon build` → `source install/setup.bash` を実行してください。

---

## 📝 課題 1：Publisher を実装する

### ファイル
`exercise/ros2_topic_sample/publisher_node.py`

### 目標
`/chatter` トピックへ **0.5秒ごと** に `String` メッセージを配信するノードを完成させる。

### TODO 一覧

| # | 場所 | やること |
|---|------|---------|
| (1) | `__init__` の先頭 | `super().__init__()` でノード名を設定 |
| (2) | `__init__` | `create_publisher()` で Publisher を作成 |
| (3) | `__init__` | `create_timer()` でタイマーを設定 |
| (4) | `timer_callback` | `String()` のインスタンスを生成 |
| (5) | `timer_callback` | `msg.data` に送信文字列をセット |
| (6) | `timer_callback` | `publish()` で配信 + ログ出力 |

### API リファレンス

```python
# Publisher 作成
self.publisher_ = self.create_publisher(
    メッセージ型,   # 例: String
    'トピック名',   # 例: 'chatter'
    キューサイズ    # 例: 10
)

# タイマー作成
self.timer = self.create_timer(
    周期秒,        # 例: 0.5
    コールバック関数  # 例: self.timer_callback
)

# メッセージの作成と配信
msg = String()
msg.data = '送信したい文字列'
self.publisher_.publish(msg)
```

### 動作確認

```bash
# ターミナル1：Publisher を起動
ros2 run ros2_topic_sample talker

# 期待されるログ出力:
# [INFO] Publisherノードを起動しました
# [INFO] 配信: "こんにちは、ROS2! カウント: 0"
# [INFO] 配信: "こんにちは、ROS2! カウント: 1"
# ...
```

---

## 📝 課題 2：Subscriber を実装する

### ファイル
`exercise/ros2_topic_sample/subscriber_node.py`

### 目標
`/chatter` トピックから `String` メッセージを受信して、受信内容をログに表示するノードを完成させる。

### TODO 一覧

| # | 場所 | やること |
|---|------|---------|
| (1) | `__init__` の先頭 | `super().__init__()` でノード名を設定 |
| (2) | `__init__` | `create_subscription()` で Subscriber を作成 |
| (3) | `listener_callback` | 受信カウントをインクリメント |
| (4) | `listener_callback` | `msg.data` の内容をログに出力 |

### API リファレンス

```python
# Subscription 作成
self.subscription = self.create_subscription(
    メッセージ型,      # 例: String
    'トピック名',      # 例: 'chatter'
    コールバック関数,  # 例: self.listener_callback
    キューサイズ       # 例: 10
)

# コールバック関数のシグネチャ
def listener_callback(self, msg: String):
    # msg.data に受信した文字列が入っている
    print(msg.data)
```

### 動作確認

```bash
# ターミナル1：Publisher を起動（課題1が完成していること）
ros2 run ros2_topic_sample talker

# ターミナル2：Subscriber を起動
ros2 run ros2_topic_sample listener

# 期待されるログ出力（ターミナル2）:
# [INFO] Subscriberノードを起動しました。メッセージを待機中...
# [INFO] 受信 [1件目]: "こんにちは、ROS2! カウント: 5"
# [INFO] 受信 [2件目]: "こんにちは、ROS2! カウント: 6"
# ...
```

---

## 🔍 デバッグ用コマンド集

```bash
# 動いているトピックの一覧を表示
ros2 topic list

# トピックに流れているメッセージをリアルタイムで表示
ros2 topic echo /chatter

# メッセージの配信頻度を確認
ros2 topic hz /chatter

# トピックのメッセージ型を確認
ros2 topic type /chatter

# 動いているノードの一覧
ros2 node list

# ノードの詳細（どのトピックをpub/subしているか）
ros2 node info /minimal_publisher
ros2 node info /minimal_subscriber

# コマンドラインからテスト配信（Subscriber の動作確認に使える）
ros2 topic pub /chatter std_msgs/String "data: 'テスト'" --once
```

---

## ✅ チェックリスト

課題が完成したら、以下をすべて確認してください。

- [ ] `talker` を起動するとカウントが増えながらログが表示される
- [ ] `listener` を起動すると受信ログが表示される
- [ ] `ros2 topic list` に `/chatter` が表示される
- [ ] `ros2 topic echo /chatter` でメッセージを確認できる
- [ ] `ros2 node list` に `/minimal_publisher` と `/minimal_subscriber` が表示される
- [ ] Ctrl+C で正常に終了する
