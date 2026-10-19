#!/usr/bin/env python3
# coding: UTF-8
#
# 研修用の上位アプリ（完成品：編集不要）
#
# 人協働マニピュレーションモジュールに作業指令を送り、
# 作業結果（notify_task_result）と作業完了（notify_task_completion）を受け取るまで待ちます。
# 作業中（Running）にしておかないと、自律動作中 ⇄ 非自律動作中 の切り替えは試せません。
#
#   ros2 run collab_manip_mode_switch_training TaskSender              # PICK(0) を1回送る
#   ros2 run collab_manip_mode_switch_training TaskSender 2            # PLACE(2) を1回送る
#   ros2 run collab_manip_mode_switch_training TaskSender --loop       # アプローチ(5) -> PICK(0) -> 初期姿勢(6) を繰り返す
#   ros2 run collab_manip_mode_switch_training TaskSender --loop 0 6   # 繰り返す作業を指定する（Ctrl+C で終了）
#
# 作業指令ID: 0=PICK, 1=DOWN, 2=PLACE, 3=RELEASE, 4=SOLVE, 5=アプローチ, 6=初期姿勢

import sys
import threading
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from collaboration_manipulation_message.msg import PlaceAreaCandidatesList, TargetArea, TaskCommand, TaskCommandList
from collaboration_manipulation_message.srv import NotifyTaskCompletion, NotifyTaskResult, SendTaskCommand

from .EnumerateModule import EnumCommandReceiveState

PICK_COMMAND = 0
LOOP_COMMANDS = [5, 0, 6]  # アプローチ -> PICK -> 初期姿勢
COMMAND_NAMES = {0: 'PICK', 1: 'DOWN', 2: 'PLACE', 3: 'RELEASE', 4: 'SOLVE', 5: 'APPROACH', 6: 'INIT'}


class TaskSender(Node):
    def __init__(self):
        super().__init__('task_sender_node')
        cb = ReentrantCallbackGroup()
        self.cmd_client = self.create_client(SendTaskCommand, 'send_command_service', callback_group=cb)
        self.create_service(NotifyTaskResult, 'notify_task_result', self.recv_task_result, callback_group=cb)
        self.create_service(NotifyTaskCompletion, 'notify_task_completion', self.recv_task_complete, callback_group=cb)
        self.task_result = None
        self.task_complete = False

    #作業結果の受信.
    def recv_task_result(self, req, res):
        self.task_result = req.task_result.task_result
        self.get_logger().info(f'<- notify_task_result: task_result={self.task_result}')
        res.return_code = 1
        return res

    #作業完了の受信.
    def recv_task_complete(self, _, res):
        self.task_complete = True
        self.get_logger().info('<- notify_task_completion')
        res.return_code = 1
        return res

    #作業指令を作成する.
    def make_request(self, command_id):
        area = TargetArea()
        area.start_point.x, area.start_point.y, area.start_point.z = -2.0, -2.0, 0.0
        area.end_point.x, area.end_point.y, area.end_point.z = 2.0, 2.0, 2.0

        task = TaskCommand()
        task.task_command_id = command_id
        task.work_type_id = 1
        task.picking_count = 1
        task.work_presence_area = area
        task.place_area_candidates = PlaceAreaCandidatesList()
        task.place_area_candidates.place_area_candidates.append(area)

        req = SendTaskCommand.Request()
        req.task_commands = TaskCommandList()
        req.task_commands.task_commands.append(task)
        return req

    #作業指令を送り、受理されるまで繰り返す.
    def send(self, command_id):
        while not self.cmd_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('waiting for send_command_service ...')
        while rclpy.ok():
            future = self.cmd_client.call_async(self.make_request(command_id))
            while rclpy.ok() and not future.done():
                time.sleep(0.01)
            if future.result().response == EnumCommandReceiveState.e_received():
                self.get_logger().info(f'-> send_command_service: command_id={command_id} received')
                return True
            self.get_logger().warn('module is busy (not Standby). retry ...')
            time.sleep(1.0)
        return False

    #作業完了まで待つ. 成功したら True を返す.
    def wait_done(self):
        while rclpy.ok() and not self.task_complete and self.task_result is not False:
            time.sleep(0.05)
        return self.task_complete and self.task_result is not False

    #作業指令を1つ送り、完了まで待つ.
    def run_once(self, command_id):
        self.task_result = None
        self.task_complete = False
        name = COMMAND_NAMES.get(command_id, '?')
        self.get_logger().info(f'===== {name}({command_id}) を送ります =====')
        if not self.send(command_id):
            return False
        ok = self.wait_done()
        #Ctrl+C で止めた場合はログを出さずに抜ける（終了後はログを出せないため）.
        if not rclpy.ok():
            return False
        self.get_logger().info(f'done {name}: task_result={self.task_result}, complete={self.task_complete}')
        return ok


def main():
    rclpy.init()
    node = TaskSender()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    args = rclpy.utilities.remove_ros_args(sys.argv)[1:]
    try:
        if args and args[0] == '--loop':
            #作業指令を順番に、Ctrl+C で止めるまで繰り返す.
            commands = [int(a) for a in args[1:]] or LOOP_COMMANDS
            names = ' -> '.join(COMMAND_NAMES.get(c, '?') for c in commands)
            node.get_logger().info(f'ループ実行: {names} を繰り返します（Ctrl+C で終了）.')
            node.get_logger().info('作業中に別ターミナルで /start_manip_task, /stop_manip_task を呼んでみましょう.')
            cycle = 0
            while rclpy.ok():
                cycle += 1
                node.get_logger().info(f'---------- {cycle} 周目 ----------')
                for command_id in commands:
                    if node.run_once(command_id):
                        continue
                    if rclpy.ok():
                        node.get_logger().error('作業が失敗したのでループを終了します.')
                    return
        else:
            command_id = int(args[0]) if args else PICK_COMMAND
            node.get_logger().info('作業中に別ターミナルで /start_manip_task, /stop_manip_task を呼んでみましょう.')
            node.run_once(command_id)
    except KeyboardInterrupt:
        pass
    finally:
        #spin スレッドが止まってからノードを破棄する（先に破棄すると終了時に異常終了する）.
        executor.shutdown()
        spin_thread.join(timeout=2.0)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
