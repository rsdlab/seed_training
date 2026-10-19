#!/usr/bin/env python3
# coding: UTF-8
# 研修（自律動作中 ⇄ 非自律動作中）: このファイルの TODO-5 を埋めてください.

from geometry_msgs.msg import TransformStamped
from std_msgs.msg import String

from .CollaborationCommunicationModule import *
from .CollaborationStateHeader import CollaborationCurrentData, CollaborationState
from .CollaborationToolModule import CollaborationTool
from .MovePlannerModule import DummyMovePlanner, MovePlanner
from .TransitionModule import Transition

#定数の定義
DEFAULT_VELOCITY = 1.0
RETRY_COUNT_MAX = 3
PREPAR_WAIT = 3
PAUSED_WAIT = 0.1
PAUSED_LOG_INTERVAL = 3.0
#非自律動作中(協働作業中)の速度制限. 自律動作の何倍の速度・加速度で動くか.
NON_OPERATING_VELOCITY_SCALE = 0.3

PICK_COMMAND = 0
DOWN_COMMAND = 1
PLACE_COMMAND = 2
RELEASE_COMMAND = 3
SOLVE_COMMAND = 4
APPROACH_COMMAND = 5
INIT_COMMAND = 6
# upper_body: 20 joints (waist×3, l_shoulder×3, l_elbow, l_wrist×3, neck×3, r_shoulder×3, r_elbow, r_wrist×3)
READY_APPROACH_VAL_01 = 0.0
READY_APPROACH_VAL_02 = 0.0
READY_APPROACH_VAL_03 = 0.0
READY_APPROACH_VAL_04 = -52.0
READY_APPROACH_VAL_05 = 12.0
READY_APPROACH_VAL_06 = -4.0
READY_APPROACH_VAL_07 = -70.0
READY_APPROACH_VAL_08 = 0.0
READY_APPROACH_VAL_09 = 0.0
READY_APPROACH_VAL_10 = 0.0
READY_APPROACH_VAL_11 = 0.0
READY_APPROACH_VAL_12 = 0.0
READY_APPROACH_VAL_13 = 0.0
READY_APPROACH_VAL_14 = -52.0
READY_APPROACH_VAL_15 = -12.0
READY_APPROACH_VAL_16 = 4.0
READY_APPROACH_VAL_17 = -70.0
READY_APPROACH_VAL_18 = 0.0
READY_APPROACH_VAL_19 = 0.0
READY_APPROACH_VAL_20 = 0.0
READY_APPROACH_VEL = 1.0
APPROACH_VAL_01 = 0.0
APPROACH_VAL_02 = 0.0
APPROACH_VAL_03 = 0.0
APPROACH_VAL_04 = -43.0
APPROACH_VAL_05 = 24.0
APPROACH_VAL_06 = -17.0
APPROACH_VAL_07 = -60.0
APPROACH_VAL_08 = 30.0
APPROACH_VAL_09 = 2.0
APPROACH_VAL_10 = -5.0
APPROACH_VAL_11 = 0.0
APPROACH_VAL_12 = 0.0
APPROACH_VAL_13 = 0.0
APPROACH_VAL_14 = -46.0
APPROACH_VAL_15 = -12.0
APPROACH_VAL_16 = 2.0
APPROACH_VAL_17 = -51.0
APPROACH_VAL_18 = -12.0
APPROACH_VAL_19 = -3.0
APPROACH_VAL_20 = 16.0
APPROACH_VEL = 1.0
PICK_VAL_01 = 0.0
PICK_VAL_02 = 0.0
PICK_VAL_03 = 0.0
PICK_VAL_04 = -46.0
PICK_VAL_05 = 17.0
PICK_VAL_06 = -28.0
PICK_VAL_07 = -61.0
PICK_VAL_08 = 26.0
PICK_VAL_09 = 4.0
PICK_VAL_10 = -0.0
PICK_VAL_11 = 0.0
PICK_VAL_12 = 0.0
PICK_VAL_13 = 0.0
PICK_VAL_14 = -44.0
PICK_VAL_15 = -6.0
PICK_VAL_16 = 5.0
PICK_VAL_17 = -57.0
PICK_VAL_18 = -5.0
PICK_VAL_19 = -2.0
PICK_VAL_20 = 16.0
PICK_VEL = 1.0
UP_VAL_01 = 0.0
UP_VAL_02 = 0.0
UP_VAL_03 = 0.0
UP_VAL_04 = -46.0
UP_VAL_05 = 17.0
UP_VAL_06 = -28.0
UP_VAL_07 = -66.0
UP_VAL_08 = 26.0
UP_VAL_09 = 4.0
UP_VAL_10 = -0.0
UP_VAL_11 = 0.0
UP_VAL_12 = 0.0
UP_VAL_13 = 0.0
UP_VAL_14 = -44.0
UP_VAL_15 = -6.0
UP_VAL_16 = 5.0
UP_VAL_17 = -60.0
UP_VAL_18 = -5.0
UP_VAL_19 = -2.0
UP_VAL_20 = 16.0
UP_VEL = 1.0
# lifter: 2 joints (ankle_joint, knee_joint)
DOWN_LIFTER_VAL_01 = 55.0
DOWN_LIFTER_VAL_02 = -55.0
DOWN_LIFTER_VEL = 1.0
SET_LIFTER_VAL_01 = 63.0
SET_LIFTER_VAL_02 = -63.0
SET_LIFTER_VEL = 0.1

