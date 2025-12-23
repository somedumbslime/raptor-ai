# cv_tgbot/detect.py
import os
import cv2
import glob
import shutil
import onnxruntime as ort
import numpy as np
import time


class ONNXDetector:
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 МБ

    def __init__(self, model_path):
        self.model_path = model_path

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

    def run_on_image(
        self,
        input_image_path,
        output_image_path,
        confidence_threshold=0.32,
        iou_threshold=0.5,
    ):
        if os.path.getsize(input_image_path) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Размер файла превышает {self.MAX_FILE_SIZE // (1024*1024)} МБ"
            )
        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if "CUDAExecutionProvider" in ort.get_available_providers()
            else ["CPUExecutionProvider"]
        )
        session = ort.InferenceSession(self.model_path, providers=providers)
        input_name = session.get_inputs()[0].name
        img = cv2.imread(input_image_path)
        orig = img.copy()
        height, width = img.shape[:2]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (640, 640))
        img_input = img_resized.astype(np.float32) / 255.0
        img_input = np.transpose(img_input, (2, 0, 1))
        img_input = np.expand_dims(img_input, axis=0)
        outputs = session.run(None, {input_name: img_input})
        pred = outputs[0][0]
        boxes, scores, class_ids = [], [], []
        for det in pred:
            conf = det[4]
            if conf < confidence_threshold:
                continue
            x1, y1, x2, y2 = det[0:4]
            cls = int(det[5]) if det.shape[0] > 5 else 0
            x1 = int(x1 / 640 * width)
            y1 = int(y1 / 640 * height)
            x2 = int(x2 / 640 * width)
            y2 = int(y2 / 640 * height)
            boxes.append([x1, y1, x2, y2])
            scores.append(float(conf))
            class_ids.append(cls)
        idxs = cv2.dnn.NMSBoxes(boxes, scores, confidence_threshold, iou_threshold)
        for i in idxs.flatten():
            x1, y1, x2, y2 = boxes[i]
            cv2.rectangle(orig, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                orig,
                str(class_ids[i]),
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )
        cv2.imwrite(output_image_path, orig)

    def run_on_video(
        self,
        input_video_path,
        output_video_path,
        confidence_threshold=0.32,
        iou_threshold=0.5,
        batch_size=16,
        compress_if_larger_than=None,  # в байтах, если None - не сжимать
    ):
        if os.path.getsize(input_video_path) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Размер файла превышает {self.MAX_FILE_SIZE // (1024*1024)} МБ"
            )
        self._process_video(
            input_video_path,
            output_video_path,
            confidence_threshold,
            iou_threshold,
            batch_size,
        )
        # Если нужно, сжимаем видео после обработки
        if (
            compress_if_larger_than is not None
            and os.path.getsize(output_video_path) > compress_if_larger_than
        ):
            compressed_path = output_video_path.replace(".mp4", "_compressed.mp4")
            self.compress_video(output_video_path, compressed_path)
            shutil.move(compressed_path, output_video_path)

    def _process_video(
        self,
        input_video_path,
        output_video_path,
        confidence_threshold=0.32,
        iou_threshold=0.5,
        batch_size=16,
    ):
        try:
            providers = (
                ["CUDAExecutionProvider", "CPUExecutionProvider"]
                if "CUDAExecutionProvider" in ort.get_available_providers()
                else ["CPUExecutionProvider"]
            )
            session = ort.InferenceSession(self.model_path, providers=providers)
            input_name = session.get_inputs()[0].name
            cap = cv2.VideoCapture(input_video_path)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
            frames = []
            orig_frames = []
            infer_times = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                orig_frames.append(frame.copy())
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (640, 640))
                img = img.astype(np.float32) / 255.0
                img = np.transpose(img, (2, 0, 1))
                frames.append(img)
                if len(frames) == batch_size:
                    batch = np.stack(frames, axis=0)
                    start_time = time.time()
                    outputs = session.run(None, {input_name: batch})
                    infer_time = (time.time() - start_time) * 1000 / batch_size
                    infer_times.extend([infer_time] * batch_size)
                    pred = outputs[0]
                    for idx, dets in enumerate(pred):
                        frame = orig_frames[idx]
                        boxes, scores, class_ids = [], [], []
                        for det in dets:
                            conf = det[4]
                            if conf < confidence_threshold:
                                continue
                            x1, y1, x2, y2 = det[0:4]
                            cls = int(det[5]) if det.shape[0] > 5 else 0
                            x1 = int(x1 / 640 * width)
                            y1 = int(y1 / 640 * height)
                            x2 = int(x2 / 640 * width)
                            y2 = int(y2 / 640 * height)
                            boxes.append([x1, y1, x2, y2])
                            scores.append(float(conf))
                            class_ids.append(cls)
                        idxs = cv2.dnn.NMSBoxes(
                            boxes, scores, confidence_threshold, iou_threshold
                        )
                        for i in idxs.flatten():
                            x1, y1, x2, y2 = boxes[i]
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(
                                frame,
                                str(class_ids[i]),
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 255, 0),
                                2,
                            )
                        out.write(frame)
                    frames = []
                    orig_frames = []
            # Обработка оставшихся кадров (если их < batch_size)
            if frames:
                pad = batch_size - len(frames)
                for _ in range(pad):
                    frames.append(frames[-1])
                    orig_frames.append(orig_frames[-1])
                batch = np.stack(frames, axis=0)
                start_time = time.time()
                outputs = session.run(None, {input_name: batch})
                infer_time = (time.time() - start_time) * 1000 / batch_size
                infer_times.extend([infer_time] * len(frames))
                pred = outputs[0]
                for idx in range(len(frames) - pad):
                    dets = pred[idx]
                    frame = orig_frames[idx]
                    boxes, scores, class_ids = [], [], []
                    for det in dets:
                        conf = det[4]
                        if conf < confidence_threshold:
                            continue
                        x1, y1, x2, y2 = det[0:4]
                        cls = int(det[5]) if det.shape[0] > 5 else 0
                        x1 = int(x1 / 640 * width)
                        y1 = int(y1 / 640 * height)
                        x2 = int(x2 / 640 * width)
                        y2 = int(y2 / 640 * height)
                        boxes.append([x1, y1, x2, y2])
                        scores.append(float(conf))
                        class_ids.append(cls)
                    idxs = cv2.dnn.NMSBoxes(
                        boxes, scores, confidence_threshold, iou_threshold
                    )
                    for i in idxs.flatten():
                        x1, y1, x2, y2 = boxes[i]
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            str(class_ids[i]),
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2,
                        )
                    out.write(frame)
            cap.release()
            out.release()
            if infer_times:
                print(
                    f"Среднее время инференса на кадр: {np.mean(infer_times):.2f} мс (batch={batch_size})"
                )
            print(f"Размеченное видео сохранено в: {output_video_path}")
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
            _process_video(input_vid, output_vid, model_p)
            print("Тестирование detect.py завершено успешно.")
        except Exception as e:
            print(f"Ошибка при тестировании detect.py: {e}")

        # Удаление временного тестового файла, если создавали
        # if os.path.exists(dummy_video_path):
        #     os.remove(dummy_video_path)
        # if os.path.exists(output_vid):
        #     os.remove(output_vid)
