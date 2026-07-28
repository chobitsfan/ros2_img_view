#!/usr/bin/env python3
"""Subscribe to a mono image topic, display it, and save a PNG when 's' is pressed."""

import datetime

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import QoSProfile, ReliabilityPolicy

WINDOW = "image"


class ImgView(Node):
    def __init__(self, topic):
        super().__init__("img_view")
        self.bridge = CvBridge()
        self.frame = None
        self.create_subscription(Image, topic, self.on_image, QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, depth=10))
        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        # Poll the GUI/keyboard at ~30 Hz.
        self.create_timer(1.0 / 30.0, self.on_timer)
        self.get_logger().info(f"subscribed to {topic}; press 's' to save, 'q' to quit")

    def on_image(self, msg):
        # "mono8" gives a single-channel grayscale image.
        self.frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="mono8")

    def on_timer(self):
        if self.frame is not None:
            cv2.imshow(WINDOW, self.frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s") and self.frame is not None:
            name = datetime.datetime.now().strftime("image_%Y%m%d_%H%M%S_%f.png")
            cv2.imwrite(name, self.frame)
            self.get_logger().info(f"saved {name}")
        elif key == ord("q"):
            rclpy.shutdown()


def main():
    rclpy.init()
    node = ImgView(topic="/mono_left")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
