# ROS2 Jazzy 講習 — Action通信 実装課題

## 📌 この課題で学ぶこと

| 概念 | 内容 |
|------|------|
| **Action** | 「長時間かかる処理」を途中経過付きで実行する非同期通信 |
| **Goal** | クライアント → サーバーへの「指示」 |
| **Feedback** | サーバー → クライアントへの「途中経過報告」（何度でも送れる） |
| **Result** | サーバー → クライアントへの「最終結果」（処理完了時に1回だけ） |
| **ActionServer** | ゴールを受け取り処理を実行してフィードバックと結果を返す側 |
| **ActionClient** | ゴールを送り、フィードバックを受け取りながら結果を待つ側 |

### Topic・Service・Action の使い分け

```
【Topic】  一方向・継続的・応答なし
  Publisher ──(センサー値を垂れ流す)──► Subscriber
  例: LiDARのスキャンデータを常に配信

【Service】 双方向・即時・短い処理
  Client ──(リクエスト)──► Server ──(レスポンス)──► Client
  例: 座標変換、パラメータ取得

【Action】  双方向・非同期・長時間処理・途中経過あり
  Client ──(Goal)──► Server
  Client ◄──(Feedback × N)── Server   ← 何度でも途中報告
  Client ◄──(Result × 1)── Server     ← 処理完了で1回だけ
  例: ナビゲーション、把持動作、長い計算処理
```

---

## 🗂 ディレクトリ構成

```
ros2_action_workshop/
├── exercise/                                ← 【あなたが編集するフォルダ】
│   ├── package.xml
│   ├── setup.py
│   ├── setup.cfg
│   ├── resource/ros2_action_sample
│   └── ros2_action_sample/
│       ├── __init__.py
│       ├── action_server_node.py            ← Server 実装課題
│       └── action_client_node.py            ← Client 実装課題
│
└── answer/                                  ← 【完成版（最後まで詰まったら参照）】
    └── ros2_action_sample/
        ├── action_server_node.py
        └── action_client_node.py
```

---

## 🔧 事前準備：ワークスペースへのコピーとビルド

```bash
# exercise フォルダをワークスペースに配置
cp -r exercise ~/ros2_ws/src/ros2_action_sample

# ビルド
cd ~/ros2_ws
colcon build --packages-select ros2_action_sample

# 環境の読み込み（毎回新しいターミナルを開いたあとに必要）
source install/setup.bash
```

---

## 📌 使用するアクション型：Fibonacci

今回は ROS2 標準の `example_interfaces/action/Fibonacci` を使います。

```
# ゴール（Clientが送る）
int32 order        ← 何番目まで計算するか
---
# 結果（Serverが返す）
int32[] sequence   ← 完成したフィボナッチ数列
---
# フィードバック（Serverが途中で送る）
int32[] partial_sequence  ← 計算途中の数列
```

型の定義を確認するには:
```bash
ros2 interface show example_interfaces/action/Fibonacci
```

---

## 📝 課題 1：Action Server を実装する

### ファイル
`exercise/ros2_action_sample/action_server_node.py`

### 目標
`order` を受け取り、フィボナッチ数列を1ステップずつ計算しながらフィードバックを送り、最終結果を返す Action Server を完成させる。

### TODO 一覧

| # | 場所 | やること |
|---|------|---------|
| (1) | `__init__` の先頭 | `super().__init__()` でノード名を設定 |
| (2) | `__init__` | `ActionServer()` で Action Server を作成 |
| (3) | `execute_callback` | `goal_handle.request.order` を取り出す |
| (4) | `execute_callback` | `Fibonacci.Feedback()` オブジェクトを作成 |
| (5) | `execute_callback` | `partial_sequence` をセットして `publish_feedback()` で送信 |
| (6) | `execute_callback` | `goal_handle.succeed()` で成功を報告 |
| (7) | `execute_callback` | `Fibonacci.Result()` を作成して `return` |

### API リファレンス

