"""Авторазметка изображений простой логикой."""

from pathlib import Path
from typing import Dict, Optional
import shutil

from loguru import logger
from ultralytics import YOLO
from tqdm import tqdm


class ImageAnnotationPipeline:
    """Авторазметка через предобученную YOLO (минимум настроек)."""

    def __init__(self, config: dict):
        self.config = config.get("annotation", {})

    def _write_label(self, label_path: Path, boxes, img_w: int, img_h: int):
        with open(label_path, "w", encoding="utf-8") as f:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x_center = ((x1 + x2) / 2) / img_w
                y_center = ((y1 + y2) / 2) / img_h
                w = (x2 - x1) / img_w
                h = (y2 - y1) / img_h
                f.write(f"0 {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

    def run(self, images_dir: Path, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        images_out = output_dir / "images"
        labels_out = output_dir / "labels"
        images_out.mkdir(parents=True, exist_ok=True)
        labels_out.mkdir(parents=True, exist_ok=True)

        image_files = [p for p in images_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        if not image_files:
            raise FileNotFoundError(f"Нет изображений для разметки в {images_dir}")

        model_name = self.config.get("pretrained_model", "yolo11n.pt")
        conf = float(self.config.get("confidence_threshold", 0.25))
        iou = float(self.config.get("iou_threshold", 0.45))
        target_class = self.config.get("target_class", None)

        logger.info(f"Загружаем модель {model_name}")
        model = YOLO(model_name)

        for img_path in tqdm(image_files, desc="Авторазметка"):
            results = model.predict(source=str(img_path), conf=conf, iou=iou, verbose=False)
            result = results[0]
            boxes = result.boxes

            if target_class is not None:
                import numpy as np

                mask = boxes.cls.cpu().numpy() == target_class
                boxes = boxes[mask]

            if len(boxes) == 0:
                continue

            # Копируем картинку и пишем метку
            shutil.copy2(img_path, images_out / img_path.name)
            img_h, img_w = result.orig_shape
            label_path = labels_out / f"{img_path.stem}.txt"
            self._write_label(label_path, boxes, img_w, img_h)

        # Создаем простой data.yaml
        data_yaml = output_dir / "data.yaml"
        with open(data_yaml, "w", encoding="utf-8") as f:
            f.write(f"path: {output_dir.absolute()}\n")
            f.write("train: images\n")
            f.write("val: images\n")
            f.write("test: images\n")
            f.write("nc: 1\n")
            f.write("names: [soldier]\n")

        logger.info(f"Разметка сохранена в {output_dir}")

