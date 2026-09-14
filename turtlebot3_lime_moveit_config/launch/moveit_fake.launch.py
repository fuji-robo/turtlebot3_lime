#!/usr/bin/env python3
#
# Copyright 2020 ROBOTIS CO., LTD.
# Copyright 2026 Hibikino-Musashi@Home
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Hye-jong KIM
# Maintainers: Tomoaki Fujino


from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.substitutions import FindExecutable
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import ThisLaunchFileDir
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ld = LaunchDescription()

    launch_dir = PathJoinSubstitution(
        [ThisLaunchFileDir(), 'launch'],
    )

    # Launch Configurations
    prefix = LaunchConfiguration('prefix')
    use_rviz = LaunchConfiguration('use_rviz')
    fake_sensor_commands = LaunchConfiguration('fake_sensor_commands')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Launch Arguments
    declare_prefix = DeclareLaunchArgument(
        'prefix',
        default_value='',
        description='Prefix of the joint and link names.',
    )

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='false',
        description='Whether to execute RViz2.',
    )

    declare_fake_sensor_commands = DeclareLaunchArgument(
        'fake_sensor_commands',
        default_value='false',
        description='Enable fake command interfaces for sensors.',
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true.',
    )

    ld.add_action(declare_prefix)
    ld.add_action(declare_use_rviz)
    ld.add_action(declare_fake_sensor_commands)
    ld.add_action(declare_use_sim_time)

    # Robot Description
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution(
                [
                    FindPackageShare('turtlebot3_lime_description'),
                    'urdf',
                    'turtlebot3_lime.urdf.xacro',
                ],
            ),
            ' ',
            'prefix:=',
            prefix,
            ' ',
            'use_gazebo:=false',
            ' ',
            'use_fake_hardware:=true',
            ' ',
            'fake_sensor_commands:=',
            fake_sensor_commands,
        ]
    )

    robot_description = {
        'robot_description': robot_description_content,
    }

    controllers_file = PathJoinSubstitution(
        [
            FindPackageShare('turtlebot3_lime_moveit_config'),
            'config',
            'ros2_controllers.yaml',
        ]
    )

    # Robot State Publisher
    rsp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_dir, '/rsp.launch.py']),
        launch_arguments={
            'prefix': prefix,
            'use_gazebo': 'false',
            'use_fake_hardware': 'true',
            'fake_sensor_commands': fake_sensor_commands,
            'use_sim_time': use_sim_time,
        }.items(),
    )
    ld.add_action(rsp_launch)

    # Fake ros2_control
    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        output='screen',
        parameters=[
            robot_description,
            controllers_file,
            {
                'use_sim_time': use_sim_time,
            },
        ],
    )
    ld.add_action(ros2_control_node)

    # Load ros2_control controllers
    load_ros2_controllers_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [launch_dir, '/load_ros2_controllers.launch.py'],
        ),
    )
    ld.add_action(load_ros2_controllers_launch)

    # RViz
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_dir, '/moveit_rviz.launch.py']),
        launch_arguments={
            'prefix': prefix,
            'use_gazebo': 'false',
            'use_fake_hardware': 'true',
            'fake_sensor_commands': fake_sensor_commands,
            'use_sim_time': use_sim_time,
        }.items(),
        condition=IfCondition(use_rviz),
    )
    ld.add_action(rviz_launch)

    # Move Group
    move_group_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_dir, '/move_group.launch.py']),
        launch_arguments={
            'prefix': prefix,
            'use_gazebo': 'false',
            'use_fake_hardware': 'true',
            'fake_sensor_commands': fake_sensor_commands,
            'use_sim_time': use_sim_time,
        }.items(),
    )
    ld.add_action(move_group_launch)

    return ld
