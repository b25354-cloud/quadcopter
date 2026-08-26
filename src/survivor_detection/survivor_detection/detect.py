import os
# Must be set before onnxruntime initializes. Pins inference to use all
# available CPU cores instead of ONNX Runtime's conservative default.
os.environ.setdefault("OMP_NUM_THREADS", str(os.cpu_count()))
os.environ.setdefault("ORT_NUM_THREADS", str(os.cpu_count()))

import cv2
import numpy as np
import time
import threading
from ultralytics import YOLO
from collections import deque

# ---- CONFIG ----
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.25   # lowered from 0.5 to catch partial/occluded people
MODEL_NAME = "yolo11s.onnx"   # YOLO11 (newer/better than YOLOv8) exported to ONNX
                               # for faster CPU inference. Run export_model.py first
                               # to generate this file.
INFERENCE_SIZE = 480          # matches the imgsz used during export -- reduced from
                               # 640 for real FPS gain on CPU with minor accuracy cost
NMS_IOU_THRESHOLD = 0.85      # YOLO's own internal NMS threshold. Default is 0.7 --
                               # raised here so two heavily overlapping/close people
                               # (e.g. standing side by side) aren't auto-merged into
                               # one detection before our code even sees them.
TRACK_MEMORY_FRAMES = 8       # how many frames a "lost" detection is kept alive
SHOW_DEBUG_WINDOW = False     # extra imshow() call costs real time each frame;
                               # turn on only when you need to visually check
                               # what the enhancement pipeline is doing
HAZE_SKIP_THRESHOLD = 0.05    # if estimated haze level is below this, skip the
                               # dehaze step entirely for this frame (saves compute
                               # on clear-air frames, which will be most of them)
DEBUG_PRINT_EVERY_N_FRAMES = 15  # how often to print detection-count debug lines;
                                   # set to 0 to disable debug prints entirely

model = YOLO(MODEL_NAME, task="detect")


# ---------- IMAGE ENHANCEMENT ----------

def enhance_low_light(frame):
    """Boost visibility in dark rooms using CLAHE on the L channel (LAB color space)."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    enhanced = cv2.merge((l_enhanced, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def dehaze(frame, strength=0.7):
    """
    Simple dark-channel-based dehazing to cut through smoke/dust.
    Not a full scientific implementation, but effective and fast enough for real-time use.
    """
    frame_f = frame.astype(np.float32) / 255.0
    dark_channel = np.min(frame_f, axis=2)

    # Estimate atmospheric light from brightest pixels in dark channel
    flat_dark = dark_channel.flatten()
    num_pixels = int(0.001 * flat_dark.shape[0])
    indices = np.argpartition(flat_dark, -max(num_pixels, 1))[-max(num_pixels, 1):]
    atmospheric_light = np.mean(frame_f.reshape(-1, 3)[indices], axis=0)

    # Estimate transmission map
    transmission = 1 - strength * (dark_channel / (np.max(atmospheric_light) + 1e-6))
    transmission = np.clip(transmission, 0.3, 1.0)  # avoid over-darkening

    result = np.zeros_like(frame_f)
    for c in range(3):
        result[:, :, c] = (frame_f[:, :, c] - atmospheric_light[c]) / transmission + atmospheric_light[c]

    result = np.clip(result, 0, 1) * 255
    return result.astype(np.uint8)


def estimate_haze_level(frame):
    """
    Cheap haze estimate: hazy scenes have a washed-out dark channel (low
    contrast, everything shifted toward gray/white). Returns roughly 0 (clear)
    to 1 (heavily hazy). Much cheaper than running full dehaze on every frame.
    """
    small = cv2.resize(frame, (80, 60))  # tiny downsample -- plenty accurate for this estimate
    frame_f = small.astype(np.float32) / 255.0
    dark_channel = np.min(frame_f, axis=2)
    return float(np.mean(dark_channel))


def auto_enhance(frame):
    """Decide enhancement level based on frame brightness/haze, applying only what's needed."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)

    processed = frame.copy()

    # Dark scene -> boost light first
    if brightness < 90:
        processed = enhance_low_light(processed)

    # Only pay the dehaze cost when the scene actually looks hazy
    if estimate_haze_level(processed) > HAZE_SKIP_THRESHOLD:
        processed = dehaze(processed, strength=0.5)

    return processed


# ---------- TEMPORAL TRACKING (keeps partial/flickering detections alive) ----------

