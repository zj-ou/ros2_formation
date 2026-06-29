# ROS2 多乌龟编队表演系统

基于 ROS2 Humble + turtlesim 的多机器人编队协同控制系统。

## 功能

### 编队模式（formation_controller + formation_teleop）

同一套终端即可切换所有模式：

| 模式 | 按键 | 说明 |
|------|------|------|
| **直线队形** | `1` | 所有乌龟以相同速度同步前进 |
| **多半径环形队形** | `2` | 乌龟以不同半径绕同心圆运动 |
| **固定夹角环形编队** | `3` | 所有乌龟保持 120° 相位差同速绕圈（挑战任务） |
| **停止** | `0` | 所有乌龟停止运动 |
| **领航跟随** | `4` | 生成 turtle4 领航者，WASD 控制，其余乌龟自动跟随（扩展功能） |

### 领航跟随模式（扩展功能·模式4）

按 `4` 键进入领航跟随模式后：
- 系统自动生成 **turtle4** 作为领航者
- 按 **W/A/S/D** 控制 turtle4 运动
- **turtle1、turtle2、turtle3** 基于 P 控制器自动跟随，保持右后、正后、左后位置
- 按 **0/1/2/3** 任意键退出领航模式，恢复对应编队控制

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

### 键盘控制总览

| 按键 | 普通模式 | 领航模式（按4进入） |
|------|----------|-------------------|
| `1` | 直线队形 | 退出领航 → 直线队形 |
| `2` | 多半径环形 | 退出领航 → 多半径环形 |
| `3` | 固定夹角环形 | 退出领航 → 固定夹角环形 |
| `0` | 停止 | 退出领航 → 停止 |
| `4` | 进入领航跟随 | - |
| `W` | - | 领航者前进 |
| `S` | - | 领航者后退 |
| `A` | - | 领航者左转 |
| `D` | - | 领航者右转 |
| `q` | 退出程序 | 退出程序 |

## 包结构

```
src/formation_package/
├── formation_package/
│   ├── __init__.py
│   ├── formation_controller.py    # 编队控制节点（含模式4领航跟随）
│   └── formation_teleop.py        # 键盘控制节点（含领航WASD控制）
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
