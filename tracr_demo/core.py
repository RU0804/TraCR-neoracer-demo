"""Timestamp validation, bounded pairing and coordinate conversion; no I/O."""
from collections import deque
from dataclasses import dataclass
import math
import time
import uuid


class Invalid(ValueError):
    pass


def number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise Invalid(name + " must be a finite number")
    return float(value)


def stamp(data, now, max_age):
    t = number(data.get("capture_time"), "capture_time")
    if t > now + 0.05 or now - t > max_age:
        raise Invalid("capture_time outside accepted window; check clocks or stale source")
    basis = data.get("time_basis")
    if basis not in ("capture", "receipt"):
        raise Invalid("time_basis must be capture or receipt")
    return t, basis


def text_id(value, name):
    if not isinstance(value, str) or not value or len(value) > 128:
        raise Invalid(name + " must be a nonempty string (<=128 characters)")
    return value


@dataclass(frozen=True)
class Pose:
    id: str
    capture_time: float
    time_basis: str
    x: float
    y: float
    z: float
    yaw: float
    source: str
    quality: str

    @classmethod
    def parse(cls, data, now, max_age):
        t, basis = stamp(data, now, max_age)
        if data.get("frame_id") != "map":
            raise Invalid("pose must be transformed into frame_id=map before ingest")
        quality = data.get("quality")
        if quality not in ("localized", "odometry", "test"):
            raise Invalid("quality must be localized, odometry or test")
        return cls(text_id(data.get("id"), "id"), t, basis,
                   *(number(data.get(k), k) for k in ("x", "y", "z", "yaw")),
                   text_id(data.get("source"), "source"), quality)


@dataclass(frozen=True)
class Frame:
    id: str
    capture_time: float
    time_basis: str
    jpeg: bytes
    source: str


def unity_pose(pose):
    # Same basis change as pinned AutoDRIVE Socket.cs. +x forward, +y left, +z up.
    return {"ux": -pose.y, "uy": pose.z, "uz": pose.x,
            "qx": 0.0, "qy": -math.sin(pose.yaw / 2), "qz": 0.0,
            "qw": math.cos(pose.yaw / 2)}


def cosim_payload(pose):
    """Serializer only. Additional scene-dependent Socket fields are not inferred."""
    return {"V1 CoSim": "1", "V1 Reset": "False",
            "V1 PosX": str(pose.x), "V1 PosY": str(pose.y), "V1 PosZ": str(pose.z),
            "V1 RotX": "0", "V1 RotY": "0", "V1 RotZ": str(math.sin(pose.yaw/2)),
            "V1 RotW": str(math.cos(pose.yaw/2))}


class Pairer:
    def __init__(self, config, clock=time.time):
        self.config, self.clock = config, clock
        self.poses = deque(maxlen=config["buffer_size"])
        self.frames = deque(maxlen=config["buffer_size"])
        self.pending = {}
        self.last_offered = None
        self.last_published = -math.inf
        self.pose_heartbeat = None
        self.loss_time = None
        self.loss_reason = "No pose received"
        self.last_pair = None
        self.samples = deque(maxlen=600)
        self.accepted_pairs = 0

    def add_pose(self, data):
        now = self.clock()
        if data.get("quality") == "lost":
            stamp(data, now, self.config["max_age_s"])
            self.poses.clear()
            self.pending.clear()
            self.loss_time = now
            self.loss_reason = "Localization lost"
            return
        pose = Pose.parse(data, now, self.config["max_age_s"])
        if self.poses and pose.capture_time <= self.poses[-1].capture_time:
            raise Invalid("out-of-order or repeated pose timestamp")
        if self.loss_time is not None and pose.capture_time <= self.loss_time:
            raise Invalid("pose predates localization loss")
        self.poses.append(pose)
        self.pose_heartbeat = now
        self.loss_time = None
        self.loss_reason = ""

    def add_frame(self, data, jpeg):
        t, basis = stamp(data, self.clock(), self.config["max_age_s"])
        if self.frames and t <= self.frames[-1].capture_time:
            raise Invalid("out-of-order or repeated camera timestamp")
        frame = Frame(text_id(data.get("id"), "id"), t, basis, jpeg,
                      text_id(data.get("source"), "source"))
        self.frames.append(frame)
        return frame

    def offer(self):
        now = self.clock()
        self.pending = {k:v for k,v in self.pending.items() if now-v[2] <= self.config["render_timeout_s"]}
        if not self.poses or not self.frames:
            return None
        frame = self.frames[-1]
        if frame.id == self.last_offered or now-frame.capture_time > self.config["stale_s"]:
            return None
        pose = min(self.poses, key=lambda p: abs(p.capture_time-frame.capture_time))
        if (now-self.poses[-1].capture_time > self.config["stale_s"] or
                abs(pose.capture_time-frame.capture_time) > self.config["max_skew_s"]):
            return None
        # A single outstanding render avoids an unbounded work queue and reversed replies.
        if self.pending:
            return None
        ticket = uuid.uuid4().hex
        self.pending[ticket] = (frame, pose, now)
        self.last_offered = frame.id
        return {"ticket": ticket, "frame_id": frame.id, "pose_id": pose.id,
                "capture_time": frame.capture_time, "pose_time": pose.capture_time,
                **unity_pose(pose)}

    def finish(self, ticket, frame_id, pose_id):
        if ticket not in self.pending:
            raise Invalid("unknown, expired or duplicate render ticket")
        frame, pose, sent = self.pending[ticket]
        now = self.clock()
        if frame.id != frame_id or pose.id != pose_id:
            raise Invalid("render acknowledgement does not match source ids")
        del self.pending[ticket]
        if (now-sent > self.config["render_timeout_s"] or
                now-frame.capture_time > self.config["stale_s"] or
                now-pose.capture_time > self.config["stale_s"] or
                frame.capture_time <= self.last_published):
            raise Invalid("render arrived too late or out of order")
        self.last_published = frame.capture_time
        self.last_pair = now
        self.accepted_pairs += 1
        self.samples.append((1000*(now-frame.capture_time), 1000*abs(frame.capture_time-pose.capture_time)))
        return frame, pose

    def status(self):
        now = self.clock()
        frame = self.frames[-1] if self.frames else None
        pose = self.poses[-1] if self.poses else None
        def age(item):
            return max(0, (now-item.capture_time)*1000) if item else None
        fresh_video = bool(frame and now-frame.capture_time <= self.config["stale_s"])
        fresh_pose = bool(pose and now-pose.capture_time <= self.config["stale_s"])
        rendered = (self.last_pair is not None and fresh_pose and
                    now-self.last_published <= self.config["stale_s"])
        calibrated_time = bool(frame and pose and frame.time_basis == pose.time_basis == "capture")
        def p95(index):
            values = sorted(x[index] for x in self.samples)
            return values[math.ceil(.95*len(values))-1] if values else None
        return {"video_fresh": fresh_video, "pose_fresh": fresh_pose, "render_fresh": rendered,
                "video_age_ms": age(frame), "pose_age_ms": age(pose),
                "pose_quality": pose.quality if pose else "lost",
                "clock_verified": self.config["clock_verified"],
                "capture_timestamps": calibrated_time,
                "timing_verified": calibrated_time and self.config["clock_verified"],
                "video_source": frame.source if frame else "—",
                "pose_source": pose.source if pose else "—",
                "loss_reason": self.loss_reason,
                "accepted_pairs": self.accepted_pairs,
                "p95_ingest_to_pair_age_ms": p95(0), "p95_source_skew_ms": p95(1)}