TEST_VAL_01 = 0.0
TEST_VAL_02 = -9.15112
TEST_VAL_03 = 0.0
TEST_VAL_04 = -46.86233
TEST_VAL_05 = 2.74952
TEST_VAL_06 = -0.95000
TEST_VAL_07 = -37.39286
TEST_VAL_08 = -1.69000
TEST_VAL_09 = 1.38875
TEST_VAL_10 = -9.68590
TEST_VAL_11 = 0.0
TEST_VAL_12 = 0.0
TEST_VAL_13 = 0.0
TEST_VAL_14 = 0.0
TEST_VAL_15 = 0.0
TEST_VAL_16 = -2.0
TEST_VAL_17 = 0.0
TEST_VAL_18 = 0.0
TEST_VAL_19 = 0.0
TEST_VAL_20 = 0.0
TEST_VAL_VEL = 1.0

###########################################
#MovePlanner共有クラス.                   #
###########################################
class ShareMovePlanner:
    move_plannner = None
    #True のときはロボット(MoveIt)を使わず、DummyMovePlanner で動作を模擬する.
    use_dummy = False
    @classmethod
    def get_move_planner(cls):
        if cls.move_plannner is None:
            cls.move_plannner = DummyMovePlanner() if cls.use_dummy else MovePlanner()
        return cls.move_plannner
    
###########################################
#初期処理クラス.                          #
###########################################
class INITIALISE(CollaborationState):
    def __init__(self,
                 label,
                 taskfin:TaskFinishServer,
                 tran:Transition,
                 outcomes):
        super().__init__(label, tran, outcomes)
        self.planner = ShareMovePlanner.get_move_planner()
        self.taskfin = taskfin
        self.counter = 0

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        
        if self.tran.get_event().is_workend():
            task_command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = task_command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        
        if self.preempt('INIITIALISE is being preempted!!!'):
            return 'preempted'
        
        #初期処理を行う.
        return self.initialise()

    def initialise(self):
        ###ロボットごとの初期動作.
        #ここから.

        while not CollaborationTool.is_shutdown():
          #初期位置移動.
          ret = self.init_pose_upper_body()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret
        
        while not CollaborationTool.is_shutdown():
          #初期位置移動.
          ret = self.init_pose_lifter()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret

        #ここまで.
        return 'succeeded'

    #初期位置移動.
    def init_pose_upper_body(self):
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('Initialise')
            rc = self.planner.initial_pose_upper_body()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'
        
    def init_pose_lifter(self):
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('Initialise')
            rc = self.planner.initial_pose_lifter()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

