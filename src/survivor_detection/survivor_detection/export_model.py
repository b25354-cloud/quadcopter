from ultralytics import YOLO

# YOLO11 is Ultralytics' newer generation -- better accuracy AND speed than
# the equivalent YOLOv8 size class. "s" (small) is the sweet spot for CPU.
print("Downloading YOLO11s...")
model = YOLO("yolo11s.pt")

print("Exporting to ONNX format for faster CPU inference...")
# imgsz=480 (down from default 640) trades a small amount of accuracy for a
# real FPS gain -- reasonable for typical drone-to-survivor distances.
model.export(format="onnx", imgsz=480, simplify=True)

print("\nDone. You should now have a 'yolo11s.onnx' file in this folder.")