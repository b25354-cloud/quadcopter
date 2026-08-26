"""
ROS2 node: subscribes to a sensor_msgs/Image topic (default "/cam"), runs the
survivor detection pipeline on each frame, and publishes annotated images and
detection info.
"""

import json

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

from survivor_detection import detection_pipeline as pipeline


class SurvivorDetectionNode(Node):
    def __init__(self):
        super().__init__("survivor_detection_node")

        self.declare_parameter("camera_topic", "/cam")
        self.declare_parameter("show_debug_window", True)

        camera_topic = self.get_parameter("camera_topic").get_parameter_value().string_value
        self.show_debug_window = self.get_parameter("show_debug_window").get_parameter_value().bool_value

        self.bridge = CvBridge()
        self.model = pipeline.load_model()
        self.tracker = pipeline.SimpleTracker()
        self.frame_count = 0

        self.subscription = self.create_subscription(
            Image, camera_topic, self.image_callback, 10
        )
        self.annotated_pub = self.create_publisher(Image, "/survivor_detection/annotated", 10)
        self.detections_pub = self.create_publisher(String, "/survivor_detection/detections", 10)

        self.get_logger().info(f"Survivor detection node started. Subscribed to '{camera_topic}'.")

    def image_callback(self, msg: Image):
        self.frame_count += 1

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"Failed to convert incoming image: {e}")
            return

        tracks, _enhanced = pipeline.process_frame(self.model, frame, self.frame_count, self.tracker)

        detections_payload = [
            {
                "box_xyxy": [float(v) for v in track["box"]],
                "age_frames": self.frame_count - track["last_seen_frame"],
            }
            for track in tracks
        ]
        self.detections_pub.publish(String(data=json.dumps(detections_payload)))

        display_frame = pipeline.draw_tracks(frame, tracks, self.frame_count)

        try:
            annotated_msg = self.bridge.cv2_to_imgmsg(display_frame, encoding="bgr8")
            annotated_msg.header = msg.header
            self.annotated_pub.publish(annotated_msg)
        except Exception as e:
            self.get_logger().error(f"Failed to publish annotated image: {e}")

        if self.show_debug_window:
            import cv2
            cv2.imshow("Survivor Detection (ROS2 /cam)", display_frame)
            cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = SurvivorDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()