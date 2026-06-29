# ROS2 多乌龟编队表演系统

基于 ROS2 Humble + turtlesim 的多机器人编队协同控制系统。

## 功能

### 编队模式（formation_controller + formation_teleop）

| 模式 | 按键 | 说明 |
|------|------|------|
| **直线队形** | `1` | 所有乌龟以相同速度同步前进 |
| **多半径环形队形** | `2` | 乌龟以不同半径绕同心圆运动 |
| **固定夹角环形编队** | `3` | 所有乌龟保持 120° 相位差同速绕圈（挑战任务） |
| **停止** | `0` | 所有乌龟停止运动 |

### 扩展功能：领航跟随（leader_follower）

通过 WASD 键盘控制 **turtle1（领航者）** 运动，**turtle2 和 turtle3** 基于 P 控制器自动跟随，保持固定相对位置。

## 快速开始

```bash
# 1. 编译
cd ~/ros2_ws
colcon build --packages-select formation_package
source install/setup.bash
```

### 编队模式（三个终端）

```bash
# 终端1
ros2 run turtlesim turtlesim_node

# 终端2
ros2 run formation_package formation_controller

# 终端3
ros2 run formation_package formation_teleop
```

### 领航跟随模式（单独运行）

```bash
# 终端1
ros2 run turtlesim turtlesim_node

# 终端2
ros2 run formation_package leader_follower
```

| 按键 | 功能 |
|------|------|
| `W` | 前进 |
| `S` | 后退 |
| `A` | 左转 |
| `D` | 右转 |
| `Q` | 退出 |

## 包结构

```
src/formation_package/
├── formation_package/
│   ├── __init__.py
│   ├── formation_controller.py    # 编队控制节点
│   ├── formation_teleop.py        # 键盘控制节点
│   └── leader_follower.py         # 领航跟随节点（扩展）
├── launch/
│   └── formation_demo.launch.py
├── resource/
│   └── formation_package
├── package.xml
├── setup.cfg
├── setup.py
└── README.md
```

## 运行环境

- Ubuntu 22.04 + ROS2 Humble
- Python 3.10+
