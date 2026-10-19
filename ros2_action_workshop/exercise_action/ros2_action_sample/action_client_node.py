"""
ROS2 Jazzy - Action Client 実装課題
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【課題】
  fibonacci アクションに order=10 のゴールを送り、
  フィードバック（途中経過）を受け取りながら
  最終結果を表示する Action Client を完成させてください。

【完成したときの動作（Clientのログ）】
  [INFO] Action Clientノードを起動しました
  [INFO] Goal送信: order=10
  [INFO] Goalが受理されました。結果を待機中...
  [INFO] フィードバック受信: [0, 1, 1]
  [INFO] フィードバック受信: [0, 1, 1, 2]
  ...
  [INFO] Result受信: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

【ヒント】
  - (1)〜(7) の TODO を順番に埋めてください
  - Client の流れ:
      ① ゴール送信 → ② ゴール受理を確認 → ③ 結果を待機 → ④ 結果取得
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from example_interfaces.action import Fibonacci


class MinimalActionClient(Node):

    def __init__(self):
        # TODO (1): 親クラスの __init__ を呼び出してノード名を設定してください
        #           ノード名は 'minimal_action_client' にしてください
        # ↓ ここに書く
        pass  # この行は削除してください

        # TODO (2): Action Client を作成してください
        #           アクション型 : Fibonacci
        #           アクション名 : 'fibonacci'
        # HINT: self._action_client = ActionClient(self, 型, 'アクション名')
        # ↓ ここに書く

        self.get_logger().info('Action Clientノードを起動しました')

    def send_goal(self, order: int):
        """ゴールを送信し、フィードバックを受け取りながら結果を待つ"""

        # サーバーが起動するまで待機（変更不要）
        self.get_logger().info('Action Serverを待機中...')
        self._action_client.wait_for_server()

        # TODO (3): ゴールメッセージを作成し order をセットしてください
        # HINT: goal_msg = Fibonacci.Goal()
        #       goal_msg.order = order
        # ↓ ここに書く

        self.get_logger().info(f'Goal送信: order={order}')

        # TODO (4): ゴールを非同期で送信してください
        #           フィードバックコールバックとして self.feedback_callback を登録してください
        # HINT: send_goal_future = self._action_client.send_goal_async(
        #           goal_msg,
        #           feedback_callback=self.feedback_callback
        #       )
        # ↓ ここに書く

        # ゴール受理の応答を待つ（変更不要）
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle: ClientGoalHandle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goalが拒否されました')
            return

        self.get_logger().info('Goalが受理されました。結果を待機中...')

        # TODO (5): 最終結果を非同期で取得してください
        # HINT: result_future = goal_handle.get_result_async()
        # ↓ ここに書く

        # 結果が返るまで待機（変更不要）
        rclpy.spin_until_future_complete(self, result_future)

        # TODO (6): result_future から結果を取り出してログに出力してください
        # HINT: result = result_future.result().result
        #       self.get_logger().info(f'Result受信: {list(result.sequence)}')
        # ↓ ここに書く

    def feedback_callback(self, feedback_msg):
        """フィードバック受信時に呼ばれるコールバック"""
        # TODO (7): フィードバックの sequence をログに出力してください
        # HINT: partial = feedback_msg.feedback.sequence
        #       self.get_logger().info(f'フィードバック受信: {list(partial)}')
        # ↓ ここに書く


def main(args=None):
    rclpy.init(args=args)

    node = MinimalActionClient()

    node.send_goal(order=10)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
