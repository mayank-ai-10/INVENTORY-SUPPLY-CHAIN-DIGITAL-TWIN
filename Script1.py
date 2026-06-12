import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open video
cap = cv2.VideoCapture("Video2.mp4")

# Video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output_boxes.mp4", fourcc, fps, (width, height))

# Store unique IDs
counted_ids = set()

box_total = 0

while True:

    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True)

    annotated_frame = results[0].plot()

    if results[0].boxes.id is not None:

        boxes = results[0].boxes
        ids = boxes.id.int().cpu().tolist()
        classes = boxes.cls.cpu().tolist()
        xyxy = boxes.xyxy.cpu().tolist()

        for obj_id, cls, box in zip(ids, classes, xyxy):

            x1, y1, x2, y2 = box
            width_box = x2 - x1
            height_box = y2 - y1
            area = width_box * height_box

            label = model.names[int(cls)]

            # Detect rectangular package-like objects
            if area > 5000:

                if obj_id not in counted_ids:
                    counted_ids.add(obj_id)
                    box_total += 1

    cv2.putText(
        annotated_frame,
        f"Boxes: {box_total}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    out.write(annotated_frame)

cap.release()
out.release()

print("\nProcessing Complete")
print("Total Boxes Detected:", box_total)
print("Output saved as: output_boxes.mp4")