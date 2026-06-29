#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn, TeleportAbsolute
from turtlesim.msg import Pose
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

        # Leader-follower state
        self.leader_pose = None
        self.follower_poses = {'turtle1': None, 'turtle2': None, 'turtle3': None}
        self.leader_cmd = Twist()
        self.follow_dist = 1.5
        self.follow_lateral = 0.8
        self.kp_linear = 1.5
        self.kp_angular = 4.0
        self.leader_spawned = False

        for name in self.turtle_names:
            self.cmd_pubs[name] = self.create_publisher(Twist, f'/{name}/cmd_vel', 10)
        self.leader_pub = self.create_publisher(Twist, '/turtle4/cmd_vel', 10)

        self.spawn_turtles()
        self.sub = self.create_subscription(Int8, '/formation_mode', self.mode_callback, 10)
        self.timer = self.create_timer(0.05, self.control_loop)

        # Leader-follower subscriptions
        self.create_subscription(Pose, '/turtle1/pose', lambda m: self._pose_cb('turtle1', m), 10)
        self.create_subscription(Pose, '/turtle2/pose', lambda m: self._pose_cb('turtle2', m), 10)
        self.create_subscription(Pose, '/turtle3/pose', lambda m: self._pose_cb('turtle3', m), 10)
        self.create_subscription(Pose, '/turtle4/pose', self._leader_pose_cb, 10)
        self.create_subscription(Twist, '/leader_cmd_vel', self._leader_cmd_cb, 10)

        self.get_logger().info('编队控制器启动，按 1/2/3/0 切换队形，4 领航跟随')

    def _pose_cb(self, name, msg):
        self.follower_poses[name] = msg

    def _leader_pose_cb(self, msg):
        self.leader_pose = msg

    def _leader_cmd_cb(self, msg):
        self.leader_cmd = msg

    def spawn_leader(self):
        if self.leader_spawned:
            return
        client = self.create_client(Spawn, '/spawn')
        if client.wait_for_service(timeout_sec=1.0):
            req = Spawn.Request()
            req.name = 'turtle4'
            req.x = 5.5
            req.y = 8.5
            req.theta = 0.0
            client.call_async(req)
            self.leader_spawned = True
            self.get_logger().info('领航乌龟 turtle4 已生成')

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
        new_mode = msg.data
        # Exiting leader mode? Stop leader
        if self.mode == 4 and new_mode != 4:
            self.leader_pub.publish(Twist())
            self.leader_cmd = Twist()

        self.mode = new_mode
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
        elif self.mode == 4:
            self.spawn_leader()
            self.get_logger().info('领航模式: WASD 控制 turtle4，其余乌龟跟随')
        else:
            for name in self.turtle_names:
                self.cmd_pubs[name].publish(Twist())

    def follow_target(self, my_pose, ox, oy):
        """P controller: move follower to (leader + offset) position."""
        cmd = Twist()
        if my_pose is None or self.leader_pose is None:
            return cmd
        l = self.leader_pose
        tx = l.x + ox*math.cos(l.theta) - oy*math.sin(l.theta)
        ty = l.y + ox*math.sin(l.theta) + oy*math.cos(l.theta)
        dx = tx - my_pose.x
        dy = ty - my_pose.y
        dist = math.hypot(dx, dy)
        if dist < 0.1:
            return cmd
        ang = math.atan2(dy, dx)
        diff = ang - my_pose.theta
        while diff > math.pi: diff -= 2*math.pi
        while diff < -math.pi: diff += 2*math.pi
        cmd.linear.x = min(self.kp_linear * dist, 2.0)
        cmd.angular.z = max(min(self.kp_angular * diff, 3.0), -3.0)
        return cmd

    def control_loop(self):
        if self.mode == 0:
            return

        if self.mode == 4:
            # Forward leader cmd to turtle4
            self.leader_pub.publish(self.leader_cmd)

            # Followers track leader
            lateral_offsets = {'turtle1': self.follow_lateral,
                               'turtle2': 0.0,
                               'turtle3': -self.follow_lateral}
            for name in self.turtle_names:
                cmd = self.follow_target(
                    self.follower_poses[name],
                    -self.follow_dist, lateral_offsets[name])
                self.cmd_pubs[name].publish(cmd)
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
