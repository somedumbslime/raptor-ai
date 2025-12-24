"""Простой пайплайн в стиле Junior ML Engineer.

Логика разбита на маленькие классы:
- ImagePreprocessPipeline  – кадры из видео + удаление дублей
- ImageAnnotationPipeline  – автодетекция и запись YOLO-формата
- DatasetSplitPipeline     – разбиение на train/val/test
- YoloTrainPipeline        – обучение YOLO через обычный PyTorch DataLoader

Стадии выбираются аргументом --stage: all | preprocess | annotate | split | train
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger

from src.utils.logger import setup_logger
from src.utils.config_loader import load_config, validate_config, get_path
from src.pipelines.preprocess import ImagePreprocessPipeline
from src.pipelines.annotate import ImageAnnotationPipeline
from src.pipelines.split import DatasetSplitPipeline
from src.pipelines.train import YoloTrainPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Простой end-to-end pipeline обучения YOLO (junior style)"
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
        choices=["all", "preprocess", "annotate", "split", "train"],
        default="all",
        help="Какие шаги выполнять",
    )
    parser.add_argument(
        "--log-file", type=str, default=None, help="Путь к файлу для логов"
    )
    parser.add_argument(
        "--finetune",
        type=str,
        choices=["yes", "no"],
        default="no",
        help="Если yes — загружаем модель из config.training.finetune_model",
    )

    args = parser.parse_args()

    config_path = Path(__file__).parent / args.config
    config = load_config(str(config_path))
    validate_config(config)

    log_level = config.get("general", {}).get("log_level", "INFO")
    setup_logger(log_level=log_level, log_file=args.log_file)

    base_path = Path(__file__).parent
    logger.info("=" * 80)
    logger.info("СТАРТ ПРОСТОГО PIPELINE")
    logger.info(f"Конфиг: {config_path}")
    logger.info(f"Стадия: {args.stage}")
    logger.info("=" * 80)

    # Подготовка путей
    video_dir = get_path(config, "paths.video_dir", base_path)
    frames_dir = get_path(config, "paths.frames_dir", base_path)
    clean_frames_dir = get_path(config, "paths.clean_frames_dir", base_path)
    dataset_dir = get_path(config, "paths.dataset_dir", base_path)
    output_dir = get_path(config, "paths.output_dir", base_path)

    # Шаг 1: Предобработка
    if args.stage in ["all", "preprocess"]:
        preprocess = ImagePreprocessPipeline(config)
        preprocess.run(video_dir, frames_dir, clean_frames_dir)

    # Шаг 2: Авторазметка
    if args.stage in ["all", "annotate"]:
        annot = ImageAnnotationPipeline(config)
        annot.run(clean_frames_dir, dataset_dir)

    # Шаг 3: Разделение (если нужно пересобрать сплит)
    if args.stage in ["all", "split"]:
        splitter = DatasetSplitPipeline(config)
        splitter.run(dataset_dir)

    finetune_flag = args.finetune == "yes"

    # Шаг 4: Обучение
    if args.stage in ["all", "train"]:
        trainer = YoloTrainPipeline(config)
        trainer.run(dataset_dir, output_dir, finetune=finetune_flag)

    logger.info("Pipeline завершен")


if __name__ == "__main__":
    main()
