"""
ROS2 Jazzy - Action Server 実装課題
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【課題】
  order で指定した番目までのフィボナッチ数列を計算し、
  1ステップごとにフィードバックを送りながら最終結果を返す
  Action Server を完成させてください。

【使用するアクション型】
  example_interfaces/action/Fibonacci
    Goal     : int32 order          ← 何番目まで計算するか
    Feedback : int32[] partial_sequence  ← 途中経過の数列
    Result   : int32[] sequence     ← 完成した数列

【完成したときの動作（Serverのログ）】
  [INFO] Action Serverノードを起動しました。Goalを待機中...
  [INFO] Goal受信: order=10
  [INFO] フィードバック送信: [0, 1, 1]
  [INFO] フィードバック送信: [0, 1, 1, 2]
  ...
  [INFO] Result送信: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

【ヒント】
  - (1)〜(7) の TODO を順番に埋めてください
  - Action = Goal（指示）+ Feedback（途中経過）+ Result（最終結果）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from example_interfaces.action import Fibonacci


class MinimalActionServer(Node):

    def __init__(self):
        # TODO (1): 親クラスの __init__ を呼び出してノード名を設定してください
        #           ノード名は 'minimal_action_server' にしてください
        # ↓ ここに書く
        pass  # この行は削除してください

        # TODO (2): Action Server を作成してください
        #           アクション型  : Fibonacci
        #           アクション名  : 'fibonacci'
        #           コールバック  : self.execute_callback
        # HINT: self._action_server = ActionServer(self, 型, 'アクション名', コールバック)
        # ↓ ここに書く

        self.get_logger().info(
            'Action Serverノードを起動しました。Goalを待機中...'
        )

    def execute_callback(self, goal_handle: ServerGoalHandle):
        """
        ゴールを受け取ったときに実行されるコールバック関数

        Args:
            goal_handle: ゴールの情報とフィードバック送信・結果報告のハンドル
                         goal_handle.request.order  : 何番目まで計算するか
        Returns:
            Fibonacci.Result: 計算したフィボナッチ数列全体
        """
        # TODO (3): goal_handle.request.order をローカル変数に取り出してください
        # HINT: order = goal_handle.request.order
        # ↓ ここに書く

        self.get_logger().info(f'Goal受信: order={order}')

        # TODO (4): フィードバック用メッセージオブジェクトを作成してください
        # HINT: feedback_msg = Fibonacci.Feedback()
        # ↓ ここに書く

        # フィボナッチ数列の計算（変更不要）
        sequence = [0, 1]
        for i in range(1, order):
            sequence.append(sequence[-1] + sequence[-2])

            # TODO (5): フィードバックを送信してください
            #           feedback_msg.sequence に現在の sequence をセットし、
            #           goal_handle.publish_feedback() で送信してください
            # HINT: feedback_msg.sequence = sequence
            #       goal_handle.publish_feedback(feedback_msg)
            # ↓ ここに書く

            self.get_logger().info(f'フィードバック送信: {sequence}')
            time.sleep(0.5)

        # TODO (6): ゴール成功を報告してください
        # HINT: goal_handle.succeed()
        # ↓ ここに書く

        # TODO (7): Result オブジェクトを作成し、sequence をセットして return してください
        # HINT: result = Fibonacci.Result()
        #       result.sequence = sequence
        #       return result
        # ↓ ここに書く


def main(args=None):
    rclpy.init(args=args)

    node = MinimalActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Ctrl+C で終了します')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
