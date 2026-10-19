"""
ROS2 Jazzy - Action Server サンプル
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action型   : example_interfaces/action/Fibonacci
アクション名: fibonacci
動作        : order で指定した番目までのフィボナッチ数列を計算し、
              1ステップごとにフィードバックを送りながら、
              最終結果をレスポンスとして返す
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Action の3つの通信】
  Goal     : クライアント → サーバー  何をやるか指示する
  Feedback : サーバー → クライアント  途中経過を通知する（何度でも）
  Result   : サーバー → クライアント  最終結果を返す（1回だけ）
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from example_interfaces.action import Fibonacci


class MinimalActionServer(Node):

    def __init__(self):
        super().__init__('minimal_action_server')

        # Action Serverの作成
        # 引数: ノード, アクション型, アクション名, ゴールコールバック
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback
        )

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
        order = goal_handle.request.order
        self.get_logger().info(f'Goal受信: order={order}')

        # フィードバックメッセージオブジェクトを用意
        feedback_msg = Fibonacci.Feedback()

        # フィボナッチ数列の計算（1ステップずつフィードバックを送る）
        sequence = [0, 1]
        for i in range(1, order):
            sequence.append(sequence[-1] + sequence[-2])

            # フィードバック: 現在の数列を途中経過として送信
            feedback_msg.sequence = sequence
            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(f'フィードバック送信: {sequence}')
            time.sleep(0.5)  # 途中経過がわかりやすいよう0.5秒待機

        # ゴール成功を報告
        goal_handle.succeed()

        # 最終結果を返す
        result = Fibonacci.Result()
        result.sequence = sequence
        self.get_logger().info(f'Result送信: {sequence}')
        return result


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
