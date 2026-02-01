import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import os
import sys
import time
import ctypes

# --- CFFI & LIBRARY LOADING (Linux-Fix) ---
base_path = "/usr/lib/ultraleap-hand-tracking-service"
if base_path not in sys.path:
    sys.path.append(base_path)

try:
    # Global loading of the shared library
    ctypes.CDLL(os.path.join(base_path, "libLeapC.so"), mode=ctypes.RTLD_GLOBAL)
    # Import from the package structure
    from leapc_cffi._leapc_cffi import ffi, lib as libleapc
except Exception as e:
    print(f"Critical error loading the Ultraleap library {e}")
    sys.exit(1)

class LeapControlNode(Node):
    def __init__(self):
        super().__init__('leap_control_node')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Initializing connection...
        self.conn_handle = ffi.new("LEAP_CONNECTION *")
        config = ffi.new("LEAP_CONNECTION_CONFIG *")
        config.server_namespace = ffi.NULL
        config.flags = 0
        
        libleapc.LeapCreateConnection(config, self.conn_handle)
        libleapc.LeapOpenConnection(self.conn_handle[0])
        
        # Set background policy
        libleapc.LeapSetPolicyFlags(self.conn_handle[0], 
                                    libleapc.eLeapPolicyFlag_BackgroundFrames, 0)
        
        self.msg = ffi.new("LEAP_CONNECTION_MESSAGE *")

        # --- CONFIGURATION ---
        self.LIMIT = 25.0        # Threshold in mm
        self.SAMPLE_DELAY = 0.05 # 20Hz for smooth ROS2 control
        self.timer = self.create_timer(self.SAMPLE_DELAY, self.timer_callback)
        
        os.system('clear')
        print("ROS2 node active. Sending data to /cmd_vel...")

    def timer_callback(self):
        latest_frame = None
        # Empty buffer (Real Time)
        while True:
            # 10ms Timeout for USBIP-Latency
            res = libleapc.LeapPollConnection(self.conn_handle[0], 10, self.msg)
            if res == libleapc.eLeapRS_Success:
                if self.msg.type == libleapc.eLeapEventType_Tracking:
                    latest_frame = self.msg.tracking_event
            else:
                break

        lx, ly, az = 0.0, 0.0, 0.0
        zone = "STOPP (CENTRE)"
        row, col = 0, 0
        hand_detected = False
        px, pz = 0.0, 0.0

        if latest_frame and latest_frame.nHands > 0:
            hand_detected = True
            hand = latest_frame.pHands[0]
            p = hand.palm.position
            px, pz = p.x, p.z
            
            # Fix axis (Mirroring)
            cz = -p.z 
            cx = p.x

            # 3x3 logic Mapping
            col = -1 if cx < -self.LIMIT else (1 if cx > self.LIMIT else 0)
            row = -1 if cz > self.LIMIT else (1 if cz < -self.LIMIT else 0) 

            # --- MOVEMENT MAPPING ---
            if row == -1: # FRONT
                lx = 0.5
                if col == -1: az, zone = 0.8, "FRONT LEFT ROTATION"
                elif col == 1: az, zone = -0.8, "FRONT RIGHT ROTATION"
                else: zone = "FORWARDS"
            elif row == 1: # REAR
                lx = -0.4
                if col == -1: az, zone = 0.8, "REAR LEFT ROTATION"
                elif col == 1: az, zone = -0.8, "REAR RIGHT ROTATION"
                else: zone = "BACKWARDS"
            else: # CENTRE
                if col == -1: ly, zone = 0.4, "GLIDE LEFT"
                elif col == 1: ly, zone = -0.4, "GLIDE RIGHT"
                else: zone = "STOPP (CENTRE)"

        # ROS2 Nachricht publizieren
        twist_msg = Twist()
        twist_msg.linear.x = float(lx)
        twist_msg.linear.y = float(ly)
        twist_msg.angular.z = float(az)
        self.publisher_.publish(twist_msg)

        # UI DARSTELLUNG
        self.render_terminal_gui(row, col, zone, hand_detected, px, pz, lx, ly, az)

    def render_terminal_gui(self, row, col, zone, hand_detected, px, pz, lx, ly, az):
        sys.stdout.write("\033[H")
        print("="*65)
        print(f" ROS2 TOPIC: /cmd_vel  |  MSG TYPE: geometry_msgs/Twist")
        print("="*65)

        grid = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        if hand_detected:
            # +1 da row/col von -1 bis 1 gehen
            grid[row+1][col+1] = "X"

        print(f"\n  GRID POSITION:             ACTIVE ZONE: {zone}")
        print(f"  +---+---+---+")
        print(f"  | {grid[0][0]} | {grid[0][1]} | {grid[0][2]} |  (FRONT)")
        print(f"  +---+---+---+                MEASUREMENT:")
        print(f"  | {grid[1][0]} | {grid[1][1]} | {grid[1][2]} |  (CENTRE)       X: {px:6.1f}")
        print(f"  +---+---+---+                Z: {pz:6.1f}")
        print(f"  | {grid[2][0]} | {grid[2][1]} | {grid[2][2]} |  (REAR)")
        print(f"  +---+---+---+")

        print(f"\n SENT MESSAGE (geometry_msgs/Twist):")
        print(f"  linear:  {{x: {lx:4.2f}, y: {ly:4.2f}, z: 0.00}}")
        print(f"  angular: {{x: 0.00, y: 0.00, z: {az:4.2f}}}")
        print("-" * 65)
        sys.stdout.flush()

def main(args=None):
    rclpy.init(args=args)
    node = LeapControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        libleapc.LeapCloseConnection(node.conn_handle[0])
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()