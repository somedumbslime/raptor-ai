"""Pipeline для подготовки данных (объединяет извлечение кадров и удаление дубликатов)"""
from pathlib import Path
from typing import Dict
from loguru import logger

from .video_to_frames import extract_frames, check_ffmpeg
from .remove_duplicates import remove_duplicates


def run_data_preparation_pipeline(config: Dict) -> Dict:
    """
    Полный pipeline подготовки данных
    
    Args:
        config: Конфигурация из config.yaml
        
    Returns:
        Словарь со статистикой всех этапов
    """
    logger.info("Запуск pipeline подготовки данных...")
    
    # Проверяем наличие ffmpeg
    if not check_ffmpeg():
        raise RuntimeError("FFmpeg не найден! Установите FFmpeg для обработки видео.")
    
    # Получаем пути
    paths = config['paths']
    video_dir = Path(paths['video_dir'])
    frames_dir = Path(paths['frames_dir'])
    clean_frames_dir = Path(paths['clean_frames_dir'])
    
    # Настройки извлечения кадров
    video_config = config['data_preparation']['video_processing']
    fps = video_config.get('fps', 0.33)
    video_formats = video_config.get('video_formats', [".mp4", ".mov", ".avi", ".mkv"])
    jpeg_quality = video_config.get('jpeg_quality', 95)
    
    # Настройки удаления дубликатов
    dedup_config = config['data_preparation']['deduplication']
    hash_threshold = dedup_config.get('hash_threshold', 5)
    hash_method = dedup_config.get('hash_method', 'phash')
    min_image_size = dedup_config.get('min_image_size', 32)
    
    # Шаг 1: Извлечение кадров
    logger.info("Этап 1: Извлечение кадров из видео...")
    frames_stats = extract_frames(
        video_dir=str(video_dir),
        output_dir=str(frames_dir),
        fps=fps,
        video_formats=video_formats,
        jpeg_quality=jpeg_quality
    )
    
    # Шаг 2: Удаление дубликатов
    logger.info("Этап 2: Удаление дубликатов...")
    dedup_stats = remove_duplicates(
        input_dir=str(frames_dir),
        output_dir=str(clean_frames_dir),
        hash_threshold=hash_threshold,
        hash_method=hash_method,
        min_image_size=min_image_size
    )
    
    return {
        'frames_extraction': frames_stats,
        'deduplication': dedup_stats,
        'clean_frames_dir': str(clean_frames_dir)
    }

