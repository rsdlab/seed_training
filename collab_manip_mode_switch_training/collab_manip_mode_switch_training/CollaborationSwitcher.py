#!/usr/bin/env python3
# coding: UTF-8
#
# 上位アプリの例（完成品：編集不要）
#
# 自律動作中 ⇄ 非自律動作中 の切り替えを、確認を挟みながら呼び出す.
# キーボードの b / e を、操作パネルの「協働作業開始」「協働作業終了」ボタンの代わりにしている.
#
#   b : 協働作業開始  /start_manip_task を呼び、速度制限がかかった(state=84)のを確認する
#   e : 協働作業終了  人がいないことを確認してから /stop_manip_task を呼ぶ
#   p : 一時停止      /pause_task を呼び、ロボットが止まった(state=132)のを確認する
#   r : 再開          人がいないことを確認してから /resume_task を呼ぶ
#   s : 状態確認  /get_status_server の状態値を表示する
#   q : 終了
#
#   ros2 run collab_manip_mode_switch_training CollaborationSwitcher
#
# ※ これは ROS のサービスによる運用上の切り替えで、安全機能ではない.
#    人が作業範囲に入る運用では、安全規格に適合した停止手段を別に用意すること.

import threading
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Int16

from collaboration_manipulation_message.srv import (
    GetStatus,
    PauseTask,
    ResumeTask,
    StartManipulationTask,
    StopManipulationTask,
)

SUCCEEDED = 1
PRECONDITION_NOT_MET = 3
STATE_NAMES = {1: '初期化中', 2: '待機中', 12: '準備中', 52: '自律動作中', 84: '非自律動作中', 132: '一時停止中'}
STATE_NONOPERATING = 84
STATE_PAUSED = 132
SWITCH_TIMEOUT = 30.0


