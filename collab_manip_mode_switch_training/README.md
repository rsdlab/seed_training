# collab_manip_mode_switch_training

人協働マニピュレーションの **自律動作中 ⇄ 非自律動作中** の切り替えを、自分でコードを書いて確かめる研修用の演習パッケージです。

`collaboration_manipulation/collaboration_manipulation_module` をコピーして作っています。切り替えに必要なところだけを穴あき（TODO）にしてあります。
ロボットがなくても `--dummy` を付けて起動すれば、状態遷移だけを確認できます。

---

## 1. 何を作るのか

作業中（Running → Working）の状態の中で、次の 2 つの状態を行き来できるようにします。

```
                 /start_manip_task（協働作業開始）
   ┌───────────────┐  ───────────────────────────▶   ┌──────────────────┐
   │ 自律動作中     │                                 │ 非自律動作中      │
   │ Operating     │  ◀───────────────────────────   │ NonOperating     │
   │ 制限なしで     │  /stop_manip_task（協働作業終了）│ 速度を 0.3 倍に   │
   │ 作業を進める   │                                 │ 落として作業を    │
   │               │                                 │ 続ける           │
   └───────────────┘                                 └──────────────────┘
          │ 動作がすべて終わる（どちらの状態からでも）
          ▼
   RESULT RECEIVE（作業結果・作業完了を上位へ通知） → Standby（待機中）へ
```

サービスが呼ばれてから状態が切り替わるまでの流れは次のとおりです。各段階が TODO になっています。

```
 ros2 service call /start_manip_task
        │
        ▼
 [TODO-6] サーバを作って executor に登録する（登録しないと呼んでも応答しない）
        │
        ▼
 [TODO-2] 今の状態が自律動作中か確認し、イベント COLLABO を通知する
        │
        ▼
 [TODO-1] 遷移表：自律動作中は COLLABO を受け付け、outcome 'collabo' で抜ける
        │
        ▼
 [TODO-4] smach の遷移先：'collabo' のときは NonOperating へ進む
        │
        ▼
 [TODO-5] 非自律動作中は速度を制限して、自律動作の続きを実行する
          （/stop_manip_task → [TODO-3] → COLLABOEND → 'collaboend' → Operating へ戻る）
```

---

## 2. 仕様

### 自律動作中と非自律動作中

どちらも「作業進行中」の中の状態で、**どちらの状態でも作業は進みます**。違うのは、動きに制限がかかっているかどうかです（人協働マニピュレーション機能インターフェース仕様書 2.7 章）。

| 状態 | 仕様書での意味 | この演習での動き |
|---|---|---|
| 自律動作中 | 制約や外部からの介入なしに、プログラムどおりに動く | 通常の速度で動作する |
| 非自律動作中 | 作業者が近くにいるので、動く範囲・速度・力を制限して動く（または外部の制御信号の影響を受けて動く） | 速度・加速度を `NON_OPERATING_VELOCITY_SCALE`（0.3）倍に落として、同じ作業を続ける |

ロボットを**止める**のは、非自律動作中ではなく「一時停止中」の役割です。一時停止は演習の対象外で、完成品として用意しています（`/pause_task`・`/resume_task`）。

| 状態 | 仕様書での意味 | この演習での動き |
|---|---|---|
| 一時停止中 | 停止すべき要因で止まる。解除すると止まった時点から再開する | その場で止まって `/resume_task` を待つ。再開すると、一時停止の前の状態（自律／非自律）で続きの動作から動く |

### サービス

| サービス名 | 型 | 受け付ける状態 | 動き |
|---|---|---|---|
| `/start_manip_task` | `collaboration_manipulation_message/srv/StartManipulationTask` | 自律動作中のみ | 非自律動作中へ切り替える（協働作業開始） |
| `/stop_manip_task` | `collaboration_manipulation_message/srv/StopManipulationTask` | 非自律動作中のみ | 自律動作中へ戻る（協働作業終了） |
| `/get_status_server` | `collaboration_manipulation_message/srv/GetStatus` | いつでも | 現在の状態値を返す（完成品） |
| `/pause_task` | `collaboration_manipulation_message/srv/PauseTask` | 自律動作中・非自律動作中 | 一時停止中へ移る（完成品）。`instructor` に停止を指示した人の名前を入れる（空でもよい） |
| `/resume_task` | `collaboration_manipulation_message/srv/ResumeTask` | 一時停止中のみ | 一時停止の前の状態へ戻り、続きの動作から再開する（完成品）。`step_ids`（再開する動作ステップの指定）には未対応で、指定しても無視する |

