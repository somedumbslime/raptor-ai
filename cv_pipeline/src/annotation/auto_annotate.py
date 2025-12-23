"""Автоматическая разметка изображений с использованием предобученной YOLO модели"""

import shutil
from pathlib import Path
from typing import Optional, List, Dict

# numpy импортирован через ultralytics
from ultralytics import YOLO
from loguru import logger
from tqdm import tqdm
from sklearn.model_selection import train_test_split


def auto_annotate(
    images_dir: str,
    output_dir: str,
    pretrained_model: str = "yolo11n.pt",
    confidence_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    target_class: Optional[int] = None,
    class_name: str = "soldier",
    auto_split: bool = True,
    split_ratios: Dict[str, float] = None,
    split_seed: int = 42,
) -> dict:
    """
    Автоматическая разметка изображений с использованием предобученной YOLO модели

    Args:
        images_dir: Путь к папке с изображениями
        output_dir: Путь для сохранения датасета YOLO
        pretrained_model: Путь к предобученной модели YOLO
        confidence_threshold: Порог уверенности для детекций
        iou_threshold: Порог IoU для NMS
        target_class: Индекс класса для фильтрации (None = все классы)
        class_name: Имя класса для сохранения в YOLO формате
        auto_split: Автоматически создавать train/val/test split
        split_ratios: Пропорции разделения {'train': 0.7, 'val': 0.2, 'test': 0.1}
        split_seed: Random seed для разделения

    Returns:
        Словарь со статистикой
    """
    if split_ratios is None:
        split_ratios = {"train": 0.7, "val": 0.2, "test": 0.1}

    images_path = Path(images_dir)
    output_path = Path(output_dir)

    if not images_path.exists():
        raise FileNotFoundError(f"Папка с изображениями не найдена: {images_dir}")

    # Создаем структуру папок для YOLO датасета
    if auto_split:
        train_images_dir = output_path / "train" / "images"
        train_labels_dir = output_path / "train" / "labels"
        val_images_dir = output_path / "val" / "images"
        val_labels_dir = output_path / "val" / "labels"
        test_images_dir = output_path / "test" / "images"
        test_labels_dir = output_path / "test" / "labels"

        for dir_path in [
            train_images_dir,
            train_labels_dir,
            val_images_dir,
            val_labels_dir,
            test_images_dir,
            test_labels_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    else:
        images_output_dir = output_path / "images"
        labels_output_dir = output_path / "labels"
        images_output_dir.mkdir(parents=True, exist_ok=True)
        labels_output_dir.mkdir(parents=True, exist_ok=True)

    # Получаем список изображений
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    image_files = [
        f
        for f in images_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    total_images = len(image_files)
    logger.info(f"Найдено {total_images} изображений для разметки")

    if total_images == 0:
        raise ValueError(f"Изображения не найдены в {images_dir}")

    # Загружаем модель
    logger.info(f"Загрузка модели {pretrained_model}...")
    model = YOLO(pretrained_model)

    # Разделяем датасет, если нужно
    if auto_split:
        # Сначала train/test split
        train_val_files, test_files = train_test_split(
            image_files, test_size=split_ratios["test"], random_state=split_seed
        )

        # Затем train/val split
        train_size = split_ratios["train"] / (
            split_ratios["train"] + split_ratios["val"]
        )
        train_files, val_files = train_test_split(
            train_val_files, train_size=train_size, random_state=split_seed
        )

        splits = {
            "train": (train_files, train_images_dir, train_labels_dir),
            "val": (val_files, val_images_dir, val_labels_dir),
            "test": (test_files, test_images_dir, test_labels_dir),
        }

        logger.info(f"Разделение датасета:")
        logger.info(f"  - Train: {len(train_files)}")
        logger.info(f"  - Val: {len(val_files)}")
        logger.info(f"  - Test: {len(test_files)}")
    else:
        splits = {"all": (image_files, images_output_dir, labels_output_dir)}

    # Статистика
    total_detections = 0
    annotated_images = 0

    # Обрабатываем каждый split
    for split_name, (files, img_dir, lbl_dir) in splits.items():
        logger.info(f"Обработка {split_name} split...")

        for image_file in tqdm(files, desc=f"Разметка {split_name}"):
            try:
                # Выполняем детекцию
                results = model.predict(
                    source=str(image_file),
                    conf=confidence_threshold,
                    iou=iou_threshold,
                    verbose=False,
                )

                # Получаем результаты
                result = results[0]
                boxes = result.boxes

                # Фильтруем по классу, если указан
                if target_class is not None:
                    class_mask = boxes.cls.cpu().numpy() == target_class
                    boxes = boxes[class_mask]

                # Если есть детекции, сохраняем аннотацию
                if len(boxes) > 0:
                    # Получаем размеры изображения
                    img_height, img_width = result.orig_shape

                    # Формируем имя файла для аннотации
                    label_file = lbl_dir / f"{image_file.stem}.txt"

                    # Записываем аннотацию в YOLO формате
                    with open(label_file, "w") as f:
                        for box in boxes:
                            # Получаем координаты bbox в формате xyxy
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                            # Преобразуем в YOLO формат (нормализованные центр и размеры)
                            x_center = ((x1 + x2) / 2) / img_width
                            y_center = ((y1 + y2) / 2) / img_height
                            width = (x2 - x1) / img_width
                            height = (y2 - y1) / img_height

                            # Класс (всегда 0, так как у нас один класс)
                            class_id = 0

                            # Записываем строку: class_id x_center y_center width height
                            f.write(
                                f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                            )

                    # Копируем изображение
                    shutil.copy2(image_file, img_dir / image_file.name)

                    total_detections += len(boxes)
                    annotated_images += 1
                else:
                    # Если детекций нет, не сохраняем изображение (можно изменить поведение)
                    logger.debug(f"Нет детекций в {image_file.name}")

            except Exception as e:
                logger.error(f"Ошибка при обработке {image_file.name}: {e}")
                continue

    # Создаем data.yaml файл
    data_yaml = output_path / "data.yaml"
    with open(data_yaml, "w", encoding="utf-8") as f:
        f.write(f"# YOLO Dataset Configuration\n")
        f.write(f"# Generated by auto_annotate\n\n")
        f.write(f"path: {output_path.absolute()}\n")
        if auto_split:
            f.write(f"train: train/images\n")
            f.write(f"val: val/images\n")
            f.write(f"test: test/images\n")
        else:
            f.write(f"train: images\n")
            f.write(f"val: images\n")
            f.write(f"test: images\n")
        f.write(f"\n")
        f.write(f"# Classes\n")
        f.write(f"nc: 1\n")
        f.write(f"names:\n")
        f.write(f"  - {class_name}\n")

    logger.info(f"Автоматическая разметка завершена:")
    logger.info(f"  - Всего изображений: {total_images}")
    logger.info(f"  - Размечено изображений: {annotated_images}")
    logger.info(f"  - Всего детекций: {total_detections}")
    logger.info(
        f"  - Среднее детекций на изображение: {total_detections / annotated_images if annotated_images > 0 else 0:.2f}"
    )
    logger.info(f"  - Датасет сохранен в: {output_path}")
    logger.info(f"  - Конфигурация: {data_yaml}")

    return {
        "total_images": total_images,
        "annotated_images": annotated_images,
        "total_detections": total_detections,
        "output_dir": str(output_path),
        "data_yaml": str(data_yaml),
    }