def iou(box1, box2):
    """Intersection-over-union between two [x1,y1,x2,y2] boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def containment_ratio(inner, outer):
    """What fraction of `inner` box's area lies inside `outer` box."""
    x1 = max(inner[0], outer[0])
    y1 = max(inner[1], outer[1])
    x2 = min(inner[2], outer[2])
    y2 = min(inner[3], outer[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    inner_area = (inner[2] - inner[0]) * (inner[3] - inner[1])
    if inner_area <= 0:
        return 0.0
    return inter_area / inner_area


def is_plausible_person_box(box, frame_shape, min_area_ratio=0.01, min_aspect=0.15, max_aspect=4.0):
    """
    Sanity check a detected box against implausible size/shape for a person.
    Rejects tiny noise detections (e.g. a shadow or hair clump near frame edge)
    while still allowing genuinely small/distant or partial-body boxes.
    """
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    if w <= 0 or h <= 0:
        return False

    frame_h, frame_w = frame_shape[:2]
    area_ratio = (w * h) / (frame_w * frame_h)
    aspect = w / h

    if area_ratio < min_area_ratio:
        return False
    if aspect < min_aspect or aspect > max_aspect:
        return False
    return True


def merge_overlapping_person_boxes(boxes, containment_threshold=0.85, max_area_ratio_to_merge=0.5):
    """
    Collapse duplicate 'person' detections that are really the same person
    (e.g. a raised arm briefly detected as its own low-confidence 'person'
    box, separate from the main body box). If one box is mostly contained
    inside another AND is substantially smaller than it, keep only the
    larger box.

    The area-ratio check matters: a limb box is typically much smaller than
    the full body box it's part of. Two real people standing close together
    (e.g. one person's raised arm bridging toward another) can produce boxes
    of SIMILAR size where one geometrically contains the other purely by
    coincidence of proximity -- without this check, that wrongly merges two
    real, separate people into one.
    """
    if len(boxes) <= 1:
        return boxes

    def area(b):
        return (b[2] - b[0]) * (b[3] - b[1])

    boxes = sorted(boxes, key=area, reverse=True)
    kept = []

    for box in boxes:
        is_duplicate = False
        for kept_box in kept:
            same_size_class = area(box) / area(kept_box) > max_area_ratio_to_merge
            if same_size_class:
                continue  # too similar in size to be "a limb of that person" -- treat as separate
            if containment_ratio(box, kept_box) > containment_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(box)

    return kept


class SimpleTracker:
    """
    Keeps recently seen detections alive for a few frames, so a person
    briefly obscured by smoke/debris doesn't just disappear from the map.
    Matches new detections to existing tracks by IoU overlap so the same
    person isn't counted as a new track every frame.

    Also requires a track to be seen in several recent frames before it's
    "confirmed" as a real survivor -- this filters out one-off false
    positives (e.g. a hand holding an object briefly misread as a partial
    person) without needing a stricter confidence threshold that would
    also block real partially-occluded survivors.
    """
    def __init__(self, memory_frames=8, iou_threshold=0.3,
                 confirm_hits_needed=3, confirm_window=5):
        self.memory_frames = memory_frames
        self.iou_threshold = iou_threshold
        self.confirm_hits_needed = confirm_hits_needed
        self.confirm_window = confirm_window
        self.tracks = []  # list of dicts: {box, last_seen_frame, hit_history: deque}

    def update(self, boxes, frame_count):
        matched_track_indices = set()
        updated_tracks = []

        for box in boxes:
            best_match_idx = None
            best_iou = self.iou_threshold

            for idx, track in enumerate(self.tracks):
                if idx in matched_track_indices:
                    continue
                score = iou(box, track["box"])
                if score > best_iou:
                    best_iou = score
                    best_match_idx = idx

            if best_match_idx is not None:
                matched_track_indices.add(best_match_idx)
                hit_history = self.tracks[best_match_idx]["hit_history"]
            else:
                hit_history = deque(maxlen=self.confirm_window)

            hit_history.append(True)
            updated_tracks.append({
                "box": box,
                "last_seen_frame": frame_count,
                "hit_history": hit_history,
            })

        MIN_OVERLAP_TO_DISCARD_AS_GHOST = 0.05

        for idx, track in enumerate(self.tracks):
            if idx in matched_track_indices:
                continue

            overlaps_fresh_detection = any(
                iou(track["box"], box) > MIN_OVERLAP_TO_DISCARD_AS_GHOST
                for box in boxes
            )
            if overlaps_fresh_detection:
                continue

            age = frame_count - track["last_seen_frame"]
            if age <= self.memory_frames:
                track["hit_history"].append(False)
                updated_tracks.append(track)

        self.tracks = updated_tracks
        return self.tracks

    def get_confirmed_tracks(self):
        """Only return tracks seen in enough recent frames to trust as real."""
        confirmed = []
        for track in self.tracks:
            hits = sum(track["hit_history"])
            if hits >= self.confirm_hits_needed:
                confirmed.append(track)
        return confirmed


class ThreadedCamera:
    """
    Reads frames from the camera on a background thread so frame capture
    never blocks the main loop while it's busy running inference. Always
    exposes the LATEST available frame -- if the main loop is slower than
    the camera, older unread frames are simply dropped rather than queued
    (queueing would introduce growing lag, which is worse for a live mission).
    """
    def __init__(self, camera_index):
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.lock = threading.Lock()
        self.latest_frame = None
        self.running = False
        self.thread = None

    def isOpened(self):
        return self.cap.isOpened()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return self

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.latest_frame = frame

    def read(self):
        with self.lock:
            if self.latest_frame is None:
                return False, None
            return True, self.latest_frame.copy()

    def release(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        self.cap.release()


# ---------- MAIN LOOP ----------

def main():
    cap = ThreadedCamera(CAMERA_INDEX).start()
    time.sleep(0.5)  # give the capture thread a moment to grab its first frame

    if not cap.isOpened():
        print(f"ERROR: Could not open camera index {CAMERA_INDEX}")
        return

    print("Camera opened. Press 'q' to quit.")
    print(f"Using model: {MODEL_NAME}, confidence threshold: {CONFIDENCE_THRESHOLD}")

    tracker = SimpleTracker(memory_frames=TRACK_MEMORY_FRAMES)
    prev_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue  # threaded camera hasn't produced a frame yet -- don't treat as failure

        frame_count += 1

        # Enhance frame for detection (smoke/dust/low light handling)
        enhanced = auto_enhance(frame)

        # Run detection on the enhanced frame
        results = model(enhanced, classes=[0], conf=CONFIDENCE_THRESHOLD, imgsz=INFERENCE_SIZE,
                         iou=NMS_IOU_THRESHOLD, verbose=False)
        raw_boxes = results[0].boxes.xyxy.cpu().numpy() if len(results[0].boxes) > 0 else []

        # Reject implausibly tiny/odd-shaped detections (likely shadows, hair,
        # or other noise picked up due to the low confidence threshold)
        plausible_boxes = [b for b in raw_boxes if is_plausible_person_box(b, frame.shape)]

        # Merge duplicate detections (e.g. a raised arm detected as its own
        # low-confidence "person", separate from the main body box)
        boxes = merge_overlapping_person_boxes(plausible_boxes, containment_threshold=0.85)

        if DEBUG_PRINT_EVERY_N_FRAMES and frame_count % DEBUG_PRINT_EVERY_N_FRAMES == 0:
            print(f"[DEBUG] Raw: {len(raw_boxes)} -> Plausible: {len(plausible_boxes)} -> After merge: {len(boxes)}")

        # Update tracker (keeps flickering/partial detections alive briefly)
        tracker.update(boxes, frame_count)
        tracks = tracker.get_confirmed_tracks()  # only show tracks seen consistently, not one-off false positives

        # Draw on the ORIGINAL frame (so display looks natural, not overly processed)
        display_frame = frame.copy()
        for track in tracks:
            x1, y1, x2, y2 = map(int, track["box"])
            age = frame_count - track["last_seen_frame"]
            color = (0, 255, 0) if age == 0 else (0, 200, 255)  # yellow-ish if "remembered", not fresh
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
            label = "Survivor" if age == 0 else f"Survivor (tracked, {age}f)"
            cv2.putText(display_frame, label, (x1, max(y1 - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # FPS + count overlay
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Active tracks: {len(tracks)}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("NIDAR AirMouse - Survivor Detection (Enhanced)", display_frame)

        # Optional: view the enhanced frame side-by-side for debugging.
        # Costs real per-frame render time -- keep off (SHOW_DEBUG_WINDOW=False)
        # for max FPS once you've confirmed the enhancement looks right.
        if SHOW_DEBUG_WINDOW:
            cv2.imshow("Enhanced (debug view)", enhanced)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()