"""Простая предобработка: извлечение кадров и удаление дублей."""

from pathlib import Path
from loguru import logger

from src.data_preparation.video_to_frames import extract_frames, check_ffmpeg
from src.data_preparation.remove_duplicates import remove_duplicates


class ImagePreprocessPipeline:
    """Минимальный класс предобработки (в стиле junior)."""

    def __init__(self, config: dict):
        self.config = config.get("preprocess", {})

    def run(self, video_dir: Path, frames_dir: Path, clean_frames_dir: Path):
        if not check_ffmpeg():
            raise RuntimeError("FFmpeg не найден, установите его перед запуском.")

        video_cfg = self.config.get("video_processing", {})
        dedup_cfg = self.config.get("deduplication", {})

        logger.info("Извлекаем кадры из видео...")
        extract_frames(
            video_dir=str(video_dir),
            output_dir=str(frames_dir),
            fps=video_cfg.get("fps", 0.33),
            video_formats=video_cfg.get(
                "video_formats", [".mp4", ".mov", ".avi", ".mkv"]
            ),
            jpeg_quality=video_cfg.get("jpeg_quality", 95),
        )

        logger.info("Удаляем дубликаты кадров...")
        remove_duplicates(
            input_dir=str(frames_dir),
            output_dir=str(clean_frames_dir),
            hash_threshold=dedup_cfg.get("hash_threshold", 5),
            hash_method=dedup_cfg.get("hash_method", "phash"),
            min_image_size=dedup_cfg.get("min_image_size", 32),
        )

        logger.info("Предобработка завершена")

