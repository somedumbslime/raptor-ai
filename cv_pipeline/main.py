"""Главный скрипт для запуска End-to-End Pipeline обучения YOLO модели"""

import argparse
import sys
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.config_loader import load_config, validate_config, get_path
from src.data_preparation.video_to_frames import extract_frames, check_ffmpeg
from src.data_preparation.remove_duplicates import remove_duplicates
from src.annotation.auto_annotate import auto_annotate
from src.training.train_yolo import train_yolo_with_mlflow
from loguru import logger


def run_data_preparation(config: dict, base_path: Path):
    """Запуск процесса подготовки данных"""
    logger.info("=" * 80)
    logger.info("ПРОЦЕСС 1: ПОДГОТОВКА ДАННЫХ")
    logger.info("=" * 80)

    # Проверяем наличие ffmpeg
    if not check_ffmpeg():
        logger.error("FFmpeg не найден! Установите FFmpeg для обработки видео.")
        logger.error("Скачать можно здесь: https://ffmpeg.org/download.html")
        raise RuntimeError("FFmpeg не установлен")

    # Получаем пути
    video_dir = get_path(config, "paths.video_dir", base_path)
    frames_dir = get_path(config, "paths.frames_dir", base_path)
    clean_frames_dir = get_path(config, "paths.clean_frames_dir", base_path)

    # Параметры извлечения кадров
    video_config = config["data_preparation"]["video_processing"]
    fps = video_config.get("fps", 0.33)
    video_formats = video_config.get("video_formats", [".mp4", ".mov", ".avi", ".mkv"])
    jpeg_quality = video_config.get("jpeg_quality", 95)

    # Параметры удаления дубликатов
    dedup_config = config["data_preparation"]["deduplication"]
    hash_threshold = dedup_config.get("hash_threshold", 5)
    hash_method = dedup_config.get("hash_method", "phash")
    min_image_size = dedup_config.get("min_image_size", 32)

    # Шаг 1: Извлечение кадров из видео
    logger.info("Шаг 1.1: Извлечение кадров из видео...")
    frames_stats = extract_frames(
        video_dir=str(video_dir),
        output_dir=str(frames_dir),
        fps=fps,
        video_formats=video_formats,
        jpeg_quality=jpeg_quality,
    )

    # Шаг 2: Удаление дубликатов
    logger.info("Шаг 1.2: Удаление дубликатов...")
    dedup_stats = remove_duplicates(
        input_dir=str(frames_dir),
        output_dir=str(clean_frames_dir),
        hash_threshold=hash_threshold,
        hash_method=hash_method,
        min_image_size=min_image_size,
    )

    logger.info("Процесс подготовки данных завершен!")
    return {
        "frames_stats": frames_stats,
        "dedup_stats": dedup_stats,
        "clean_frames_dir": clean_frames_dir,
    }


def run_annotation(config: dict, base_path: Path, clean_frames_dir: Path):
    """Запуск процесса автоматической разметки"""
    logger.info("=" * 80)
    logger.info("ПРОЦЕСС 2: АВТОМАТИЧЕСКАЯ РАЗМЕТКА")
    logger.info("=" * 80)

    # Получаем пути
    annotations_dir = get_path(config, "paths.annotations_dir", base_path)
    dataset_dir = get_path(config, "paths.dataset_dir", base_path)

    # Параметры разметки
    ann_config = config["annotation"]
    pretrained_model = ann_config.get("pretrained_model", "yolo11n.pt")
    confidence_threshold = ann_config.get("confidence_threshold", 0.25)
    iou_threshold = ann_config.get("iou_threshold", 0.45)
    target_class = ann_config.get("target_class", 0)
    class_name = ann_config.get("class_name", "soldier")
    auto_split = ann_config.get("auto_split", True)
    split_ratios = ann_config.get(
        "split_ratios", {"train": 0.7, "val": 0.2, "test": 0.1}
    )
    split_seed = ann_config.get("split_seed", 42)

    # Запускаем автоматическую разметку
    annotation_stats = auto_annotate(
        images_dir=str(clean_frames_dir),
        output_dir=str(dataset_dir),
        pretrained_model=pretrained_model,
        confidence_threshold=confidence_threshold,
        iou_threshold=iou_threshold,
        target_class=target_class if target_class is not None else None,
        class_name=class_name,
        auto_split=auto_split,
        split_ratios=split_ratios,
        split_seed=split_seed,
    )

    logger.info("Процесс автоматической разметки завершен!")
    return annotation_stats


