"""
ROS2 Jazzy - Subscriberサンプル
/chatter トピックから std_msgs/String 型のメッセージを受信します
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')

        # Subscriberの作成
        # 引数: メッセージ型, トピック名, コールバック関数, QoS (キューサイズ)
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )
        # 未使用警告を抑制するための代入
        self.subscription

        self.received_count = 0
        self.get_logger().info('Subscriberノードを起動しました。メッセージを待機中...')

    def listener_callback(self, msg: String):
        self.received_count += 1
        self.get_logger().info(
            f'受信 [{self.received_count}件目]: "{msg.data}"'
        )


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
