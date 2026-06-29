#!/usr/bin/env python3
"""
Leader-Follower Node
- WASD controls the leader (turtle1)
- turtle2 and turtle3 automatically follow with fixed offset
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import sys
import termios
import tty
import select


class LeaderFollower(Node):
    def __init__(self):
        super().__init__('leader_follower')
        self.leader_pose = Pose()
        self.follower_poses = {'turtle2': None, 'turtle3': None}

        self.follow_dist = 1.5       # 跟随后置距离
        self.follow_lateral = 0.8    # 左右偏移（turtle2左, turtle3右）
        self.max_linear = 2.0
        self.max_angular = 3.0
        self.kp_linear = 1.5
        self.kp_angular = 4.0

        # Publishers: leader + followers
        self.leader_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub_t2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.pub_t3 = self.create_publisher(Twist, '/turtle3/cmd_vel', 10)

        # Subscribe to poses
        self.create_subscription(Pose, '/turtle1/pose', self.pose_cb_leader, 10)
        self.create_subscription(Pose, '/turtle2/pose', self.pose_cb_t2, 10)
        self.create_subscription(Pose, '/turtle3/pose', self.pose_cb_t3, 10)

        self.leader_cmd = Twist()
        self.running = True

        self.get_logger().info('领航跟随模式启动')
        self.get_logger().info('W=前进  S=后退  A=左转  D=右转  Q=退出')
        self.get_logger().info(f'turtle2 跟随 (后{self.follow_dist}m 左{self.follow_lateral}m)')
        self.get_logger().info(f'turtle3 跟随 (后{self.follow_dist}m 右{self.follow_lateral}m)')

    def pose_cb_leader(self, msg):
        self.leader_pose = msg

    def pose_cb_t2(self, msg):
        self.follower_poses['turtle2'] = msg

    def pose_cb_t3(self, msg):
        self.follower_poses['turtle3'] = msg

    def get_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            # Non-blocking read with timeout
            if select.select([sys.stdin], [], [], 0.05)[0]:
                ch = sys.stdin.read(1)
                return ch
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def follow_target(self, my_pose, offset_x, offset_y):
        """Proportional control: move to target position relative to leader."""
        cmd = Twist()

        if my_pose is None:
            return cmd

        # Target position relative to leader's frame
        leader = self.leader_pose
        target_x = leader.x + offset_x * math.cos(leader.theta) - offset_y * math.sin(leader.theta)
        target_y = leader.y + offset_x * math.sin(leader.theta) + offset_y * math.cos(leader.theta)

        # Error in global frame
        dx = target_x - my_pose.x
        dy = target_y - my_pose.y
        dist = math.hypot(dx, dy)

        if dist < 0.1:
            return cmd

        # Desired heading
        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - my_pose.theta
        # Normalize to [-pi, pi]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        cmd.linear.x = min(self.kp_linear * dist, self.max_linear)
        cmd.angular.z = min(self.kp_angular * angle_diff, self.max_angular)
        cmd.angular.z = max(cmd.angular.z, -self.max_angular)
        return cmd

    def run(self):
        while rclpy.ok() and self.running:
            key = self.get_key()

            if key == 'q':
                break

            # Leader keyboard control
            cmd = Twist()
            if key == 'w':
                cmd.linear.x = 2.0
            elif key == 's':
                cmd.linear.x = -1.5
            elif key == 'a':
                cmd.angular.z = 2.0
            elif key == 'd':
                cmd.angular.z = -2.0
            elif key is not None:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0

            self.leader_pub.publish(cmd)

            # Followers: turtle2 behind-left, turtle3 behind-right
            cmd_t2 = self.follow_target(
                self.follower_poses['turtle2'],
                -self.follow_dist, self.follow_lateral
            )
            cmd_t3 = self.follow_target(
                self.follower_poses['turtle3'],
                -self.follow_dist, -self.follow_lateral
            )
            self.pub_t2.publish(cmd_t2)
            self.pub_t3.publish(cmd_t3)

        # Stop all
        stop = Twist()
        self.leader_pub.publish(stop)
        self.pub_t2.publish(stop)
        self.pub_t3.publish(stop)
        self.get_logger().info('领航跟随已停止')


def main(args=None):
    rclpy.init(args=args)
    node = LeaderFollower()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
