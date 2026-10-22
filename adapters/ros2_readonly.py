#!/usr/bin/env python3
"""Read-only ROS 2 camera and map-pose adapter; never creates a publisher."""
import argparse
import base64
import io
import json
import math
from pathlib import Path
from PIL import Image as PILImage
from common import LatestSender, metadata


def image_jpeg(msg, compressed=False):
    raw = bytes(msg.data)
    encoding = msg.format.lower() if compressed else msg.encoding.lower()
    if "jpeg" in encoding or "jpg" in encoding:
        with PILImage.open(io.BytesIO(raw)) as im:
            im.load()
            image = im.convert("RGB")
    else:
        if compressed:
            with PILImage.open(io.BytesIO(raw)) as im:
                im.load()
                image = im.convert("RGB")
        elif encoding in ("rgb8", "bgr8", "mono8"):
            mode = "L" if encoding == "mono8" else "RGB"
            rawmode = "BGR" if encoding == "bgr8" else mode
            image = PILImage.frombytes(mode, (msg.width, msg.height), raw, "raw", rawmode, msg.step).convert("RGB")
        else:
            raise ValueError("unsupported image encoding: " + encoding)
    image.thumbnail((1280,720))
    out = io.BytesIO()
    image.save(out, format="JPEG", quality=80)
    return base64.b64encode(out.getvalue()).decode()


def main():
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image, CompressedImage
    from geometry_msgs.msg import PoseStamped
    from nav_msgs.msg import Odometry
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="http://127.0.0.1:8080")
    parser.add_argument("--image-topic", default="/camera/color")
    parser.add_argument("--compressed", action="store_true")
    parser.add_argument("--pose-topic", default="/localization/pose")
    parser.add_argument("--odometry", action="store_true")
    parser.add_argument("--transform", type=Path, help="explicit map<-source SE(2) calibration JSON")
    parser.add_argument("--capture-timestamps", action="store_true", help="use ROS header stamps; only after verifying clock source")
    parser.add_argument("--clock-offset-s", type=float, default=0, help="server UTC minus ROS source clock")
    args = parser.parse_args()
    transform = json.loads(args.transform.read_text()) if args.transform else None
    if transform and not transform.get("calibrated"):
        parser.error("transform must be measured and calibrated=true")
    if args.odometry and not transform:
        parser.error("Odometry requires explicit map<-odom transform; it still drifts")
    sender = LatestSender(args.server)

    class Adapter(Node):
        def __init__(self):
            super().__init__("tracr_readonly_display")
            self.create_subscription(CompressedImage if args.compressed else Image,
                                     args.image_topic, self.camera, qos_profile_sensor_data)
            self.create_subscription(Odometry if args.odometry else PoseStamped,
                                     args.pose_topic, self.pose, qos_profile_sensor_data)

        def meta(self, msg):
            if args.capture_timestamps:
                t = msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9 + args.clock_offset_s
                return metadata("real-ros2", t, "capture")
            return metadata("real-ros2", basis="receipt")

        def camera(self, msg):
            meta = self.meta(msg)
            try:
                sender.put("/api/camera", {**meta, "jpeg": image_jpeg(msg, args.compressed)})
            except (ValueError, OSError) as exc:
                self.get_logger().warning(str(exc))

        def pose(self, msg):
            meta = self.meta(msg)
            p = msg.pose.pose if args.odometry else msg.pose
            q = p.orientation
            norm = q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w
            if not math.isfinite(norm) or abs(norm-1) > .02:
                self.get_logger().warning("Rejecting non-unit quaternion")
                return
            yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
            x,y,z = p.position.x,p.position.y,p.position.z
            if transform:
                if msg.header.frame_id != transform["source_frame"]:
                    self.get_logger().warning("Rejecting unexpected source frame")
                    return
                angle = transform["yaw"]
                x,y = (math.cos(angle)*x-math.sin(angle)*y+transform["x"],
                       math.sin(angle)*x+math.cos(angle)*y+transform["y"])
                z += transform.get("z",0)
                yaw += angle
            elif msg.header.frame_id != "map":
                self.get_logger().warning("Rejecting non-map pose; provide measured --transform")
                return
            sender.put("/api/pose", {**meta, "frame_id":"map", "x":x,"y":y,"z":z,"yaw":yaw,
                                    "quality":"odometry" if args.odometry else "localized"})

    rclpy.init()
    node = Adapter()
    if node.get_parameter("use_sim_time").value:
        raise RuntimeError("use_sim_time must be false for physical input")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        sender.close()


if __name__ == "__main__":
    main()
