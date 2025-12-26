import cv2
import random
import os
import yaml
from ultralytics import YOLO


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# --- КОНСТАНТЫ ---
DEFAULT_CONFIG = "config/config.yaml"

# --- ФУНКЦИИ ЗАГРУЗКИ ---


def load_config(path=DEFAULT_CONFIG):
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def init_model(model_path, device="cpu"):
    """Инициализация модели."""
    model = YOLO(model_path)
    model.to(device)
    model.fuse()
    return model


# --- ОСНОВНАЯ ЛОГИКА ---


def process_video_with_tracking(
    model,
    input_video_path,
    output_video_path,
    show_video=False,
    save_video=True,
    conf=0.5,
    iou=0.5,
    imgsz=640,
    tracker="bytetrack.yaml",
):
    """Функция обработки. Теперь она принимает готовый объект модели и пути."""

    # Создаем папку для результатов, если её нет
    os.makedirs(output_video_path, exist_ok=True)

    # Список видео для обработки
    video_files = [
        f for f in os.listdir(input_video_path) if f.lower().endswith(".mp4")
    ]

    for vid in video_files:
        print(f"Обработка видео: '{vid}'")
        cap = cv2.VideoCapture(os.path.join(input_video_path, vid))

        if not cap.isOpened():
            print(f"Ошибка: Не удалось открыть {vid}")
            continue

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = None
        if save_video:
            result_path = os.path.join(output_video_path, f"result_{vid}")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Инференс
            results = model.track(
                frame,
                iou=float(iou),
                conf=float(conf),
                persist=True,
                imgsz=int(imgsz),
                verbose=False,
                tracker=tracker,
            )

            # Отрисовка
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                ids = results[0].boxes.id.cpu().numpy().astype(int)
                confidences = results[0].boxes.conf.cpu().numpy()

                for box, id, cnf in zip(boxes, ids, confidences):
                    random.seed(int(id))
                    color = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                    )

                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
                    cv2.putText(
                        frame,
                        f"ID {id} | {cnf:.2f}",
                        (box[0], box[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),
                        2,
                    )

            if save_video:
                out.write(frame)

            if show_video:
                cv2.imshow("Tracking", cv2.resize(frame, (0, 0), fx=0.5, fy=0.5))
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        cap.release()
        if out:
            out.release()
        print(f"Видео '{vid}' успешно обработано.")

    cv2.destroyAllWindows()


# --- ТОЧКА ВХОДА ---

if __name__ == "__main__":
    # 1. Загружаем конфиг
    cfg = load_config()

    # 2. Собираем пути
    m_path = os.path.join(cfg["paths"]["models_dir"], cfg["predict"]["model"])

    # 3. Инициализируем модель (только при прямом запуске!)
    yolo_model = init_model(m_path, device=cfg["predict"]["device"])

    # 4. Запускаем процесс
    process_video_with_tracking(
        model=yolo_model,
        input_video_path=cfg["paths"]["test_video_dir"],
        output_video_path=cfg["paths"]["test_video_results"],
        show_video=True,
        save_video=True,
        conf=cfg["predict"]["conf"],
        iou=cfg["predict"]["iou"],
        imgsz=cfg["predict"]["image_size"],
        tracker=cfg["predict"]["tracker"],
    )
