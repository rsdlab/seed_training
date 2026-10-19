"""
ROS2 Jazzy - Service Client 実装課題
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【課題】
  add_two_ints サービスに a=3, b=5 のリクエストを送り
  結果 (sum) を受け取って表示する Client を完成させてください。

【完成したときの動作（Clientのログ）】
  [INFO] Clientノードを起動しました
  [INFO] 結果受信: 3 + 5 = 8

【ヒント】
  - (1)〜(5) の TODO を順番に埋めてください
  - Topic と違い、Service は「1回送って1回受け取る」通信です
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalClient(Node):

    def __init__(self):
        # TODO (1): 親クラスの __init__ を呼び出してノード名を設定してください
        #           ノード名は 'minimal_client' にしてください
        # ↓ ここに書く
        pass  # この行は削除してください

        # TODO (2): Serviceクライアントを作成してください
        #           サービス型 : AddTwoInts
        #           サービス名 : 'add_two_ints'
        # HINT: self.client = self.create_client(型, 'サービス名')
        # ↓ ここに書く

        # サーバーが起動するまで待機（変更不要）
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('サーバーを待機中...')

        self.get_logger().info('Clientノードを起動しました')

    def send_request(self, a: int, b: int):
        """リクエストを送信して結果を返す"""
        # TODO (3): リクエストオブジェクトを作成し a, b をセットしてください
        # ↓ ここに書く

        # TODO (4): 非同期でリクエストを送信してください
        # HINT: call_async(request)
        # ↓ ここに書く

        # レスポンスが返るまで待機（変更不要）
        rclpy.spin_until_future_complete(self, future)

        # TODO (5): 結果を return してください
        # ↓ ここに書く


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