###########################################
#スタート前処理クラス.                    #
###########################################
class BEFORE_START(CollaborationState):
    def __init__(self, label, taskfin:TaskFinishServer, tran:Transition, outcomes):
        super().__init__(label, tran, outcomes)
        self.taskfin = taskfin

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        if self.tran.get_event().is_pause():
            CollaborationState.set_history_label(self.label)
            self.tran.set_history_state(self.tran.get_state())

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        
        CollaborationTool.loginfo('Before Start ...')
        if self.preempt('State BEFORE_START is being preempted!!!'):
            return 'preempted'
      
        return self.before_start()

    def before_start(self):
        ###ロボットごとのスタート前動作.
        #ここから.

        #ここまで.
        return 'succeeded'

###########################################
#準備中処理クラス.                        #
###########################################
class PREPAR_WORK(CollaborationState):
    def __init__(self, label, taskfin:TaskFinishServer, tran:Transition, area, disc, workd, outcomes):
        super().__init__(label, tran, outcomes)
        self.taskfin = taskfin
        self.area = area
        self.disc = disc
        self.workd = workd

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)

        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
      
        CollaborationTool.loginfo('Preparing ...')
        if self.preempt('State Prepar is being preempted!!!'):
            return 'preempted'
        
        #準備処理.
        return self.prepar()

    def prepar(self):
        ###ロボットごとの準備動作.
        #ここから.

        self.counter = 0

        #周辺環境範囲設定.
        while not CollaborationTool.is_shutdown():
            ret = self.PeripheralEnvironmentAreaSet()
            if 'succeeded' == ret:
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
          
        #ワーク検知.
        while not CollaborationTool.is_shutdown():
            ret = self.WorkDetect()
            if 'succeeded' == ret:
                    break
            elif 'retry' == ret:
                continue
            else:
                return ret
          
        #排出位置検出.
        while not CollaborationTool.is_shutdown():
            ret = self.PlaceDetect()
            if 'succeeded' == ret:
                    break
            elif 'retry' == ret:
             continue
            else:
                return ret
        
        #ここまで.
        return 'succeeded'
    
    #周辺環境範囲を設定する.
    def PeripheralEnvironmentAreaSet(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event

        return 'succeeded'

    #排出位置を検出する.
    def PlaceDetect(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event

        CollaborationTool.loginfo("waiting place_position")
        self.disc.wait_for_service()
        CollaborationTool.loginfo("place_position comes up")

        event = self.check_event()
        if(None != event ):
            return event
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State PlaceDetect is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            #排出位置を探索.
            self.set_place_area()
            rc = self.disc.execute(None)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc) 
        else:
            return 'aborted'

    #ワークを検知する.
    def WorkDetect(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event

        CollaborationTool.loginfo("waiting work_det_service")
        self.workd.wait_for_service()
        CollaborationTool.loginfo("work_det_service comes up")

        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State Work Detect is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            #ワーク検知範囲の設定.
            self.set_presence_area()
            rc = self.workd.execute(None)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc) 
        else:
            return 'aborted'

    #排出位置を設定する.
    def set_place_area(self):
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        task_command = command_list.get(0)
        place_area_list = task_command.get_PlaceLocationAreaList()
        print(place_area_list)
        place_area = place_area_list[0]
        print(place_area)
        self.disc.set_place_area(place_area.start_point.x,
                                     place_area.start_point.y,
                                     place_area.start_point.z,
                                     place_area.end_point.x,
                                     place_area.end_point.y,
                                     place_area.end_point.z,)

    #ワーク検知範囲を設定する.
    def set_presence_area(self):
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        task_command = command_list.get(0)
        presence_area = task_command.work_presence_area
        self.workd.set_presence_area(task_command.task_command_id,
                                     task_command.work_type_id,
                                     presence_area.start_point.x,
                                     presence_area.start_point.y,
                                     presence_area.start_point.z,
                                     presence_area.end_point.x,
                                     presence_area.end_point.y,
                                     presence_area.end_point.z,)
    
    #作業途中で状態遷移するイベントの確認.
    def check_event(self):
        if self.tran.get_event().is_pause():
            CollaborationState.set_history_label(self.label)
            self.tran.set_history_state(self.tran.get_state())

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        return None
        
###########################################
#自律動作処理クラス.                      #
###########################################
class OPERATING_WORK(CollaborationState):
    #どの動作まで終わったか. 自律動作中と非自律動作中で共有し、切り替えても続きから動く.
    _shared_work_label = None

    @property
    def work_label(self):
        return OPERATING_WORK._shared_work_label

    @work_label.setter
    def work_label(self, label):
        OPERATING_WORK._shared_work_label = label

    def __init__(self,
                 label,
                 taskfin:TaskFinishServer,
                 tran:Transition,
                 outcomes):
        super().__init__(label, tran, outcomes)
        self.planner = ShareMovePlanner.get_move_planner()
        self.taskfin = taskfin
        self.counter = 0
        self.work_label = None

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        CollaborationTool.loginfo('========== 自律動作中 (Operating) ==========')
        CollaborationTool.loginfo(command_list.get(0).task_command_id)
        
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
        
        #自律動作.
        return self.operating_work()

    #自律動作処理.
    def operating_work(self):
        ###ロボットごとの自律動作.
        #ここから.

        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        command_id = command_list.get(0).task_command_id

        ret = ''
        if(PICK_COMMAND == command_id):
            ret = self.pick_move()
        elif(DOWN_COMMAND == command_id):
            ret = self.down_move()
        elif(PLACE_COMMAND == command_id):
            ret = self.place_move()
        elif(RELEASE_COMMAND == command_id):
            ret = self.release_move()
        elif(SOLVE_COMMAND == command_id):
            ret = self.solve_move()
        elif(APPROACH_COMMAND == command_id):
            ret = self.approach_move()
        elif(INIT_COMMAND == command_id):
            ret = self.init_move()

        #ここまで.
        #自律⇄非自律の切り替え/一時停止で抜けるときは work_label を残し、次の状態で続きの動作から再開する.
        if ret not in ('collabo', 'collaboend', 'paused'):
            self.work_label = None
        #イベント遷移(paused等)はそのまま返す. 未知の値を'succeeded'にすると未完了でも作業結果Trueが送られるため'aborted'にする.
        return ret if ret in self.get_registered_outcomes() else 'aborted'
    
    def pick_move(self):
        #上半身の初期位置1.
        if (None == self.work_label) or ('UpperInit' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'UpperInit'
                ret = self.init_pose_upper_body()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret
        
        #リフターの初期位置.
        if (None == self.work_label) or ('CurrentManip' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'CurrentManip'
                ret = self.init_pose_lifter()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret
        
        #アプローチ準備位置.
        if (None == self.work_label) or ('ReadyApproach' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'ReadyApproach'
                ret = self.joint_manip_upper(READY_APPROACH_VAL_01, READY_APPROACH_VAL_02, READY_APPROACH_VAL_03, READY_APPROACH_VAL_04, READY_APPROACH_VAL_05,
                                             READY_APPROACH_VAL_06, READY_APPROACH_VAL_07, READY_APPROACH_VAL_08, READY_APPROACH_VAL_09, READY_APPROACH_VAL_10,
                                             READY_APPROACH_VAL_11, READY_APPROACH_VAL_12, READY_APPROACH_VAL_13, READY_APPROACH_VAL_14, READY_APPROACH_VAL_15,
                                             READY_APPROACH_VAL_16, READY_APPROACH_VAL_17, READY_APPROACH_VAL_18, READY_APPROACH_VAL_19, READY_APPROACH_VAL_20,
                                             READY_APPROACH_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #アプローチ位置.
        if (None == self.work_label) or ('Approach' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Approach'
                ret = self.joint_manip_upper(APPROACH_VAL_01, APPROACH_VAL_02, APPROACH_VAL_03, APPROACH_VAL_04, APPROACH_VAL_05,
                                             APPROACH_VAL_06, APPROACH_VAL_07, APPROACH_VAL_08, APPROACH_VAL_09, APPROACH_VAL_10,
                                             APPROACH_VAL_11, APPROACH_VAL_12, APPROACH_VAL_13, APPROACH_VAL_14, APPROACH_VAL_15,
                                             APPROACH_VAL_16, APPROACH_VAL_17, APPROACH_VAL_18, APPROACH_VAL_19, APPROACH_VAL_20,
                                             APPROACH_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #つかみ位置.
        if (None == self.work_label) or ('Pick' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Pick'
                ret = self.joint_manip_upper(PICK_VAL_01, PICK_VAL_02, PICK_VAL_03, PICK_VAL_04, PICK_VAL_05,
                                             PICK_VAL_06, PICK_VAL_07, PICK_VAL_08, PICK_VAL_09, PICK_VAL_10,
                                             PICK_VAL_11, PICK_VAL_12, PICK_VAL_13, PICK_VAL_14, PICK_VAL_15,
                                             PICK_VAL_16, PICK_VAL_17, PICK_VAL_18, PICK_VAL_19, PICK_VAL_20,
                                             PICK_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #上昇位置.
        if (None == self.work_label) or ('Up' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Up'
                ret = self.joint_manip_upper(UP_VAL_01, UP_VAL_02, UP_VAL_03, UP_VAL_04, UP_VAL_05,
                                             UP_VAL_06, UP_VAL_07, UP_VAL_08, UP_VAL_09, UP_VAL_10,
                                             UP_VAL_11, UP_VAL_12, UP_VAL_13, UP_VAL_14, UP_VAL_15,
                                             UP_VAL_16, UP_VAL_17, UP_VAL_18, UP_VAL_19, UP_VAL_20,
                                             UP_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        self.work_label = None
        return 'succeeded'

    def down_move(self):
        #リフターを下げる.
        if (None == self.work_label) or ('DownLifetr' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'DownLifetr'
                ret = self.joint_manip_lifter(DOWN_LIFTER_VAL_01, DOWN_LIFTER_VAL_02, DOWN_LIFTER_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        self.work_label = None
        return 'succeeded'

    def place_move(self):
        #リフターをセット位置にする.
        if (None == self.work_label) or ('SetLifetr' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'SetLifetr'
                ret = self.joint_manip_lifter(SET_LIFTER_VAL_01, SET_LIFTER_VAL_02, SET_LIFTER_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret
    
        #上昇位置.
        if (None == self.work_label) or ('Place1' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Place1'
                ret = self.joint_manip_upper(UP_VAL_01, UP_VAL_02, UP_VAL_03, UP_VAL_04, UP_VAL_05,
                                             UP_VAL_06, UP_VAL_07, UP_VAL_08, UP_VAL_09, UP_VAL_10,
                                             UP_VAL_11, UP_VAL_12, UP_VAL_13, UP_VAL_14, UP_VAL_15,
                                             UP_VAL_16, UP_VAL_17, UP_VAL_18, UP_VAL_19, UP_VAL_20,
                                             UP_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret
        
        #つかみ位置.
        if (None == self.work_label) or ('Place2' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Place2'
                ret = self.joint_manip_upper(PICK_VAL_01, PICK_VAL_02, PICK_VAL_03, PICK_VAL_04, PICK_VAL_05,
                                             PICK_VAL_06, PICK_VAL_07, PICK_VAL_08, PICK_VAL_09, PICK_VAL_10,
                                             PICK_VAL_11, PICK_VAL_12, PICK_VAL_13, PICK_VAL_14, PICK_VAL_15,
                                             PICK_VAL_16, PICK_VAL_17, PICK_VAL_18, PICK_VAL_19, PICK_VAL_20,
                                             PICK_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret
        
        #リリース位置.
        if (None == self.work_label) or ('Release' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Release'
                ret = self.joint_manip_upper(APPROACH_VAL_01, APPROACH_VAL_02, APPROACH_VAL_03, APPROACH_VAL_04, APPROACH_VAL_05,
                                             APPROACH_VAL_06, APPROACH_VAL_07, APPROACH_VAL_08, APPROACH_VAL_09, APPROACH_VAL_10,
                                             APPROACH_VAL_11, APPROACH_VAL_12, APPROACH_VAL_13, APPROACH_VAL_14, APPROACH_VAL_15,
                                             APPROACH_VAL_16, APPROACH_VAL_17, APPROACH_VAL_18, APPROACH_VAL_19, APPROACH_VAL_20,
                                             APPROACH_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #初期化準備位置.
        if (None == self.work_label) or ('ReadyInit' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'ReadyInit'
                ret = self.joint_manip_upper(READY_APPROACH_VAL_01, READY_APPROACH_VAL_02, READY_APPROACH_VAL_03, READY_APPROACH_VAL_04, READY_APPROACH_VAL_05,
                                             READY_APPROACH_VAL_06, READY_APPROACH_VAL_07, READY_APPROACH_VAL_08, READY_APPROACH_VAL_09, READY_APPROACH_VAL_10,
                                             READY_APPROACH_VAL_11, READY_APPROACH_VAL_12, READY_APPROACH_VAL_13, READY_APPROACH_VAL_14, READY_APPROACH_VAL_15,
                                             READY_APPROACH_VAL_16, READY_APPROACH_VAL_17, READY_APPROACH_VAL_18, READY_APPROACH_VAL_19, READY_APPROACH_VAL_20,
                                             READY_APPROACH_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #上半身の初期位置.
        if (None == self.work_label) or ('UpperInit' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'UpperInit'
                ret = self.init_pose_upper_body()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret
        
        #リフターの初期位置.
        if (None == self.work_label) or ('CurrentManip' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'CurrentManip'
                ret = self.init_pose_lifter()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        self.work_label = None
        return 'succeeded'
    
    def release_move(self):
        #上昇位置.
        if (None == self.work_label) or ('Release1' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Release1'
                ret = self.joint_manip_upper(UP_VAL_01, UP_VAL_02, UP_VAL_03, UP_VAL_04, UP_VAL_05,
                                             UP_VAL_06, UP_VAL_07, UP_VAL_08, UP_VAL_09, UP_VAL_10,
                                             UP_VAL_11, UP_VAL_12, UP_VAL_13, UP_VAL_14, UP_VAL_15,
                                             UP_VAL_16, UP_VAL_17, UP_VAL_18, UP_VAL_19, UP_VAL_20,
                                             UP_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #つかみ位置.
        if (None == self.work_label) or ('Release2' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Release2'
                ret = self.joint_manip_upper(PICK_VAL_01, PICK_VAL_02, PICK_VAL_03, PICK_VAL_04, PICK_VAL_05,
                                             PICK_VAL_06, PICK_VAL_07, PICK_VAL_08, PICK_VAL_09, PICK_VAL_10,
                                             PICK_VAL_11, PICK_VAL_12, PICK_VAL_13, PICK_VAL_14, PICK_VAL_15,
                                             PICK_VAL_16, PICK_VAL_17, PICK_VAL_18, PICK_VAL_19, PICK_VAL_20,
                                             PICK_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #リリース位置.
        if (None == self.work_label) or ('Release3' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Release3'
                ret = self.joint_manip_upper(APPROACH_VAL_01, APPROACH_VAL_02, APPROACH_VAL_03, APPROACH_VAL_04, APPROACH_VAL_05,
                                             APPROACH_VAL_06, APPROACH_VAL_07, APPROACH_VAL_08, APPROACH_VAL_09, APPROACH_VAL_10,
                                             APPROACH_VAL_11, APPROACH_VAL_12, APPROACH_VAL_13, APPROACH_VAL_14, APPROACH_VAL_15,
                                             APPROACH_VAL_16, APPROACH_VAL_17, APPROACH_VAL_18, APPROACH_VAL_19, APPROACH_VAL_20,
                                             APPROACH_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #初期化準備位置.
        if (None == self.work_label) or ('ReadyInit2' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'ReadyInit2'
                ret = self.joint_manip_upper(READY_APPROACH_VAL_01, READY_APPROACH_VAL_02, READY_APPROACH_VAL_03, READY_APPROACH_VAL_04, READY_APPROACH_VAL_05,
                                             READY_APPROACH_VAL_06, READY_APPROACH_VAL_07, READY_APPROACH_VAL_08, READY_APPROACH_VAL_09, READY_APPROACH_VAL_10,
                                             READY_APPROACH_VAL_11, READY_APPROACH_VAL_12, READY_APPROACH_VAL_13, READY_APPROACH_VAL_14, READY_APPROACH_VAL_15,
                                             READY_APPROACH_VAL_16, READY_APPROACH_VAL_17, READY_APPROACH_VAL_18, READY_APPROACH_VAL_19, READY_APPROACH_VAL_20,
                                             READY_APPROACH_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #上半身の初期位置.
        if (None == self.work_label) or ('UpperInit2' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'UpperInit2'
                ret = self.init_pose_upper_body()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret
        
        #リフターの初期位置.
        if (None == self.work_label) or ('InitManip2' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'InitManip2'
                ret = self.init_pose_lifter()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        self.work_label = None
        return 'succeeded'

    #初期姿勢に戻る（上半身 -> リフター）.
    def init_move(self):
        #上半身の初期位置.
        if (None == self.work_label) or ('InitUpper' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'InitUpper'
                ret = self.init_pose_upper_body()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        #リフターの初期位置.
        if (None == self.work_label) or ('InitLifter' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'InitLifter'
                ret = self.init_pose_lifter()
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        self.work_label = None
        return 'succeeded'

    def solve_move(self):
        return self.pick_move()

    def approach_move(self):
        if (None == self.work_label) or ('Approach' == self.work_label):
            while not CollaborationTool.is_shutdown():
                self.work_label = 'Approach'
                ret = self.joint_manip_upper(TEST_VAL_01, TEST_VAL_02, TEST_VAL_03, TEST_VAL_04, TEST_VAL_05,
                                             TEST_VAL_06, TEST_VAL_07, TEST_VAL_08, TEST_VAL_09, TEST_VAL_10,
                                             TEST_VAL_11, TEST_VAL_12, TEST_VAL_13, TEST_VAL_14, TEST_VAL_15,
                                             TEST_VAL_16, TEST_VAL_17, TEST_VAL_18, TEST_VAL_19, TEST_VAL_20,
                                             TEST_VAL_VEL)
                if 'succeeded' == ret:
                    self.work_label = None
                    break
                elif 'retry' == ret:
                    continue
                else:
                    return ret

        self.work_label = None
        return 'succeeded'

    #初期位置移動.
    def init_pose_upper_body(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event

        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('Initialise')
            rc = self.planner.initial_pose_upper_body()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'
        
    def init_pose_lifter(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('Initialise')
            rc = self.planner.initial_pose_lifter()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'
        
    def joint_manip_upper(self, val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8, val_9, val_10,
                                          val_11, val_12, val_13, val_14, val_15, val_16, val_17, val_18, val_19, val_20, vel):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event

        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State NORMAL_MANIP is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            rc = self.planner.joint_value_upper_body(val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8, val_9, val_10,
                                          val_11, val_12, val_13, val_14, val_15, val_16, val_17, val_18, val_19, val_20, vel)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    def joint_manip_lifter(self, val_1, val_2, vel):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event

        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State NORMAL_MANIP is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            rc = self.planner.joint_value_lifter(val_1, val_2, vel)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    #作業途中で状態遷移するイベントの確認.
    def check_event(self):
        if self.tran.get_event().is_pause():
            CollaborationState.set_history_label(self.label)
            self.tran.set_history_state(self.tran.get_state())

        elif self.tran.get_event().is_workend():
            command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        return None


###########################################
#非自律動作処理クラス.                    #
###########################################
class NON_OPERATING_WORK(OPERATING_WORK):
    #自律動作(OPERATING_WORK)と同じ動作の並びと進み具合(work_label)を使い、速度だけを制限する.
    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        CollaborationTool.loginfo('========== 非自律動作中 (NonOperating) ==========')
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        CollaborationTool.loginfo(command_list.get(0).task_command_id)
        
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
        
        #非自律動作処理.
        try:
            return self.non_operating_work()
        finally:
            #自律動作中へ戻る・一時停止へ移るときは、速度制限を外す.
            self.planner.set_velocity_scale(1.0)
    
    #非自律動作処理.
    #  作業者が近くにいる前提で、速度を制限したまま作業を続ける(仕様書 2.7章「非自律動作中」).
    #  協働作業終了(stop_manip_task)が来たら 'collaboend' を返し、自律動作中へ戻る.
    def non_operating_work(self):
        # === TODO-5 =================================================
        # 非自律動作中は、ロボットは止まりません. 作業者が近くにいるので、
        # 速度を落として、自律動作の「続き」の動作を実行します.
        #   (1) 速度を NON_OPERATING_VELOCITY_SCALE 倍に制限する
        #   (2) 自律動作と同じ動作の続きを実行し、その戻り値(outcome)を return する
        #       例) 最後まで動く               -> 'succeeded'  -> 作業結果を通知
        #           /stop_manip_task が呼ばれる -> 'collaboend' -> 自律動作中へ戻る
        #
        # 使える道具:
        #   self.planner.set_velocity_scale(倍率)  # 以降の動作の速度・加速度を 倍率 倍にする
        #   self.operating_work()                  # 自律動作中と同じ動作を、終わった動作の続きから実行し、
        #                                          # outcome の文字列を返す
        #
        # ヒント：
        #   self.planner.____(NON_OPERATING_VELOCITY_SCALE)
        #   return self.____()
        # ============================================================
        # ここから

        # ここまで
        CollaborationTool.loginfo('TODO-5 が未記入です. 非自律動作中の処理がないため作業を中断します')
        return 'aborted'

###########################################
#一時停止中処理クラス.                    #
###########################################
class PAUSED_WORK(CollaborationState):
    def __init__(self, label, taskfin:TaskFinishServer, tran:Transition, outcomes):
        super().__init__(label, tran, outcomes)
        self.taskfin = taskfin

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        CollaborationTool.loginfo('========== 一時停止中 (Paused) ==========')

        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event

        #待機処理.
        return self.paused()

    #一時停止中は、ロボットはその場で止まり、自分からは動かない.
    #  一時停止解除(resume_task)が来たら 'pausecancel' を返し、一時停止前の状態へ戻る.
    def paused(self):
        CollaborationTool.loginfo('Robot holds position. Call /resume_task to resume.')
        elapsed = 0.0
        while not CollaborationTool.is_shutdown():
            #作業途中で状態遷移するイベントの確認.
            event = self.check_event()
            if(None != event):
                return event

            CollaborationTool.wait_time(PAUSED_WAIT)

            #一時停止中であることを定期的に表示する.
            elapsed += PAUSED_WAIT
            if elapsed >= PAUSED_LOG_INTERVAL:
                CollaborationTool.loginfo('... Paused: waiting for /resume_task')
                elapsed = 0.0

        return 'aborted'

    #作業途中で状態遷移するイベントの確認.
    def check_event(self):
        if self.tran.get_event().is_workend():
            command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        return None

###########################################
#終了処理クラス.                          #
###########################################        
class FINALISE(CollaborationState):
    def __init__(self,
                 label,
                 taskfin:TaskFinishServer,
                 tran:Transition,
                 outcomes):
        super().__init__(label, tran, outcomes)
        self.planner = ShareMovePlanner.get_move_planner()
        self.taskfin = taskfin
        self.counter = 0

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)

        if self.tran.get_event().is_workend():
            task_command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = task_command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        
        if self.preempt('INIITIALISE_POSE is being preempted!!!'):
            return 'preempted'
        
        #終了処理を行う.
        return self.finalise()

    #終了処理.
    def finalise(self):
        ###ロボットごとの終了動作.
        #ここから.

        #トレイを持っているときに軸を動かすと事故につながるので何もせず終了.

        #終了する.
        CollaborationTool.signal_shutdown("sys_manage_halt")

        #ここまで.
        return 'succeeded'
    
    def init_pose(self):
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('finalise')
            rc = self.planner.initial_pose()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'