class CollaborationSwitcher(Node):
    def __init__(self):
        super().__init__('collaboration_switcher')
        cb = ReentrantCallbackGroup()
        self.start_cli = self.create_client(StartManipulationTask, 'start_manip_task', callback_group=cb)
        self.stop_cli = self.create_client(StopManipulationTask, 'stop_manip_task', callback_group=cb)
        self.status_cli = self.create_client(GetStatus, 'get_status_server', callback_group=cb)
        self.pause_cli = self.create_client(PauseTask, 'pause_task', callback_group=cb)
        self.resume_cli = self.create_client(ResumeTask, 'resume_task', callback_group=cb)
        #人検知の結果（1 = 人がいる）.
        self.human_present = False
        self.create_subscription(Int16, '/intrusion_result', self._intrusion_cb, 10, callback_group=cb)

    def _intrusion_cb(self, msg):
        self.human_present = (msg.data != 0)

    #サービスを呼んで応答を返す. 応答がなければ None.
    def _call(self, client, request, timeout=5.0):
        if not client.wait_for_service(timeout_sec=timeout):
            self.get_logger().error(f'{client.srv_name} が見つかりません')
            return None
        future = client.call_async(request)
        end = time.time() + timeout
        while rclpy.ok() and not future.done() and time.time() < end:
            time.sleep(0.01)
        return future.result() if future.done() else None

    #現在の状態値を取得する. 取得できなければ None.
    def get_state(self):
        res = self._call(self.status_cli, GetStatus.Request())
        return None if res is None else res.status.state

    #協働作業開始：ロボットを非自律動作中にして、速度制限がかかったのを確認する.
    def begin_collaboration(self):
        res = self._call(self.start_cli, StartManipulationTask.Request())
        if res is None:
            return False
        if res.return_code == PRECONDITION_NOT_MET:
            self.get_logger().warn('今は切り替えられません（自律動作中ではありません）')
            return False
        if res.return_code != SUCCEEDED:
            self.get_logger().error(f'切り替えに失敗しました（return_code={res.return_code}）')
            return False

        #受け付けただけ. 実行中の動作が終わり、次の動作から速度制限がかかるまで待つ.
        self.get_logger().info('切り替え中... まだエリアに入らないでください')
        end = time.time() + SWITCH_TIMEOUT
        while rclpy.ok() and time.time() < end:
            if self.get_state() == STATE_NONOPERATING:
                self.get_logger().info('速度制限を確認しました. エリアに入ってかまいません（ロボットは低速で動き続けます）')
                return True
            time.sleep(0.2)
        self.get_logger().error('時間内に非自律動作中になりませんでした. エリアに入らないでください')
        return False

    #協働作業終了：人がいないことを確認してから、自律動作中に戻す.
    def end_collaboration(self):
        if self.human_present:
            self.get_logger().warn('人を検知しています. エリアから出てからもう一度押してください')
            return False
        res = self._call(self.stop_cli, StopManipulationTask.Request())
        if res is None:
            return False
        if res.return_code == PRECONDITION_NOT_MET:
            self.get_logger().warn('戻せません（非自律動作中ではありません）')
            return False
        if res.return_code != SUCCEEDED:
            self.get_logger().error(f'戻すのに失敗しました（return_code={res.return_code}）')
            return False
        self.get_logger().info('自律動作に戻しました（次の動作から通常速度）')
        return True

    #一時停止：実行中の動作が終わったところで止め、止まったのを確認する.
    def pause(self):
        req = PauseTask.Request()
        req.instructor = 'CollaborationSwitcher'
        res = self._call(self.pause_cli, req)
        if res is None:
            return False
        if res.return_code == PRECONDITION_NOT_MET:
            self.get_logger().warn('今は一時停止できません（自律動作中・非自律動作中ではありません）')
            return False
        if res.return_code != SUCCEEDED:
            self.get_logger().error(f'一時停止に失敗しました（return_code={res.return_code}）')
            return False

        #受け付けただけ. 実行中の動作が終わって止まるまで待つ.
        self.get_logger().info('停止中... まだエリアに入らないでください')
        end = time.time() + SWITCH_TIMEOUT
        while rclpy.ok() and time.time() < end:
            if self.get_state() == STATE_PAUSED:
                self.get_logger().info('ロボットの停止を確認しました. エリアに入ってかまいません')
                return True
            time.sleep(0.2)
        self.get_logger().error('時間内に一時停止中になりませんでした. エリアに入らないでください')
        return False

    #再開：人がいないことを確認してから、一時停止前の状態に戻して続きを動かす.
    def resume(self):
        if self.human_present:
            self.get_logger().warn('人を検知しています. エリアから出てからもう一度押してください')
            return False
        res = self._call(self.resume_cli, ResumeTask.Request())
        if res is None:
            return False
        if res.return_code == PRECONDITION_NOT_MET:
            self.get_logger().warn('再開できません（一時停止中ではありません）')
            return False
        if res.return_code != SUCCEEDED:
            self.get_logger().error(f'再開に失敗しました（return_code={res.return_code}）')
            return False
        self.get_logger().info('作業を再開しました（止まった続きの動作から）')
        return True

    #状態を表示する.
    def show_state(self):
        state = self.get_state()
        if state is not None:
            self.get_logger().info(f'状態: {STATE_NAMES.get(state, "その他")} (state={state})')


def main():
    rclpy.init()
    node = CollaborationSwitcher()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    actions = {'b': node.begin_collaboration, 'e': node.end_collaboration,
               'p': node.pause, 'r': node.resume, 's': node.show_state}
    try:
        while rclpy.ok():
            key = input('b: 協働作業開始 / e: 協働作業終了 / p: 一時停止 / r: 再開 / s: 状態確認 / q: 終了 > ').strip()
            if key == 'q':
                break
            if key in actions:
                actions[key]()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        #spin スレッドが止まってからノードを破棄する（先に破棄すると終了時に異常終了する）.
        executor.shutdown()
        spin_thread.join(timeout=2.0)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
