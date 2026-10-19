from glob import glob

from setuptools import find_packages, setup

package_name = 'collab_manip_mode_switch_training'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test', 'answer']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/answer', glob('answer/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rsdlab',
    maintainer_email='rsdlab@todo.todo',
    description='研修用：自律動作中 ⇄ 非自律動作中 の切り替え（穴あき演習）',
    license='MIT',
    entry_points={
        'console_scripts': [
            'CollaborationManipulationModule = collab_manip_mode_switch_training.CollaborationManipulationModule:main',
            'TaskSender = collab_manip_mode_switch_training.TaskSender:main',
            'CollaborationSwitcher = collab_manip_mode_switch_training.CollaborationSwitcher:main',
            'CollaborationManipulationModuleAnswer = collab_manip_mode_switch_training.AnswerRunner:main',
        ],
    },
)
