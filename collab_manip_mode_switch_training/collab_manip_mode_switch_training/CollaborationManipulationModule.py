#!/usr/bin/env python3
# coding: UTF-8
# 研修（自律動作中 ⇄ 非自律動作中）: このファイルの TODO-6 を埋めてください.

#####################################################################################################################
#このノードは．人協働マニピュレーションモジュールを機能単位で作成したモジュールです．　
#ハンド部分のモジュールと人検知部分の追加を行っています．　　　　　　　　　　　　　　 #
#===================================================================================================================#
#バージョン管理
#===================================================================================================================#
#ver. 0.1:  基本実装（Linux版）　　　2023/11/07
#08/30 排出位置検出システム編集
#09/21 排出位置検出システム　統合
#09/28 WS環境認識システム作成
#10/05 排出位置検出システム　統合確認　
#2026/10/13 研修用（自律動作中 ⇄ 非自律動作中）に collaboration_manipulation_module からコピー
#===================================================================================================================#
#依存ノード
#===================================================================================================================#
#このノードはLinuxでのみ利用可能です．
#===================================================================================================================#

import sys

from .CollaborationCommunicationModule import (
    GetStatusServer,
    NotifyTaskCompleteClient,
    NotifyTaskResultClient,
    PauseTaskServer,
    PeripheralEnvironmentAreaSetClient,
    PlacePositionClient,
    ResumeTaskServer,
    ServiceServerExecutor,
    StartManipulationTaskServer,
    StopManipulationTaskServer,
    SystemTerminate,
    TaskCancelServer,
    TaskCommandServer,
    TaskFinishServer,
    WorkDetectionClient,
)
from .CollaborationEventModule import (
    CollaborationEventPublisher,
    CollaborationEventSubscriverWorkStart,
)
from .CollaborationStateModule import HumanCollaborationStateMachine
from .CollaborationToolModule import CollaborationTool
from .CollaborationUserDefineModule import ShareMovePlanner


##################################################################
#　　　　　　　　　　　 クラス定義　                            #
##################################################################
class HumanCollaboration:
    def __init__(self):
        area = PeripheralEnvironmentAreaSetClient()
        disc = PlacePositionClient()
        workd = WorkDetectionClient()
        workstart_event = CollaborationEventSubscriverWorkStart()
        self.recv_cmd = TaskCommandServer()
        self.sys_teminate = SystemTerminate()
        self.task_cancel = TaskCancelServer()
        self.task_finish = TaskFinishServer()
        self.get_status = GetStatusServer()
        #作業の一時停止/一時停止解除（完成品）.
        self.pause_task = PauseTaskServer()
        self.resume_task = ResumeTaskServer()
        # === TODO-6 (1) =====================================================
        # 協働作業開始/終了を受け付けるサーバ（TODO-2, TODO-3 で書いたクラス）を
        # 作成してください.
        #   self.start_manip <- StartManipulationTaskServer
        #   self.stop_manip  <- StopManipulationTaskServer
        #
        # ヒント： 上の self.get_status = GetStatusServer() と同じ書き方です.
        # ====================================================================
        # ここから

        # ここまで
        self.statemachine = HumanCollaborationStateMachine(
              NotifyTaskResultClient(),
              NotifyTaskCompleteClient(),
              self.task_cancel,
              self.task_finish,
              self.get_status,
              area,
              disc,
              workd,
              workstart_event
              )
        CollaborationEventPublisher.register(self.statemachine)
        CollaborationEventPublisher.register(workstart_event)

        # サブスレッドにサービスサーバーを渡す.
        self.executor = ServiceServerExecutor()
        self.executor.add_service_server(self.recv_cmd)
        self.executor.add_service_server(self.sys_teminate)
        self.executor.add_service_server(self.task_cancel)
        self.executor.add_service_server(self.task_finish)
        self.executor.add_service_server(self.get_status)
        self.executor.add_service_server(self.pause_task)
        self.executor.add_service_server(self.resume_task)
        # === TODO-6 (2) =====================================================
        # 作成したサーバを executor に登録してください.
        # 登録しないと spin されず、サービスを呼んでも応答しません.
        #
        # ヒント： 上の行と同じく self.executor.add_service_server(____)
        # ====================================================================
        # ここから

        # ここまで

        # MonitorState（人検知 /intrusion_result）のノードを
        # executor に追加して spin させる. これがないと購読コールバックが呼ばれず、
        # 人検知などのトピック監視が機能しない.
        for monitor_node in self.statemachine.monitor_nodes:
            self.executor.add_service_server(monitor_node)

    def execute(self):
        # サブスレッドでサービスサーバをspinする.
        self.executor.execute()

        # 状態遷移を開始.
        try:
            CollaborationTool.loginfo('State machine Start')
            self.statemachine.execute()
            CollaborationTool.loginfo(' State machine End')
        
        except KeyboardInterrupt:
            print('shutdown')

        finally:
            # マルチスレッドノードを破棄.
            self.executor.shutdown()
            CollaborationTool.signal_shutdown("sys_manage_halt")

def main():
    # --dummy を付けて起動すると、ロボット(MoveIt)なしで状態遷移だけを確認できる.
    #   ros2 run collab_manip_mode_switch_training CollaborationManipulationModule --dummy
    ShareMovePlanner.use_dummy = '--dummy' in sys.argv
    CollaborationTool.ros_init()
    hc = HumanCollaboration()
 
    #実行
    hc.execute()
##################################################################
#　　　　　　　　　　　 以下実行処理内容                         #
##################################################################   
if __name__ == '__main__':
    main()
 
