#!/usr/bin/env python3
#
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
# Author: Tomoaki Fujino

from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    controllers_file = PathJoinSubstitution(
        [
            FindPackageShare('turtlebot3_lime_moveit_config'),
            'config',
            'ros2_controllers.yaml',
        ]
    )

    def spawner(controller_name):
        return Node(
            package='controller_manager',
            executable='spawner',
            arguments=[
                controller_name,
                '--param-file',
                controllers_file,
            ],
            output='screen',
        )

    # Joint State Broadcaster
    joint_state_broadcaster_spawner = spawner('joint_state_broadcaster')

    # Arm Controller
    arm_controller_spawner = spawner('arm_controller')

    # Gripper Controller
    gripper_controller_spawner = spawner('gripper_controller')

    # Start the arm controller after the joint state broadcaster.
    start_arm_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[
                arm_controller_spawner,
            ],
        )
    )

    # Start the gripper controller after the arm controller.
    start_gripper_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=arm_controller_spawner,
            on_exit=[
                gripper_controller_spawner,
            ],
        )
    )

    ld = LaunchDescription()

    ld.add_action(joint_state_broadcaster_spawner)
    ld.add_action(start_arm_controller)
    ld.add_action(start_gripper_controller)

    return ld
