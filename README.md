# leap_control

ROS2 node for controlling robots via Ultraleap motion controller using cmd_vel.

![Leap Control ROS2](https://github.com/Michdo93/test2/blob/main/ros2_leap.jpeg?raw=true)

## Pre-Installation

At first you have to install the Ultraleap SDK.

Add the GPG Key:

```
wget -qO - https://repo.ultraleap.com/keys/apt/gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/ultraleap.gpg
```

Add the repository:

```
echo 'deb [arch=amd64] https://repo.ultraleap.com/apt stable main' | sudo tee /etc/apt/sources.list.d/ultraleap.list
```

Install the Software:

```
sudo apt update
sudo apt install -y ultraleap-hand-tracking
```

Normally, it should start and enable the service automatically. That's what it says in the installation instructions.

## Installation

Then you have to go to your `ros2_ws/src` folder and clone this repository:

```
cd ~/ros2_ws/src
git clone https://github.com/Michdo93/leap_control
```

After that you have to run `colcon build`:

```
colcon build --packages-select leap_control
```

## Usage

You can run this `colcon package` with:

```
ros2 run leap_control leap_control
```

You should see something like this:

```
=================================================================
 ROS2 TOPIC: /cmd_vel  |  MSG TYPE: geometry_msgs/Twist
=================================================================

  GRID POSITION:             ACTIVE ZONE: STOPP (CENTRE)
  +---+---+---+
  |   |   |   |  (FRONT)
  +---+---+---+                MEASUREMENT:
  |   |   |   |  (CENTRE)       X:    0.0
  +---+---+---+                Z:    0.0
  |   |   |   |  (REAR)
  +---+---+---+

 SENT MESSAGE (geometry_msgs/Twist):
  linear:  {x: 0.00, y: 0.00, z: 0.00}
  angular: {x: 0.00, y: 0.00, z: 0.00}
-----------------------------------------------------------------
```
