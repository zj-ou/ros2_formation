#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn, TeleportAbsolute
from std_msgs.msg import Int8
import math

class FormationController(Node):
    def __init__(self):
        super().__init__('formation_controller')
        self.turtle_names = ['turtle1', 'turtle2', 'turtle3']
        self.cmd_pubs = {}
        self.mode = 0
        self.center_x = 5.5
        self.center_y = 5.5
        self.radius_circle = [2.0, 3.0, 4.0]
        self.ring_radius = 3.0
        self.angular_speed = 0.3
        self.phase_offset = [0, 2*math.pi/3, 4*math.pi/3]
        for name in self.turtle_names:
            self.cmd_pubs[name] = self.create_publisher(Twist, f'/{name}/cmd_vel', 10)
        self.spawn_turtles()
        self.sub = self.create_subscription(Int8, '/formation_mode', self.mode_callback, 10)
        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info('编队控制器启动，按 1/2/3/0 切换队形')

    def spawn_turtles(self):
        for name in ['turtle2', 'turtle3']:
            client = self.create_client(Spawn, '/spawn')
            if not client.wait_for_service(timeout_sec=1.0):
                continue
            req = Spawn.Request()
            req.name = name
            req.x = 3.0 if name=='turtle2' else 5.0
            req.y = 3.0 if name=='turtle2' else 5.0
            req.theta = 0.0
            client.call_async(req)

    def teleport_turtle(self, name, x, y, theta):
        client = self.create_client(TeleportAbsolute, f'/{name}/teleport_absolute')
        if not client.wait_for_service(timeout_sec=0.5):
            return
        req = TeleportAbsolute.Request()
        req.x = x; req.y = y; req.theta = theta
        client.call_async(req)

    def mode_callback(self, msg):
        self.mode = msg.data
        self.get_logger().info(f'切换模式: {self.mode}')
        if self.mode == 1:
            for i, name in enumerate(self.turtle_names):
                self.teleport_turtle(name, 1.0 + i*1.5, 5.5, 0.0)
        elif self.mode == 2:
            for i, name in enumerate(self.turtle_names):
                r = self.radius_circle[i]
                x = self.center_x + r
                y = self.center_y
                theta = math.pi/2
                self.teleport_turtle(name, x, y, theta)
        elif self.mode == 3:
            for i, name in enumerate(self.turtle_names):
                angle = self.phase_offset[i]
                x = self.center_x + self.ring_radius * math.cos(angle)
                y = self.center_y + self.ring_radius * math.sin(angle)
                theta = angle + math.pi/2
                self.teleport_turtle(name, x, y, theta)
        else:
            for name in self.turtle_names:
                self.cmd_pubs[name].publish(Twist())

    def control_loop(self):
        if self.mode == 0:
            return
        cmd = Twist()
        if self.mode == 1:
            cmd.linear.x = 0.5
            for name in self.turtle_names:
                self.cmd_pubs[name].publish(cmd)
        elif self.mode == 2:
            w = self.angular_speed
            for i, name in enumerate(self.turtle_names):
                r = self.radius_circle[i]
                cmd.linear.x = r * w
                cmd.angular.z = w
                self.cmd_pubs[name].publish(cmd)
        elif self.mode == 3:
            w = self.angular_speed
            r = self.ring_radius
            for name in self.turtle_names:
                cmd.linear.x = r * w
                cmd.angular.z = w
                self.cmd_pubs[name].publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = FormationController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
