"""
Shared survivor-detection pipeline: image enhancement, YOLO inference config,
duplicate/false-positive filtering, and occlusion-tolerant tracking.
"""

import os
os.environ.setdefault("OMP_NUM_THREADS", str(os.cpu_count()))
os.environ.setdefault("ORT_NUM_THREADS", str(os.cpu_count()))

import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque

# ---- CONFIG ----
CONFIDENCE_THRESHOLD = 0.25
MODEL_NAME = "yolo11s.onnx"
INFERENCE_SIZE = 480
NMS_IOU_THRESHOLD = 0.85
TRACK_MEMORY_FRAMES = 8
HAZE_SKIP_THRESHOLD = 0.05


def load_model():
    return YOLO(MODEL_NAME, task="detect")


def enhance_low_light(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    enhanced = cv2.merge((l_enhanced, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def dehaze(frame, strength=0.7):
    frame_f = frame.astype(np.float32) / 255.0
    dark_channel = np.min(frame_f, axis=2)

    flat_dark = dark_channel.flatten()
    num_pixels = int(0.001 * flat_dark.shape[0])
    indices = np.argpartition(flat_dark, -max(num_pixels, 1))[-max(num_pixels, 1):]
    atmospheric_light = np.mean(frame_f.reshape(-1, 3)[indices], axis=0)

    transmission = 1 - strength * (dark_channel / (np.max(atmospheric_light) + 1e-6))
    transmission = np.clip(transmission, 0.3, 1.0)

    result = np.zeros_like(frame_f)
    for c in range(3):
        result[:, :, c] = (frame_f[:, :, c] - atmospheric_light[c]) / transmission + atmospheric_light[c]

    result = np.clip(result, 0, 1) * 255
    return result.astype(np.uint8)


def estimate_haze_level(frame):
    small = cv2.resize(frame, (80, 60))
    frame_f = small.astype(np.float32) / 255.0
    dark_channel = np.min(frame_f, axis=2)
    return float(np.mean(dark_channel))


def auto_enhance(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)

    processed = frame.copy()

    if brightness < 90:
        processed = enhance_low_light(processed)

    if estimate_haze_level(processed) > HAZE_SKIP_THRESHOLD:
        processed = dehaze(processed, strength=0.5)

    return processed


def iou(box1, box2):
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
                continue
            if containment_ratio(box, kept_box) > containment_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(box)

    return kept


class SimpleTracker:
    def __init__(self, memory_frames=TRACK_MEMORY_FRAMES, iou_threshold=0.3,
                 confirm_hits_needed=3, confirm_window=5):
        self.memory_frames = memory_frames
        self.iou_threshold = iou_threshold
        self.confirm_hits_needed = confirm_hits_needed
        self.confirm_window = confirm_window
        self.tracks = []

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
        confirmed = []
        for track in self.tracks:
            hits = sum(track["hit_history"])
            if hits >= self.confirm_hits_needed:
                confirmed.append(track)
        return confirmed


def process_frame(model, frame, frame_count, tracker):
    enhanced = auto_enhance(frame)

    results = model(enhanced, classes=[0], conf=CONFIDENCE_THRESHOLD, imgsz=INFERENCE_SIZE,
                     iou=NMS_IOU_THRESHOLD, verbose=False)
    raw_boxes = results[0].boxes.xyxy.cpu().numpy() if len(results[0].boxes) > 0 else []

    plausible_boxes = [b for b in raw_boxes if is_plausible_person_box(b, frame.shape)]
    boxes = merge_overlapping_person_boxes(plausible_boxes)

    tracker.update(boxes, frame_count)
    confirmed_tracks = tracker.get_confirmed_tracks()

    return confirmed_tracks, enhanced


def draw_tracks(frame, tracks, frame_count):
    display_frame = frame.copy()
    for track in tracks:
        x1, y1, x2, y2 = map(int, track["box"])
        age = frame_count - track["last_seen_frame"]
        color = (0, 255, 0) if age == 0 else (0, 200, 255)
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        label = "Survivor" if age == 0 else f"Survivor (tracked, {age}f)"
        cv2.putText(display_frame, label, (x1, max(y1 - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return display_frame