### 戻り値 `return_code`

| 値 | 意味 |
|---|---|
| 1 | 成功（succeeded） |
| 2 | 失敗（failed） |
| 3 | 前提条件不成立（precondition_not_met）：受け付けられない状態で呼ばれた |

### 状態値（`/get_status_server` の `status.state`）

状態値はビットの組み合わせです（`EnumerateModule.py` の `EnumState`）。

| 状態 | 値 |
|---|---|
| 初期化中 Initializing | 1 |
| 待機中 Standby | 2 |
| 準備中 Preparing | 12 |
| **自律動作中 Operating** | **52** |
| **非自律動作中 NonOperating** | **84** |
| 一時停止中 Paused | 132 |

### 切り替わるタイミング

イベントは、ロボットの **1 動作の区切り** で確認されます。動作中に `/start_manip_task` を呼ぶと、その動作は通常の速度のまま最後まで動き、**次の動作から** 速度が制限されます。`/stop_manip_task` も同じで、次の動作から通常の速度に戻ります。
（動作の途中で速度を変えるには、MoveIt の動作目標をキャンセルして計画し直す必要があるため、この演習では扱いません。）

切り替えても、作業は **途中の動作から続き** を実行します（最初からやり直しません）。どこまで動いたか（`work_label`）は、自律動作中と非自律動作中で共有しています。

`/pause_task` も同じく 1 動作の区切りで効きます。実行中の動作が終わったところで止まり、一時停止中（`state=132`）になります。
ただし、作業の **最後の動作中** に呼んだ場合は、止める動作が残っていないため、一時停止せずに作業が完了します（`return_code=1` が返っても `state=132` にはなりません。ターミナル 3 に `一時停止せずに完了します` が出ます）。`TaskSender --loop` では次の作業が始まるので、止めたいときはもう一度 `/pause_task` を呼んでください。

---

## 3. ファイルと TODO

`collab_manip_mode_switch_training/` の中の次の 5 ファイルに TODO があります。各 TODO は `# === TODO-N ===` で始まります。
書く場所は、`# ここから` 〜 `# ここまで` の間か、`# <- ここを書き換える` の行です。

| TODO | ファイル | 内容 | 書く量 |
|---|---|---|---|
| TODO-1 (a)(b) | `TransitionModule.py` | 遷移表：自律動作中で COLLABO、非自律動作中で COLLABOEND を受け付ける | 2 行を書き換える |
| TODO-2 | `CollaborationCommunicationModule.py` | `/start_manip_task` の受信処理（状態を確認してイベントを通知） | 約 5 行 |
| TODO-3 | `CollaborationCommunicationModule.py` | `/stop_manip_task` の受信処理（TODO-2 の逆） | 約 5 行 |
| TODO-4 (a)(b) | `CollaborationStateModule.py` | smach の遷移先：collabo → NonOperating、collaboend → Operating | 2 行を書き換える |
| TODO-5 | `CollaborationUserDefineModule.py` | 非自律動作中の処理：速度を制限して、自律動作の続きを実行する | 2 行 |
| TODO-6 (1)(2) | `CollaborationManipulationModule.py` | サーバを作り、executor に登録する | 4 行 |

ほかのファイルは編集しなくてかまいません。`TaskSender.py` は、作業指令を送る上位アプリの完成品です。

解答は `answer/<ファイル名>_answer.py` にあります（ファイル全体の完成版）。

---

## 4. ビルド

```bash
cd ~/seed_ROS2_ws
colcon build --packages-select collab_manip_mode_switch_training
source install/setup.bash
```

TODO は未記入のままでもビルド・起動できます。何も書かない状態で一度動かし、どう動かないかを見ておくと、違いがわかりやすくなります。

