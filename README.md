# 人協働マニピュレーション実装講座(ROS2) コマンド集

講座資料（Vol.1 / Vol.2）に掲載されているコマンドをまとめたものです。
コピー＆ペーストしやすいように、行頭の `$` は省いています。

> **ターミナルでのコピー・貼り付け（Ubuntu MATE）**
> - ターミナルを開く：`Ctrl + Alt + T`（または Terminator）
> - コピー：`Ctrl + Shift + C`
> - 貼り付け：`Ctrl + Shift + V`
> - 実行中のプログラムを止める：`Ctrl + C`

---

## 目次

- [Vol.1](#vol1)
  - [1. Parameter（パラメータ）](#1-parameterパラメータ)
  - [2. ROS2環境構築（Dockerなし）](#2-ros2環境構築dockerなし)
  - [3. ROS2環境構築（Docker）](#3-ros2環境構築docker)
  - [4. 動作確認（talker / listener）](#4-動作確認talker--listener)
  - [5. ROS2ビルド方法](#5-ros2ビルド方法)
  - [6. ROS2通信実装（Topic / Service / Action）](#6-ros2通信実装topic--service--action)
- [Vol.2](#vol2)
  - [7. SEED-Noid-Mover開発環境構築](#7-seed-noid-mover開発環境構築)
  - [8. launchファイル](#8-launchファイル)
  - [9. SEED-Noid-Moverの動作確認（Gazebo）](#9-seed-noid-moverの動作確認gazebo)
  - [10. 人協働マニピュレーション実装教材](#10-人協働マニピュレーション実装教材)
  - [11. 自律動作 ⇄ 非自律動作 動作確認](#11-自律動作--非自律動作-動作確認)

---

# Vol.1

## 1. Parameter（パラメータ）

**参照：Vol.1 p.27**

| コマンド | 内容 |
|---|---|
| `ros2 param list` | パラメータ名の一覧表示 |
| `ros2 param get` | パラメータの値と型の取得 |
| `ros2 param set` | パラメータの値変更 |

パラメータ宣言（Pythonコード内）：

```python
self.declare_parameter('max_speed', 1.5)
```

ノード起動時に次のオプションを付けると、デフォルト値を上書きできます。

```bash
--ros-args -p max_speed:=2.0
```

---

## 2. ROS2環境構築（Dockerなし）

### 2-1. ロケール設定

**参照：Vol.1 p.31**

```bash
sudo apt update && sudo apt upgrade
sudo apt install locales
sudo locale-gen ja_JP ja_JP.UTF-8
sudo update-locale LC_ALL=ja_JP.UTF-8 LANG=ja_JP.UTF-8
export LANG=ja_JP.UTF-8
```

確認：

```bash
locale
```

`LANG=ja_JP.UTF-8` と表示されればOKです。

### 2-2. 必要ツールのインストール

```bash
sudo apt install -y curl gnupg lsb-release git software-properties-common python3-pip
```

### 2-3. ROS2 aptリポジトリ追加

**参照：Vol.1 p.32**

```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
```

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### 2-4. ROS2 Jazzyインストール

```bash
sudo apt update
sudo apt install ros-jazzy-desktop
sudo apt install -y ros-jazzy-rqt-graph ros-jazzy-ros2-controllers ros-jazzy-ros2-control-test-assets ros-jazzy-ros2-control ros-jazzy-ros-gz ros-jazzy-gz-ros2-control
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-vcstool python3-colcon-clean
```

### 2-5. 環境設定（起動時に読み込まれるように設定）

**参照：Vol.1 p.33**

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2-6. rosdep初期化

```bash
sudo rosdep init
rosdep update
```

### 2-7. パッケージインストール

```bash
sudo apt install ros-${ROS_DISTRO}-nav2-bringup \
ros-${ROS_DISTRO}-laser-proc \
ros-${ROS_DISTRO}-laser-filters \
ros-${ROS_DISTRO}-ros2-control-cmake \
ros-${ROS_DISTRO}-tf-transformations \
ros-${ROS_DISTRO}-moveit \
ros-${ROS_DISTRO}-moveit-ros-planning-interface \
ros-${ROS_DISTRO}-moveit-core \
ros-${ROS_DISTRO}-moveit-common \
ros-${ROS_DISTRO}-moveit-ros-planning \
ros-${ROS_DISTRO}-moveit-visual-tools \
mplayer \
ros-${ROS_DISTRO}-joy-linux
```

---

## 3. ROS2環境構築（Docker）

### 3-1. WSL2のメモリ・プロセッサ設定（Windows側）

**参照：Vol.1 p.35**

Gazeboでシミュレーションを行うため、WSL2で使えるメモリ・プロセッサを設定します。
ファイル `C:\Users\<ユーザ名>\.wslconfig` に以下を記述します（値はホストPCのスペックに合わせて変更）。

```ini
[wsl2]
memory=24GB
processors=6
swap=8GB
```

> 例：メモリ 32GB → 24GB、プロセッサ 8core → 6core
> ホストPCのスペックはタスクマネージャーで確認できます。

設定が完了したら、**PowerShell** から以下を実行します。

```powershell
wsl --shutdown
```

### 3-2. ROS2のDocker環境をクローン・ビルド（WSL2内）

**参照：Vol.1 p.36**

```bash
git clone -b ros2-jazzy https://github.com/rsdlab/docker-ros2-desktop-vnc.git
cd docker-ros2-desktop-vnc/jazzy
docker build -t tiryoh/ros2-desktop-vnc:jazzy .
```

### 3-3. Dockerコンテナを起動

```bash
docker run -p 6080:80 --shm-size=512m tiryoh/ros2-desktop-vnc:jazzy
```

または、Docker Desktopの「Containers」から、ビルドしたコンテナの「▷」を押します。
コンテナが起動したら、ブラウザで http://127.0.0.1:6080/ にアクセスします。

### 3-4. noVNCが使用できない場合

**参照：Vol.1 p.38–39**

https://www.tightvnc.com/download.php から TightVNC をダウンロードします。

Dockerイメージのビルド：

```bash
docker build -t tiryoh/ros2-desktop-vnc:jazzy .
```

Dockerコンテナの起動（ポート5901も開ける）：

```bash
docker run -p 6080:80 -p 5901:5901 --shm-size=512m tiryoh/ros2-desktop-vnc:jazzy
```

TightVNCの Remote Host に `localhost:5901` を入力して接続します（パスワード：`ubuntu`）。

---

## 4. 動作確認（talker / listener）

**参照：Vol.1 p.43**

ターミナルを2つ開いて実行します。

**ターミナル1**

```bash
ros2 run demo_nodes_cpp listener
```

**ターミナル2**

```bash
ros2 run demo_nodes_cpp talker
```

---

## 5. ROS2ビルド方法

### 5-1. サンプルビルド

**参照：Vol.1 p.44**

```bash
mkdir -p ~/colcon_ws/src
cd ~/colcon_ws/src
git clone https://github.com/ros2/examples.git -b jazzy
cd ~/colcon_ws
colcon build
source install/setup.bash
```

### 5-2. サンプル実行

**参照：Vol.1 p.45**

別々のターミナルで起動します（`Ctrl + C` で停止）。

**ターミナル1**

```bash
ros2 run examples_rclcpp_minimal_subscriber subscriber_lambda
```

**ターミナル2**

```bash
ros2 run examples_rclcpp_minimal_publisher publisher_lambda
```

### 5-3. ディレクトリ構成

**参照：Vol.1 p.46**

```text
colcon_ws
├── build    中間生成物（CMakeのキャッシュ・オブジェクトファイル・コンパイル途中の成果物）
├── install  最終成果物（実行ファイル・ライブラリ・package.xml）
├── log      ビルド・実行時のログ
└── src      ビルドに必要なソースファイル
```

### 5-4. colcon build のオプション

| オプション | 内容 |
|---|---|
| `--packages-select <pkg>` | 指定パッケージのみビルド |
| `--packages-up-to <pkg>` | 指定パッケージとその依存を順にビルド |
| `--symlink-install` | install先をシンボリックリンク化（再ビルド負荷を軽減） |
| `--cmake-args -DCMAKE_BUILD_TYPE=Release` | CMakeへ引数を渡す（例：リリースビルド） |
| `--parallel-workers N` | 並列ビルド数を指定（N＝同時実行数） |
| `--event-handlers console_direct+` | ビルドログをリアルタイム表示 |

---

## 6. ROS2通信実装（Topic / Service / Action）

### 6-1. 事前準備

**参照：Vol.1 p.48**

```bash
mkdir -p ~/colcon_ws/src
cd ~/colcon_ws/src
mkdir ros2_topic_sample ros2_service_sample ros2_action_sample
```

### 6-2. Topic通信

**参照：Vol.1 p.51**

ビルド：

```bash
cd ~/colcon_ws
colcon build --packages-select ros2_topic_sample
source install/setup.bash
```

実行：

**ターミナル1**

```bash
ros2 run ros2_topic_sample listener
```

**ターミナル2**

```bash
ros2 run ros2_topic_sample talker
```

### 6-3. Service通信

**参照：Vol.1 p.54**

ビルド：

```bash
cd ~/colcon_ws
colcon build --packages-select ros2_service_sample
source install/setup.bash
```

実行：

**ターミナル1**

```bash
ros2 run ros2_service_sample service_server
```

**ターミナル2**

```bash
ros2 run ros2_service_sample service_client
```

### 6-4. Action通信

**参照：Vol.1 p.56**

ビルド：

```bash
cd ~/colcon_ws
colcon build --packages-select ros2_action_sample
source install/setup.bash
```

実行：

**ターミナル1**

```bash
ros2 run ros2_action_sample action_server
```

**ターミナル2**

```bash
ros2 run ros2_action_sample action_client
```

---

# Vol.2

## 7. SEED-Noid-Mover開発環境構築

### 7-1. ワークスペース作成（seed_robot_ros2_pkg）

**参照：Vol.2 p.8**

```bash
mkdir -p ~/colcon_ws/src
cd ~/colcon_ws/src
git clone -b ros2-jazzy https://github.com/rsdlab/seed_robot_ros2_pkg.git
```

### 7-2. サブモジュールアップデート

```bash
cd ~/colcon_ws/src/seed_robot_ros2_pkg
git submodule update --init --recursive
```

### 7-3. パッチ適用

```bash
patch -p0 < patch/urg_node2.patch
```

### 7-4. ロボットプロジェクトのクローン

**参照：Vol.2 p.9**

```bash
cd ~/colcon_ws/src/seed_robot_ros2_pkg/robots
git clone -b ros2-jazzy https://github.com/rsdlab/noid_lifter_mover.git
```

### 7-5. ビルド

```bash
cd ~/colcon_ws
colcon build --symlink-install
source install/setup.bash
```

### 7-6. udev設定（実機を動かす場合のみ）

**参照：Vol.2 p.10**

ロボットのUSBをPCにまだ登録していない場合に実行します。
（`/etc/udev/rules.d/90-aero.rules` がすでにある場合は不要です。）

```bash
cd ~/colcon_ws/src/seed_robot_ros2_pkg/scripts
./make_udev_install.sh
```

実行すると以下のメッセージが表示されます。

```text
udevファイルをコピーします
完了しました
```

### 7-7. Gazebo用パッケージをクローン

**参照：Vol.2 p.11**

```bash
cd ~/colcon_ws/src
git clone https://github.com/ros-controls/gz_ros2_control.git -b jazzy
touch gz_ros2_control/gz_ros2_control_demos/COLCON_IGNORE
```

### 7-8. 移動機能パッケージをクローン

```bash
cd ~/colcon_ws/src
git clone -b ros2-jazzy https://github.com/rsdlab/Mobility_Function.git
```

### 7-9. 人協働マニピュレーションパッケージをクローン

**参照：Vol.2 p.12**

```bash
cd ~/
git clone -b ros2-jazzy https://github.com/rsdlab/Human_Collaboration_System.git
cd Human_Collaboration_System/
cp Seed-noid/* ~/colcon_ws/src
```

### 7-10. ビルド

```bash
cd ~/colcon_ws
colcon build --symlink-install
source install/setup.bash
```

---

## 8. launchファイル

**参照：Vol.2 p.15**

起動コマンドの書式：

```bash
ros2 launch <package> <launch_file>
```

---

## 9. SEED-Noid-Moverの動作確認（Gazebo）

### 9-1. Gazeboの起動

**参照：Vol.2 p.17**

```bash
ros2 launch noid_lifter_mover bringup_gazebo.launch.py
```

| 操作 | マウス操作 |
|---|---|
| 視点を回転 | ホイールクリック（または Shift＋左クリック）しながらドラッグ |
| 視点を平行移動 | 左クリックしながらドラッグ |
| ズームイン／アウト | マウスホイールを回す（または右クリックしながらドラッグ） |

### 9-2. 動作確認

**参照：Vol.2 p.18**

以下のコマンドを、**それぞれ別のターミナル**で順番に実行します。

> **補足（資料外）**：新しく開いたターミナルでは、最初に
> `source ~/colcon_ws/install/setup.bash`
> を実行しておかないと、パッケージが見つからないエラーになります。

**ターミナル1**

```bash
ros2 launch noid_lifter_mover bringup_gazebo.launch.py
```

**ターミナル2**

```bash
ros2 run map_management map_management_node
```

**ターミナル3**

```bash
ros2 run node_transformation get_environment_coordinates_server
```

**ターミナル4**

```bash
ros2 run workpieces_detection_subsystem WorkpiecesDetectionNode
```

**ターミナル5**

```bash
ros2 run place_position_detection_subsystem PlacePositionDetectionNode
```

**ターミナル6**

```bash
ros2 run collaboration_manipulation_module CollaborationManipulationModule --ros-args -p use_sim_time:=true
```

**ターミナル7**

```bash
ros2 run mobile_robot_navigation_module mobile_robot_navigation_node --ros-args -p use_sim_time:=true
```

**ターミナル8**

```bash
ros2 run external_app pose_hint_client
```

**ターミナル9**

```bash
ros2 run management_system ManagementSystemNode --ros-args -p use_sim_time:=true
```

### 9-3. Gazeboでロボットが動かない場合

**参照：Vol.2 p.19**

Gazeboの影の描画をオフにします。
ファイル `seed_robot_ros2_pkg/robots/noid_lifter_mover/world/seed_noid.sdf`（27行目）を編集します。

変更前：

```xml
<cast_shadows>true</cast_shadows>
```

変更後：

```xml
<cast_shadows>false</cast_shadows>
```

---

## 10. 人協働マニピュレーション実装教材

### 10-1. 教材をクローン

**参照：Vol.2 p.30**

```bash
cd ~/colcon_ws/src
git clone https://github.com/rsdlab/seed_training.git
```

### 10-2. ビルド

`{package_name}` の部分は、ビルドしたいパッケージ名に置き換えてください。

```bash
cd ~/colcon_ws
colcon build --packages-select {package_name}
source install/setup.bash
```

### 10-3. 演習ファイルの場所

**参照：Vol.2 p.31–34**

| 演習 | 実装するファイル | 資料記載の「ファイルの場所」 |
|---|---|---|
| 周辺環境・人検出 | `intrusion_detection_exercise/` 内のファイル | `collaboration_manipulation/peripheral_environment_detection_subsystem/peripheral_environment_detection_subsystem/PerEnvDetectNode.py` |
| ワーク検出 | `workpieces_detection_exercise/` 内のファイル | `collaboration_manipulation/workpieces_detection_subsystem/workpieces_detection_subsystem/WorkpiecesDetectionNode.py` |
| 上位アプリからの作業指示 | `management_system_exercise/` 内のファイル | `collaboration_manipulation/management_system/management_system/ManagementSystemNode.py` |
| 自律 ⇄ 非自律 切り替え | `collaboration_manipulation_training/` 内の TODO-1〜6 | `collaboration_manipulation_training/collaboration_manipulation_training/` |

人検出の演習で、人を検知したときに表示されるログの例：

```text
[WARN] [1781661036.208017296] [move_planner]: Human detected (/intrusion_result=1). Pausing before next motion...
```

---

## 11. 自律動作 ⇄ 非自律動作 動作確認

**参照：Vol.2 p.35**

ロボットなし（`--dummy`）で、状態の切り替えを確認します。
以下を**それぞれ別のターミナル**で実行します。

**ターミナル1**

```bash
ros2 launch noid_lifter_mover bringup_gazebo.launch.py
```

**ターミナル2**

```bash
ros2 run workpieces_detection_subsystem WorkpiecesDetectionNode
```

**ターミナル3**

```bash
ros2 run place_position_detection_subsystem PlacePositionDetectionNode
```

**ターミナル4**

```bash
ros2 run collaboration_manipulation_training CollaborationManipulationModule --dummy
```

**ターミナル5**

```bash
ros2 run collaboration_manipulation_training TaskSender --loop 0 6
```

**ターミナル6**

```bash
ros2 run collaboration_manipulation_training CollaborationSwitcher
```

ターミナル6で使うキー：

| キー | 動作 |
|---|---|
| `b` | 協働作業開始 |
| `e` | 協働作業終了 |
| `p` | 一時停止 |
| `r` | 再開 |
| `s` | 状態確認 |

**確認すること**

- 状態値が **52（自律動作中）→ 84（非自律動作中）→ 52** と変わること
- 非自律動作中は、1動作が遅くなること（3秒 → 10秒）