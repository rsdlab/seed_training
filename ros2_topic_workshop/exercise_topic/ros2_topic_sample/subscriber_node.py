"""
ROS2 Jazzy - Subscriber 実装課題
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【課題】
  /chatter トピックから std_msgs/String 型のメッセージを
  受信して、内容をログに表示する Subscriber ノードを
  完成させてください。

【完成したときの動作】
  talker を起動した状態で listener を起動すると:
  [INFO] 受信 [1件目]: "こんにちは、ROS2! カウント: 3"
  [INFO] 受信 [2件目]: "こんにちは、ROS2! カウント: 4"
  ...

【ヒント】
  - rclpy, Node, String のインポートは完成しています
  - (1)〜(4) の TODO を順番に埋めてください
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        # TODO (1): 親クラスの __init__ を呼び出してノード名を設定してください
        #           ノード名は 'minimal_subscriber' にしてください
        # HINT: super().__init__('ノード名')
        # ↓ ここに書く
        pass  # この行は削除してください

        # TODO (2): Subscription を作成してください
        #           メッセージ型    : String
        #           トピック名      : 'chatter'
        #           コールバック関数: self.listener_callback
        #           QoSキュー       : 10
        # HINT: self.subscription = self.create_subscription(型, 'トピック名', コールバック, キューサイズ)
        # ↓ ここに書く

        # ※ 未使用警告を抑制するための代入（変更不要）
        self.subscription

        self.received_count = 0
        self.get_logger().info('Subscriberノードを起動しました。メッセージを待機中...')

    def listener_callback(self, msg: String):
        # TODO (3): 受信カウントをインクリメントしてください
        # ↓ ここに書く

        # TODO (4): 受信したメッセージ内容をログに出力してください
        #           例: 受信 [1件目]: "こんにちは、ROS2! カウント: 0"
        # HINT: self.get_logger().info(f'受信 [{self.received_count}件目]: "{msg.data}"')
        # ↓ ここに書く


def main(args=None):
    rclpy.init(args=args)

    node = MinimalSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Ctrl+C で終了します')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
