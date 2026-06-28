#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8
import sys, termios, tty

class FormationTeleop(Node):
    def __init__(self):
        super().__init__('formation_teleop')
        self.pub = self.create_publisher(Int8, '/formation_mode', 10)
        self.get_logger().info('控制: 1直线  2圆圈  3环形  0停止  q退出')

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
            if key in '0123':
                msg = Int8()
                msg.data = int(key)
                self.pub.publish(msg)
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
