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
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import ThisLaunchFileDir


def generate_launch_description():
    ld = LaunchDescription()

    launch_dir = ThisLaunchFileDir()

    # Launch Configurations
    prefix = LaunchConfiguration('prefix')

    # Launch Arguments
    declare_prefix = DeclareLaunchArgument(
        'prefix',
        default_value='',
        description='Prefix of the joint and link names.',
    )
    ld.add_action(declare_prefix)

    # RViz
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_dir, '/moveit_rviz.launch.py']),
        launch_arguments={
            'prefix': prefix,
            'use_gazebo': 'true',
            'use_fake_hardware': 'false',
            'fake_sensor_commands': 'false',
            'use_sim_time': 'true',
        }.items(),
    )
    ld.add_action(rviz_launch)

    # Move Group
    move_group_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_dir, '/move_group.launch.py']),
        launch_arguments={
            'prefix': prefix,
            'use_gazebo': 'true',
            'use_fake_hardware': 'false',
            'fake_sensor_commands': 'false',
            'use_sim_time': 'true',
        }.items(),
    )
    ld.add_action(move_group_launch)

    return ld
