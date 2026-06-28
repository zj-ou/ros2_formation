#!/usr/bin/env python3
"""Launch file for the multi-turtle formation performance system."""

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen'
        ),
        Node(
            package='formation_package',
            executable='formation_controller',
            name='formation_controller',
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'run', 'formation_package', 'formation_teleop'],
            output='screen',
            emulate_tty=True,
        ),
    ])