> **注意：同じ LAN で複数人が演習する場合**
> ROS 2 は同じネットワーク上のほかの PC とも通信します。隣の人のモジュールが応答してしまうことがあるので、**ターミナルごとに** 次を実行してから始めてください（番号は 1 人ずつ別の値にします）。
> ```bash
> export ROS_DOMAIN_ID=<自分の番号 1〜100>
> export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
> ```

---

## 5. 実行（ロボットなし：`--dummy`）

ターミナルを 6 つ使います。すべてのターミナルで `source ~/seed_ws/install/setup.bash` を実行しておきます。

**ターミナル 1：ロボットシミュレーションを起動**

```bash
ros2 launch noid_lifter_mover bringup_gazebo.launch.py
```

**ターミナル 2・3：ワーク検出・排出位置検出（準備中に呼ばれるスタブ）**

```bash
ros2 run workpieces_detection_subsystem WorkpiecesDetectionNode
```
```bash
ros2 run place_position_detection_subsystem PlacePositionDetectionNode
```

**ターミナル 4：人協働マニピュレーションモジュール**

```bash
ros2 run collab_manip_mode_switch_training CollaborationManipulationModule --dummy
```

`--dummy` を付けると、MoveIt を使わずに 1 動作 3 秒の模擬動作になります。
`Wait starting ...` が出たら待機中（Standby）です。
（TaskSender を先に起動してもかまいません。待機中になるまで `module is busy (not Standby). retry ...` を出しながら送り直します。）

**ターミナル 5：上位アプリ（作業指令を送る）**

```bash
ros2 run collab_manip_mode_switch_training TaskSender
```

PICK 作業（6 動作、約 18 秒）が始まります。ターミナル 3 に `========== 自律動作中 (Operating) ==========` が出たら、すぐにターミナル 5 で操作します。
間に合わなかったら、作業完了後にもう一度 `TaskSender` を実行してください。

**何度も試したいとき（ループ実行）**

```bash
ros2 run collab_manip_mode_switch_training TaskSender --loop 0 6
```

| 作業指令 ID | 作業 |
|---|---|
| 0 | PICK（初期姿勢 → アプローチ準備 → アプローチ → つかみ → 上昇） |
| 2 | PLACE |
| 6 | 初期姿勢に戻る（上半身 → リフター） |

- 作業と作業の間は、一瞬だけ待機中・準備中になります。このときに `/start_manip_task` や `/pause_task` を呼ぶと `return_code=3` が返ります。少し待ってから呼び直してください。
- Ctrl+C で止めるのは「次の作業指令を送ること」だけです。実行中の作業は、モジュール側で最後まで続きます。ロボットを止めたいときは `/pause_task`（実行中の動作が終わったところで止まる）を、すぐに止めたいときは非常停止を使ってください（`/start_manip_task` で非自律動作中にしても、遅くなるだけで止まりません）。

**ターミナル 6：切り替え・一時停止の操作**

```bash
# 非自律動作中へ切り替える
ros2 service call /start_manip_task collaboration_manipulation_message/srv/StartManipulationTask

# 状態を確認する（84 なら非自律動作中）
ros2 service call /get_status_server collaboration_manipulation_message/srv/GetStatus

# 自律動作中へ戻す
ros2 service call /stop_manip_task collaboration_manipulation_message/srv/StopManipulationTask

# 状態を確認する（52 なら自律動作中）
ros2 service call /get_status_server collaboration_manipulation_message/srv/GetStatus

# 一時停止する（132 なら一時停止中）
ros2 service call /pause_task collaboration_manipulation_message/srv/PauseTask "{instructor: operator}"

# 一時停止を解除する（一時停止の前の状態に戻る）
ros2 service call /resume_task collaboration_manipulation_message/srv/ResumeTask
```

### 上位アプリから切り替える（CollaborationSwitcher）

実際の運用では、`ros2 service call` を手で打つのではなく、上位アプリの中からサービスを呼びます。その例が `CollaborationSwitcher` です（[CollaborationSwitcher.py](collab_manip_mode_switch_training/CollaborationSwitcher.py)、完成品）。ターミナル 5 で、サービス呼び出しの代わりに起動します。

```bash
ros2 run collab_manip_mode_switch_training CollaborationSwitcher
```

キーボードの `b` / `e` / `p` / `r` を、操作パネルの「協働作業開始」「協働作業終了」「一時停止」「再開」ボタンの代わりにしています。

