#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8
from geometry_msgs.msg import Twist
import sys, termios, tty

class FormationTeleop(Node):
    def __init__(self):
        super().__init__('formation_teleop')
        self.mode_pub = self.create_publisher(Int8, '/formation_mode', 10)
        self.leader_pub = self.create_publisher(Twist, '/leader_cmd_vel', 10)
        self.leader_mode = False
        self.get_logger().info('控制: 1直线 2圆圈 3环形 0停止 4领航 q退出')
        self.get_logger().info('领航模式下: W前进 S后退 A左转 D右转')

    def get_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

    def run(self):
        while rclpy.ok():
            key = self.get_key()
            if key == 'q':
                break

            if self.leader_mode:
                # In leader mode: WASD controls turtle4
                if key in '0123':
                    # Exit leader mode, switch to formation mode
                    self.leader_mode = False
                    # Stop leader
                    self.leader_pub.publish(Twist())
                    msg = Int8(); msg.data = int(key)
                    self.mode_pub.publish(msg)
                    self.get_logger().info(f'退出领航，模式 {key}')
                elif key == 'w':
                    cmd = Twist(); cmd.linear.x = 2.0
                    self.leader_pub.publish(cmd)
                elif key == 's':
                    cmd = Twist(); cmd.linear.x = -1.5
                    self.leader_pub.publish(cmd)
                elif key == 'a':
                    cmd = Twist(); cmd.angular.z = 2.0
                    self.leader_pub.publish(cmd)
                elif key == 'd':
                    cmd = Twist(); cmd.angular.z = -2.0
                    self.leader_pub.publish(cmd)
                else:
                    # Any other key stops leader
                    self.leader_pub.publish(Twist())
            else:
                # Normal mode switching
                if key == '4':
                    self.leader_mode = True
                    msg = Int8(); msg.data = 4
                    self.mode_pub.publish(msg)
                    self.get_logger().info('进入领航跟随模式')
                elif key in '0123':
                    msg = Int8(); msg.data = int(key)
                    self.mode_pub.publish(msg)
                    self.get_logger().info(f'模式 {key}')

def main(args=None):
    rclpy.init(args=args)
    node = FormationTeleop()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
