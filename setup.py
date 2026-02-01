from setuptools import find_packages, setup

package_name = 'leap_control'

setup(
    name=package_name,
    version='21.3.93',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Michael Christian Dörflinger',
    maintainer_email='michaeldoerflinger93@gmail.com',
    description='ROS2 node for controlling robots via Ultraleap motion controller using cmd_vel',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'leap_control = leap_control.leap_control_node:main'
        ],
    },
)