def run_training(config: dict, base_path: Path, dataset_dir: Path):
    """Запуск процесса обучения"""
    logger.info("=" * 80)
    logger.info("ПРОЦЕСС 3: ОБУЧЕНИЕ YOLO МОДЕЛИ")
    logger.info("=" * 80)

    # Получаем пути
    output_dir = get_path(config, "paths.output_dir", base_path)
    data_yaml = Path(dataset_dir) / "data.yaml"

    if not data_yaml.exists():
        raise FileNotFoundError(f"Файл конфигурации датасета не найден: {data_yaml}")

    # Получаем конфигурацию обучения
    # Передаем весь config, чтобы функция могла получить доступ к paths
    full_config = {**config["training"], "paths": config.get("paths", {})}

    # Запускаем обучение
    training_results = train_yolo_with_mlflow(
        config=full_config,
        data_yaml=str(data_yaml),
        output_dir=str(output_dir),
        base_path=base_path,
    )

    logger.info("Процесс обучения завершен!")
    return training_results


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="End-to-End Pipeline для обучения YOLO модели детекции солдат"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Путь к файлу конфигурации",
    )
    parser.add_argument(
        "--stage",
        type=str,
        choices=["all", "data_preparation", "annotation", "training"],
        default="all",
        help="Этап pipeline для запуска",
    )
    parser.add_argument(
        "--log-file", type=str, default=None, help="Путь к файлу для сохранения логов"
    )

    args = parser.parse_args()

    # Загружаем конфигурацию
    config_path = Path(__file__).parent / args.config
    config = load_config(str(config_path))
    validate_config(config)

    # Настраиваем логирование
    log_level = config.get("general", {}).get("log_level", "INFO")
    setup_logger(log_level=log_level, log_file=args.log_file)

    # Базовый путь проекта
    base_path = Path(__file__).parent

    logger.info("=" * 80)
    logger.info("ЗАПУСК END-TO-END PIPELINE ОБУЧЕНИЯ YOLO МОДЕЛИ")
    logger.info("=" * 80)
    logger.info(f"Конфигурация: {config_path}")
    logger.info(f"Этап: {args.stage}")

    try:
        # Процесс 1: Подготовка данных
        if args.stage in ["all", "data_preparation"]:
            prep_results = run_data_preparation(config, base_path)
            clean_frames_dir = prep_results["clean_frames_dir"]
        else:
            # Если пропускаем подготовку, используем существующую папку
            clean_frames_dir = get_path(config, "paths.clean_frames_dir", base_path)
            if not clean_frames_dir.exists():
                logger.warning(
                    f"Папка с очищенными кадрами не найдена: {clean_frames_dir}"
                )
                logger.warning(
                    "Пропущен процесс подготовки данных. Убедитесь, что кадры уже готовы."
                )

        # Процесс 2: Автоматическая разметка
        if args.stage in ["all", "annotation"]:
            ann_results = run_annotation(config, base_path, clean_frames_dir)
            dataset_dir = Path(ann_results["output_dir"])
        else:
            # Если пропускаем разметку, используем существующий датасет
            dataset_dir = get_path(config, "paths.dataset_dir", base_path)
            if not dataset_dir.exists():
                logger.warning(f"Папка с датасетом не найдена: {dataset_dir}")
                logger.warning(
                    "Пропущен процесс разметки. Убедитесь, что датасет уже готов."
                )

        # Процесс 3: Обучение
        if args.stage in ["all", "training"]:
            train_results = run_training(config, base_path, dataset_dir)
            logger.info("=" * 80)
            logger.info("PIPELINE ЗАВЕРШЕН УСПЕШНО!")
            logger.info("=" * 80)
            logger.info(f"Лучшая модель: {train_results.get('best_model_path', 'N/A')}")
            logger.info(f"MLflow Run ID: {train_results.get('run_id', 'N/A')}")
            logger.info(
                f"Для просмотра MLflow: mlflow ui --backend-store-uri {train_results.get('mlflow_uri', 'runs/mlflow')}"
            )

        logger.info("Все процессы завершены успешно!")

    except Exception as e:
        logger.error(f"Ошибка при выполнении pipeline: {e}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