| キー | 動き |
|---|---|
| `b` | 協働作業開始：`/start_manip_task` を呼び、`state=84`（速度制限がかかった）になるまで待ってから「エリアに入ってかまいません」と表示する |
| `e` | 協働作業終了：人検知（`/intrusion_result`）で人がいないことを確認してから `/stop_manip_task` を呼ぶ。人がいるあいだは呼ばない |
| `p` | 一時停止：`/pause_task` を呼び、`state=132`（ロボットが止まった）になるまで待ってから「エリアに入ってかまいません」と表示する |
| `r` | 再開：人検知で人がいないことを確認してから `/resume_task` を呼ぶ。人がいるあいだは呼ばない |
| `s` | 状態確認：現在の状態を表示する |
| `q` | 終了 |

`return_code=1` は「受け付けた」という意味で、その時点ではまだロボットは通常の速度で動いています。そのため `b` では `state=84`（次の動作から速度制限がかかる）に、`p` では `state=132`（止まった）になるのを確かめてから入室の許可を出しています。

人検知のガードを試すときは、別のターミナルで「人がいる」を送ってから `e` または `r` を押します。

```bash
ros2 topic pub -r 5 /intrusion_result std_msgs/msg/Int16 "{data: 1}"   # 人がいる（Ctrl+C で止める）
ros2 topic pub -r 5 /intrusion_result std_msgs/msg/Int16 "{data: 0}"   # 人がいない
```

> これは ROS のサービスによる運用上の切り替えで、安全機能ではありません。人が作業範囲に入る運用では、安全規格に適合した停止手段（安全柵・エリアセンサ・非常停止など）を別に用意してください。

### 終了

終了するときは、次のサービスを呼ぶか、ターミナル 3 で Ctrl+C を押します。

```bash
ros2 service call /terminate_system collaboration_manipulation_message/srv/TerminateSystem
```

---

## 6. 完成ラインのチェックリスト

- [ ] 自律動作中に `/start_manip_task` を呼ぶと `return_code=1` が返る
- [ ] ターミナル 3 に `transitioning 'Operating':'collabo'-->'NonOperating'` と `========== 非自律動作中 (NonOperating) ==========` が出る
- [ ] 非自律動作中も動作は続き、`[DUMMY] ... (10.0 s, velocity x0.3)` のように 1 動作が遅くなる
- [ ] `/get_status_server` の `state` が `84` になる
- [ ] 非自律動作中にもう一度 `/start_manip_task` を呼ぶと `return_code=3`（前提条件不成立）が返る
- [ ] `/stop_manip_task` を呼ぶと `return_code=1` が返り、`'NonOperating':'collaboend'-->'Operating'` が出る
- [ ] 自律動作中に戻ると `state` が `52` になり、`[DUMMY] ... (3.0 s)` の通常の速度で **続きの動作から** 実行する（最初の `upper_body initial pose` からやり直さない）
- [ ] 非自律動作中のまま最後まで動くと、`'NonOperating':'succeeded'-->'RESULT RECEIVE'` が出て作業が完了する
- [ ] 自律動作中に `/stop_manip_task` を呼ぶと `return_code=3` が返る
- [ ] 最後まで動作すると、ターミナル 4 に `done: task_result=True, complete=True` が出る

一時停止（完成品）も試してみましょう。
- [ ] 自律動作中・非自律動作中に `/pause_task` を呼ぶと、動作が止まって `... Paused: waiting for /resume_task` が出て、`state` が `132` になる
- [ ] `/resume_task` を呼ぶと、一時停止の前の状態（`52` か `84`）に戻り、続きの動作から動く

---

## 7. うまくいかないとき

