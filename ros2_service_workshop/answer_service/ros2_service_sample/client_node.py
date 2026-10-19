"""
ROS2 Jazzy - Service Client サンプル
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service型    : example_interfaces/srv/AddTwoInts
サービス名   : add_two_ints
動作         : a=3, b=5 を Server に送り、結果 (sum=8) を受け取って表示する
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalClient(Node):

    def __init__(self):
        super().__init__('minimal_client')

        # Serviceクライアントの作成
        # 引数: サービス型, サービス名
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

        # サーバーが起動するまで待機（1秒タイムアウトで繰り返す）
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('サーバーを待機中...')

        self.get_logger().info('Clientノードを起動しました')

    def send_request(self, a: int, b: int):
        """リクエストを送信して結果を返す（同期的に待機）"""
        # リクエストオブジェクトの作成とフィールドへの代入
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        # 非同期でリクエストを送信し、Futureオブジェクトを取得
        future = self.client.call_async(request)

        # レスポンスが返るまでスピン（イベントループを回す）
        rclpy.spin_until_future_complete(self, future)

        return future.result()


def main(args=None):
    rclpy.init(args=args)

    node = MinimalClient()

    # a=3, b=5 のリクエストを送信
    a, b = 3, 5
    result = node.send_request(a, b)

    node.get_logger().info(
        f'結果受信: {a} + {b} = {result.sum}'
    )

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
