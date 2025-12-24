import cv2
from ultralytics import YOLO
import random
import os
import yaml


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

CONFIG_PATH = "config/config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)


MODEL_PATH = data["paths"]["models_dir"]
MODEL_NAME = data["predict"]["model"]

TEST_PATH = data["paths"]["test_video_dir"]

test_video_list = [
    [vid, f"result_{vid}"] for vid in os.listdir(TEST_PATH) if str(vid).endswith(".mp4")
]


RESULT_FOLDER = data["paths"]["test_video_results"]


CONF = data["predict"]["conf"]
IOU = data["predict"]["iou"]
IMAGE_SIZE = data["predict"]["image_size"]
TRACKER = data["predict"]["tracker"]
DEVICE = data["predict"]["device"]

MODEL = YOLO(f"{MODEL_PATH}/{MODEL_NAME}")
MODEL.to(DEVICE)
MODEL.fuse()


def process_video_with_tracking(
    model,
    input_video_path,
    show_video=True,
    save_video=False,
    output_video_path=f"test_video_results",
    conf=0.5,
    iou=0.5,
    imgsz=640,
    tracker="bytetrack.yaml",
):

    process_video_list = [
        [vid, f"result_{vid}"]
        for vid in os.listdir(input_video_path)
        if str(vid).lower().endswith(".mp4")
    ]

    for vid, result_name in process_video_list:
        print(f"Process video '{vid}'")
        # Open the input video file
        cap = cv2.VideoCapture(f"{input_video_path}/{vid}")

        if not cap.isOpened():
            raise Exception("Error: Could not open video file.")

        # Get input video frame rate and dimensions
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the output video writer
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(
                f"{output_video_path}/{result_name}",
                fourcc,
                fps,
                (frame_width, frame_height),
            )

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            results = model.track(
                frame,
                iou=float(iou),
                conf=float(conf),
                persist=True,
                imgsz=int(imgsz),
                verbose=False,
                tracker=tracker,
            )

            if (
                results[0].boxes.id != None
            ):  # this will ensure that id is not None -> exist tracks
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                ids = results[0].boxes.id.cpu().numpy().astype(int)

                confidences = results[0].boxes.conf.cpu().numpy()

                for box, id, conf in zip(boxes, ids, confidences):
                    # Generate a random color for each object based on its ID
                    random.seed(int(id))
                    color = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                    )

                    cv2.rectangle(
                        frame,
                        (box[0], box[1]),
                        (
                            box[2],
                            box[3],
                        ),
                        color,
                        2,
                    )
                    cv2.putText(
                        frame,
                        f"Id {id} | {conf:.2f}",
                        (box[0], box[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),
                        2,
                    )

            if save_video:
                out.write(frame)

            if show_video:
                frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
                cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        print(f"Video '{vid}' was successfully processed.")

        # Release the input video capture and output video writer
        cap.release()
        if save_video:
            out.release()

        # Close all OpenCV windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Example usage:
    print(f"Video folder: {os.listdir(TEST_PATH)}")

    process_video_with_tracking(
        model=MODEL,
        input_video_path=TEST_PATH,
        show_video=True,
        save_video=True,
        output_video_path=RESULT_FOLDER,
        conf=CONF,
        iou=IOU,
        imgsz=IMAGE_SIZE,
        tracker=TRACKER,
    )
