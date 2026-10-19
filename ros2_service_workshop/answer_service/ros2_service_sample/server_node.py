"""
ROS2 Jazzy - Service Server サンプル
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service型    : example_interfaces/srv/AddTwoInts
サービス名   : add_two_ints
動作         : クライアントから受け取った2つの整数を足して返す
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalServer(Node):

    def __init__(self):
        super().__init__('minimal_server')

        # Serviceサーバーの作成
        # 引数: サービス型, サービス名, コールバック関数
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )

        self.get_logger().info(
            'Serverノードを起動しました。リクエストを待機中...'
        )

    def add_two_ints_callback(self, request, response):
        """
        リクエストを受信したときに呼ばれるコールバック関数

        Args:
            request  (AddTwoInts.Request) : クライアントからのリクエスト
                                            request.a, request.b に整数が入っている
            response (AddTwoInts.Response): クライアントへ返すレスポンス
                                            response.sum に計算結果をセットして返す
        """
        response.sum = request.a + request.b

        self.get_logger().info(
            f'リクエスト受信: a={request.a}, b={request.b} → sum={response.sum}'
        )

        return response


def main(args=None):
    rclpy.init(args=args)

    node = MinimalServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Ctrl+C で終了します')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
