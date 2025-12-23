# cv_tgbot/detect.py
import os
from ultralytics import YOLO
import cv2
import glob
import shutil


class PTDetector:
    MAX_FILE_SIZE = 49 * 1024 * 1024  # 49 МБ
    CONFIDENCE = 0.32
    IOU = 0.5
    DEVICE = "cuda"

    def __init__(self, model_path, confidence=CONFIDENCE, iou=IOU, device=DEVICE):
        self.model_path = model_path
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.iou = iou
        self.device = device

    @staticmethod
    def compress_video(input_path, output_path, target_bitrate="1M"):
        import subprocess

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-b:v",
            target_bitrate,
            "-bufsize",
            target_bitrate,
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            output_path,
        ]
        subprocess.run(cmd, check=True)

    @staticmethod
    def convert_avi_to_mp4(input_path, output_path):
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        cap.release()
        out.release()

    def run_on_image(
        self,
        input_image_path,
        output_image_path,
    ):
        if os.path.getsize(input_image_path) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Размер файла превышает {self.MAX_FILE_SIZE // (1024*1024)} МБ"
            )
        try:
            results = self.model.predict(
                source=input_image_path,
                conf=self.confidence,
                iou=self.iou,
                save=True,
                project=os.path.dirname(output_image_path),
                name=os.path.splitext(os.path.basename(output_image_path))[0],
                exist_ok=True,
                device=self.device,
            )
            save_dir = results[0].save_dir
            output_basename = os.path.splitext(os.path.basename(input_image_path))[0]
            found_files = []
            for ext in [".jpg", ".jpeg", ".png"]:
                candidate = os.path.join(save_dir, output_basename + ext)
                if os.path.exists(candidate):
                    found_files.append(candidate)
            if found_files:
                os.rename(found_files[0], output_image_path)
            else:
                raise FileNotFoundError(
                    f"Размеченное изображение не найдено после инференса."
                )
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            raise

    def run_on_video(
        self,
        input_video_path,
        output_video_path,
    ):
        if os.path.getsize(input_video_path) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Размер файла превышает {self.MAX_FILE_SIZE // (1024*1024)} МБ"
            )
        try:
            results = self.model.track(
                source=input_video_path,
                conf=self.confidence,
                iou=self.iou,
                tracker="bytetrack.yaml",
                save=True,
                project=os.path.dirname(output_video_path),
                name=os.path.splitext(os.path.basename(output_video_path))[0],
                exist_ok=True,
                device=self.device,
            )
            save_dir = results[0].save_dir
            output_basename = os.path.splitext(os.path.basename(input_video_path))[0]
            video_patterns = [f"{output_basename}.*"]
            found_files = []
            for pattern in video_patterns:
                found_files.extend(glob.glob(os.path.join(save_dir, pattern)))
            found_files = [
                f
                for f in found_files
                if os.path.splitext(f)[1].lower()
                in [".avi", ".mp4", ".mov", ".mkv", ".wmv"]
            ]
            if found_files:
                actual_output_video_path = found_files[0]
                ext = os.path.splitext(actual_output_video_path)[1].lower()
                if ext == ".avi":
                    self.convert_avi_to_mp4(actual_output_video_path, output_video_path)
                    os.remove(actual_output_video_path)
                else:
                    os.rename(actual_output_video_path, output_video_path)
            else:
                raise FileNotFoundError(
                    f"Размеченное видео не найдено после инференса."
                )
            if os.path.getsize(output_video_path) > self.MAX_FILE_SIZE:
                compressed_path = output_video_path.replace(".mp4", "_compressed.mp4")
                self.compress_video(output_video_path, compressed_path)
                shutil.move(compressed_path, output_video_path)
        except Exception as e:
            print(f"Ошибка при обработке видео: {e}")
            raise


if __name__ == "__main__":
    # Пример использования для тестирования detect.py
    # Убедитесь, что у вас есть test_video.mp4 и модель в cv_tgbot/model/

    # Создайте временный тестовый видеофайл или укажите существующий
    # import cv2
    # import numpy as np
    # dummy_video_path = "temp_test_video.mp4"
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter(dummy_video_path, fourcc, 20.0, (640, 480))
    # for _ in range(50):
    #     frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    #     out.write(frame)
    # out.release()

    input_vid = "video_source_2.mp4"  # Замените на путь к вашему тестовому видео
    output_vid = "output_test_video.mp4"
    model_p = "model/model_5783f.pt"  # Путь к вашей модели

    # Создаем папку 'runs/detect' если ее нет, ultralytics создаст ее сам, но для тестов полезно
    os.makedirs(os.path.dirname(output_vid), exist_ok=True)

    print(f"Тестирование detect.py с моделью: {model_p}")
    print(f"Входное видео: {input_vid}")
    print(f"Выходное видео: {output_vid}")

    try:
        detector = PTDetector(model_p)
        detector.run_on_video(input_vid, output_vid)
        print("Тестирование detect.py завершено успешно.")
    except Exception as e:
        print(f"Ошибка при тестировании detect.py: {e}")

    # Удаление временного тестового файла, если создавали
    # if os.path.exists(dummy_video_path):
    #     os.remove(dummy_video_path)
    # if os.path.exists(output_vid):
    #     os.remove(output_vid)
