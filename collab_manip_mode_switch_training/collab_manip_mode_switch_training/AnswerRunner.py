#!/usr/bin/env python3
# coding: UTF-8
#
# 解答版で起動するためのランチャ（講師用・編集不要）
#
# answer/*_answer.py を、同じ名前のモジュールの代わりに読み込んでから起動する.
# 穴あき版のファイルは書き換えないので、受講者用のコードはそのまま残る.
#
#   ros2 run collab_manip_mode_switch_training CollaborationManipulationModuleAnswer --dummy

import importlib.util
import os
import sys

from ament_index_python.packages import get_package_share_directory

PACKAGE = 'collab_manip_mode_switch_training'

# 依存される側から順に読み込む（後のモジュールが import したときに解答版が使われるように）.
ANSWER_MODULES = [
    'TransitionModule',
    'CollaborationCommunicationModule',
    'CollaborationUserDefineModule',
    'CollaborationStateModule',
    'CollaborationManipulationModule',
]


def load_answers():
    answer_dir = os.path.join(get_package_share_directory(PACKAGE), 'answer')
    for name in ANSWER_MODULES:
        full_name = f'{PACKAGE}.{name}'
        path = os.path.join(answer_dir, f'{name}_answer.py')
        spec = importlib.util.spec_from_file_location(full_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[full_name] = module
        spec.loader.exec_module(module)
        print(f'[ANSWER] {name} <- {path}')
    return sys.modules[f'{PACKAGE}.CollaborationManipulationModule']


def main():
    load_answers().main()


if __name__ == '__main__':
    main()
