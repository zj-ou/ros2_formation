# ROS2 多乌龟编队表演系统

基于 ROS2 Humble + turtlesim 的多机器人编队协同控制系统。

## 功能

- **模式1：直线队形** — 所有乌龟以相同速度同步前进
- **模式2：多半径环形队形** — 乌龟以不同半径绕同心圆运动
- **模式3：固定夹角环形编队** — 所有乌龟保持 120° 相位差同速绕圈（挑战任务）
- **模式0：停止** — 所有乌龟停止运动

## 快速开始

```bash
# 1. 编译
cd ~/ros2_ws
colcon build --packages-select formation_package
source install/setup.bash

# 2. 启动（三个终端）
# 终端1
ros2 run turtlesim turtlesim_node

# 终端2
ros2 run formation_package formation_controller

# 终端3
ros2 run formation_package formation_teleop
```

### 键盘控制

| 按键 | 功能 |
|------|------|
| `1` | 直线队形 |
| `2` | 多半径环形队形 |
| `3` | 固定夹角环形编队（120°） |
| `0` | 停止 |
| `q` | 退出 |

## 包结构

```
src/formation_package/
├── formation_package/
│   ├── __init__.py
│   ├── formation_controller.py    # 编队控制节点
│   └── formation_teleop.py        # 键盘控制节点
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