| 症状 | 原因として多いもの |
|---|---|
| `ros2 service call /start_manip_task` が `waiting for service to become available...` のまま進まない | TODO-6 が未記入：サーバを作っていない、または executor に登録していない |
| `return_code=0` が返り、何も起きない | TODO-2 / TODO-3 が未記入：`res.return_code` を設定していない |
| `return_code=1` なのに切り替わらない。ターミナル 3 に `ignore event COLLABO (state=OperatingTran)` が出る | TODO-1 (a) が未記入：遷移表が COLLABO を受け付けていない（COLLABOEND なら TODO-1 (b)） |
| `transitioning 'Operating':'collabo'-->'Operating'` が出て、自律動作をそのまま続ける | TODO-4 (a) の遷移先が `'Operating'` のまま |
| 非自律動作中に切り替わった直後に `TODO-5 が未記入です` が出て、モジュールが終了する | TODO-5 が未記入：非自律動作中の処理を書いていない |
| 非自律動作中なのに `[DUMMY] ... (3.0 s)` のまま遅くならない | TODO-5 で `set_velocity_scale()` を呼んでいない |
| 非自律動作中に切り替わると、作業の最初の動作（`upper_body initial pose`）からやり直す | `operating_work()` ではなく、ほかの動作関数（`pick_move()` など）を直接呼んでいないか確認する |
| `'NonOperating':'collaboend'-->'NonOperating'` が出て、非自律動作中から戻らない | TODO-4 (b) の遷移先が `'NonOperating'` のまま |
| 自律動作中なのに `return_code=3` が返る | TODO-2 の条件が逆（`is_nonoperating()` にしていないか確認する） |
| 起動時に `Waiting for move_action server...` で止まる | `--dummy` を付け忘れている（実機・シミュレータがない場合）。実機では MoveIt の起動が終わるまで待つ |
| TaskSender が `module is busy (not Standby). retry ...` を繰り返す | モジュールがまだ待機中になっていない（実機では MoveIt の起動待ちで数十秒かかる）。待機中になれば自動で送られる |
| `/pause_task` が `return_code=1` なのに `state=132` にならず、`一時停止せずに完了します` が出る | 作業の最後の動作中に呼んだ。止める動作が残っていないので、そのまま作業が完了する（「2. 仕様」の「切り替わるタイミング」参照） |
| 呼んでいないのにイベントが届く、状態がおかしい | 同じ LAN のほかの PC と混線している。「4. ビルド」の注意を参照し、`ROS_DOMAIN_ID` を変える |

コードを直したら、もう一度 `colcon build` と `source install/setup.bash` を実行してから起動し直してください。

終了時に `ExternalShutdownException` のトレースバックが出ることがありますが、終了処理中のものなので問題ありません。

---

## 8. 実機・シミュレータで動かす場合

`--dummy` を付けずに起動すると、MoveIt の `move_action` を使って実際に関節を動かします。先にロボット（またはシミュレータ）と MoveIt を起動しておいてください。

```bash
ros2 run collab_manip_mode_switch_training CollaborationManipulationModule
```

非自律動作中は、MoveIt に送る速度・加速度の倍率（`max_velocity_scaling_factor` / `max_acceleration_scaling_factor`）を 0.3 倍にして動作を続けます（[MovePlannerModule.py](collab_manip_mode_switch_training/MovePlannerModule.py) の `set_velocity_scale()`）。

> 速度を落とすのは運用上の制限で、安全機能ではありません。人とロボットが同じ空間で作業するときの速度・力の制限は、安全規格に適合した安全機能（安全コントローラによる速度・力の監視など）で行ってください。

---

## 9. 解答版で動かす

TODO を埋めずに、完成した動きを確かめたいときは、解答版のモジュールを起動します（講師用）。

```bash
ros2 run collab_manip_mode_switch_training CollaborationManipulationModuleAnswer --dummy   # ロボットなし
ros2 run collab_manip_mode_switch_training CollaborationManipulationModuleAnswer           # 実機・シミュレータ
```

起動すると、最初に `[ANSWER] TransitionModule <- .../answer/TransitionModule_answer.py` のような行が 5 つ出ます。
穴あき版と解答版を同時に起動しないでください（サービス名が同じため）。

### 解答の使い方（ファイルを差し替える）

ファイル全体を差し替えます。

```bash
cd ~/seed_ROS2_ws/src/seed_training/collab_manip_mode_switch_training
cp answer/TransitionModule_answer.py collab_manip_mode_switch_training/TransitionModule.py
# ほかのファイルも同様
```

差分だけを見たいときは、次のコマンドを使います。

```bash
diff collab_manip_mode_switch_training/TransitionModule.py answer/TransitionModule_answer.py
```