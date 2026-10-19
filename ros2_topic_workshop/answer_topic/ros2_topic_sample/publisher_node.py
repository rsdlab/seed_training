"""
ROS2 Jazzy - Publisherサンプル
std_msgs/String 型のメッセージを /chatter トピックへ配信します
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')

        # Publisherの作成
        # 引数: メッセージ型, トピック名, QoS (キューサイズ)
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # 0.5秒ごとにタイマーコールバックを呼び出す
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.count = 0
        self.get_logger().info('Publisherノードを起動しました')

    def timer_callback(self):
        msg = String()
        msg.data = f'こんにちは、ROS2! カウント: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'配信: "{msg.data}"')
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
