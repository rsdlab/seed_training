"""
ROS2 Jazzy - Action Client サンプル
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action型   : example_interfaces/action/Fibonacci
アクション名: fibonacci
動作        : order=10 のゴールを送り、
              フィードバック（途中経過）を受け取りながら
              最終結果を表示する
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Action の3つの通信】
  Goal     : クライアント → サーバー  何をやるか指示する
  Feedback : サーバー → クライアント  途中経過を通知する（何度でも）
  Result   : サーバー → クライアント  最終結果を返す（1回だけ）
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from example_interfaces.action import Fibonacci


class MinimalActionClient(Node):

    def __init__(self):
        super().__init__('minimal_action_client')

        # Action Clientの作成
        # 引数: ノード, アクション型, アクション名
        self._action_client = ActionClient(self, Fibonacci, 'fibonacci')

        self.get_logger().info('Action Clientノードを起動しました')

    def send_goal(self, order: int):
        """ゴールを送信し、フィードバックを受け取りながら結果を待つ"""

        # サーバーが起動するまで待機
        self.get_logger().info('Action Serverを待機中...')
        self._action_client.wait_for_server()

        # ゴールメッセージの作成
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info(f'Goal送信: order={order}')

        # ゴールを非同期で送信（フィードバックコールバックを登録）
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # ゴール受理の応答を待つ
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle: ClientGoalHandle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goalが拒否されました')
            return

        self.get_logger().info('Goalが受理されました。結果を待機中...')

        # 最終結果を待つ
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        self.get_logger().info(f'Result受信: {list(result.sequence)}')

    def feedback_callback(self, feedback_msg):
        """フィードバック受信時に呼ばれるコールバック"""
        partial = feedback_msg.feedback.sequence
        self.get_logger().info(f'フィードバック受信: {list(partial)}')


def main(args=None):
    rclpy.init(args=args)

    node = MinimalActionClient()

    node.send_goal(order=10)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
