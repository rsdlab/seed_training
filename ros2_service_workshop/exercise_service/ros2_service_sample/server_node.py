"""
ROS2 Jazzy - Service Server 実装課題
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【課題】
  クライアントから受け取った2つの整数 a, b を足し算して
  結果 (sum) を返す Service Server を完成させてください。

【使用するサービス型】
  example_interfaces/srv/AddTwoInts
    Request  : int64 a, int64 b
    Response : int64 sum

【完成したときの動作（Serverのログ）】
  [INFO] Serverノードを起動しました。リクエストを待機中...
  [INFO] リクエスト受信: a=3, b=5 → sum=8

【ヒント】
  - (1)〜(4) の TODO を順番に埋めてください
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalServer(Node):

    def __init__(self):
        # TODO (1): 親クラスの __init__ を呼び出してノード名を設定してください
        #           ノード名は 'minimal_server' にしてください
        # HINT: super().__init__('ノード名')
        # ↓ ここに書く
        pass  # この行は削除してください

        # TODO (2): Serviceサーバーを作成してください
        #           サービス型    : AddTwoInts
        #           サービス名    : 'add_two_ints'
        #           コールバック  : self.add_two_ints_callback
        # HINT: self.srv = self.create_service(型, 'サービス名', コールバック)
        # ↓ ここに書く

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
        # TODO (3): response.sum に a + b の計算結果をセットしてください
        # HINT: response.sum = request.a + request.b
        # ↓ ここに書く

        self.get_logger().info(
            f'リクエスト受信: a={request.a}, b={request.b} → sum={response.sum}'
        )

        # TODO (4): response を return してください
        # ↓ ここに書く


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
