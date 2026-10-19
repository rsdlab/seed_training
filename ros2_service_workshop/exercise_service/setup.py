from setuptools import find_packages, setup

package_name = 'ros2_service_sample'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your@email.com',
    description='ROS2 Jazzy Python Service通信サンプル',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'service_server = ros2_service_sample.server_node:main',
            'service_client = ros2_service_sample.client_node:main',
        ],
    },
)
