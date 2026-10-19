"""
ROS2 Jazzy - Publisher 実装課題
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【課題】
  /chatter トピックへ std_msgs/String 型のメッセージを
  0.5秒ごとに配信する Publisher ノードを完成させてください。

【完成したときの動作】
  [INFO] 配信: "こんにちは、ROS2! カウント: 0"
  [INFO] 配信: "こんにちは、ROS2! カウント: 1"
  [INFO] 配信: "こんにちは、ROS2! カウント: 2"
  ...

【ヒント】
  - rclpy, Node, String のインポートは完成しています
  - (1)〜(6) の TODO を順番に埋めてください
  - わからない箇所は HINT を読んでください
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        # TODO (1): 親クラスの __init__ を呼び出してノード名を設定してください
        #           ノード名は 'minimal_publisher' にしてください
        # HINT: super().__init__('ノード名')
        # ↓ ここに書く
        pass  # この行は削除してください

        # TODO (2): Publisher を作成してください
        #           メッセージ型: String
        #           トピック名  : 'chatter'
        #           QoSキュー   : 10
        # HINT: self.publisher_ = self.create_publisher(型, 'トピック名', キューサイズ)
        # ↓ ここに書く

        # TODO (3): 0.5秒ごとに timer_callback を呼ぶタイマーを作成してください
        # HINT: self.timer = self.create_timer(周期秒, コールバック関数)
        timer_period = 0.5  # seconds
        # ↓ ここに書く

        self.count = 0
        self.get_logger().info('Publisherノードを起動しました')

    def timer_callback(self):
        # TODO (4): String 型のメッセージオブジェクトを作成してください
        # HINT: msg = メッセージ型()
        # ↓ ここに書く

        # TODO (5): メッセージの data フィールドに文字列をセットしてください
        #           例: 'こんにちは、ROS2! カウント: 0'  (countを使うこと)
        # HINT: msg.data = f'...'
        # ↓ ここに書く

        # TODO (6): メッセージを配信し、ログに内容を出力してください
        # HINT: self.publisher_.publish(msg)
        #       self.get_logger().info(...)
        # ↓ ここに書く

        self.count += 1


def main(args=None):
    rclpy.init(args=args)

    node = MinimalPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Ctrl+C で終了します')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