```python
from rclpy.action import ActionServer

# Action Server 作成
self._action_server = ActionServer(
    self,            # ノード（self）
    Fibonacci,       # アクション型
    'fibonacci',     # アクション名
    self.execute_callback  # コールバック
)

# コールバック内でのフィードバック送信
feedback_msg = Fibonacci.Feedback()
feedback_msg.partial_sequence = sequence       # リストをセット
goal_handle.publish_feedback(feedback_msg)     # 送信

# 処理完了の報告と結果の返送
goal_handle.succeed()                          # 成功を宣言（必須）
result = Fibonacci.Result()
result.sequence = sequence
return result                                  # 結果を返す
```

### 動作確認

```bash
# ターミナル1：Server を起動
ros2 run ros2_action_sample action_server

# 期待されるログ（Client起動後）:
# [INFO] Action Serverノードを起動しました。Goalを待機中...
# [INFO] Goal受信: order=10
# [INFO] フィードバック送信: [0, 1, 1]
# [INFO] フィードバック送信: [0, 1, 1, 2]
# ...
# [INFO] Result送信: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

---

## 📝 課題 2：Action Client を実装する

### ファイル
`exercise/ros2_action_sample/action_client_node.py`

### 目標
`order=10` のゴールを送り、フィードバックを受け取りながら最終結果を表示する Action Client を完成させる。

### TODO 一覧

| # | 場所 | やること |
|---|------|---------|
| (1) | `__init__` の先頭 | `super().__init__()` でノード名を設定 |
| (2) | `__init__` | `ActionClient()` で Action Client を作成 |
| (3) | `send_goal` | `Fibonacci.Goal()` を作成して `order` をセット |
| (4) | `send_goal` | `send_goal_async()` でゴールを送信 |
| (5) | `send_goal` | `goal_handle.get_result_async()` で結果を取得 |
| (6) | `send_goal` | `result_future.result().result` から結果を取り出してログ出力 |
| (7) | `feedback_callback` | `partial_sequence` をログに出力 |

### API リファレンス

```python
from rclpy.action import ActionClient

# Action Client 作成
self._action_client = ActionClient(self, Fibonacci, 'fibonacci')

# ゴールの送信（フィードバックコールバックを登録）
goal_msg = Fibonacci.Goal()
goal_msg.order = 10

send_goal_future = self._action_client.send_goal_async(
    goal_msg,
    feedback_callback=self.feedback_callback   # フィードバック受信時に呼ばれる
)
rclpy.spin_until_future_complete(self, send_goal_future)
goal_handle = send_goal_future.result()        # ゴールハンドルを取得

# 結果の取得
result_future = goal_handle.get_result_async()
rclpy.spin_until_future_complete(self, result_future)
result = result_future.result().result         # .result().result の二重アクセスに注意

# フィードバックコールバックのシグネチャ
def feedback_callback(self, feedback_msg):
    partial = feedback_msg.feedback.partial_sequence
```

### 動作確認

```bash
# ターミナル1：先に Server を起動しておく
ros2 run ros2_action_sample action_server

# ターミナル2：Client を起動
ros2 run ros2_action_sample action_client

# 期待されるログ（ターミナル2）:
# [INFO] Action Clientノードを起動しました
# [INFO] Goal送信: order=10
# [INFO] Goalが受理されました。結果を待機中...
# [INFO] フィードバック受信: [0, 1, 1]
# [INFO] フィードバック受信: [0, 1, 1, 2]
# ...
# [INFO] Result受信: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

---

## 🔍 デバッグ用コマンド集

```bash
# Actionサーバー一覧の表示
ros2 action list

# Actionの型を確認
ros2 action type /fibonacci

# アクション型の定義を表示
ros2 interface show example_interfaces/action/Fibonacci

# コマンドラインからゴールを送る（Serverの動作確認に使える）
ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci \
  "{order: 5}" --feedback

# ノード一覧
ros2 node list

# ノードの詳細（どのアクションを持っているか）
ros2 node info /minimal_action_server
ros2 node info /minimal_action_client
```

---

## ✅ チェックリスト

- [ ] `action_server` を起動するとゴール待機のログが表示される
- [ ] `action_client` を起動するとフィードバックが段階的に表示される
- [ ] 最終的に `Result受信: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]` が表示される
- [ ] `ros2 action list` に `/fibonacci` が表示される
- [ ] `ros2 action send_goal` コマンドでも動作する
- [ ] Client は結果受信後に自動終了する
