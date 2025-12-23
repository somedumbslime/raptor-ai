"""Извлечение кадров из видео файлов"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional
from loguru import logger
from tqdm import tqdm


def extract_frames(
    video_dir: str,
    output_dir: str,
    fps: float = 0.33,
    video_formats: List[str] = None,
    jpeg_quality: int = 95,
    overwrite: bool = False,
) -> dict:
    """
    Извлечение кадров из видео файлов с использованием ffmpeg

    Args:
        video_dir: Путь к папке с видео файлами
        output_dir: Путь к папке для сохранения кадров
        fps: Частота извлечения кадров (кадров в секунду)
        video_formats: Список поддерживаемых форматов видео
        jpeg_quality: Качество JPEG (1-100)
        overwrite: Перезаписывать ли существующие файлы

    Returns:
        Словарь со статистикой:
        {
            'total_videos': int,
            'processed_videos': int,
            'total_frames': int,
            'output_dir': str
        }
    """
    if video_formats is None:
        video_formats = [".mp4", ".mov", ".avi", ".mkv"]

    video_path = Path(video_dir)
    output_path = Path(output_dir)

    if not video_path.exists():
        raise FileNotFoundError(f"Папка с видео не найдена: {video_dir}")

    # Создаем выходную папку
    output_path.mkdir(parents=True, exist_ok=True)

    # Находим все видео файлы
    video_files = []
    for fmt in video_formats:
        video_files.extend(video_path.glob(f"*{fmt}"))
        video_files.extend(video_path.glob(f"*{fmt.upper()}"))

    video_files = list(set(video_files))  # Убираем дубликаты
    total_videos = len(video_files)

    if total_videos == 0:
        logger.warning(f"Видео файлы не найдены в {video_dir}")
        return {
            "total_videos": 0,
            "processed_videos": 0,
            "total_frames": 0,
            "output_dir": str(output_path),
        }

    logger.info(f"Найдено {total_videos} видео файлов для обработки")

    processed_count = 0
    total_frames_count = 0

    # Обрабатываем каждый видео файл
    for video_file in tqdm(video_files, desc="Извлечение кадров"):
        try:
            video_name = video_file.stem

            # Формируем паттерн имени для выходных файлов
            output_pattern = output_path / f"{video_name}_frame_%06d.jpg"

            # Проверяем, нужно ли обрабатывать (если не overwrite и уже есть кадры)
            if not overwrite:
                existing_frames = list(output_path.glob(f"{video_name}_frame_*.jpg"))
                if existing_frames:
                    logger.debug(f"Пропускаем {video_file.name} - кадры уже существуют")
                    continue

                # Команда ffmpeg
            # FFmpeg использует обратную шкалу качества для JPEG (2 = лучшее качество, 31 = худшее)
            # Преобразуем качество из стандартной шкалы 1-100 в шкалу FFmpeg
            if jpeg_quality >= 90:
                ffmpeg_quality = 2
            elif jpeg_quality >= 80:
                ffmpeg_quality = 3
            elif jpeg_quality >= 70:
                ffmpeg_quality = 5
            else:
                ffmpeg_quality = 31 - (jpeg_quality // 3)

            cmd = [
                "ffmpeg",
                "-i",
                str(video_file),
                "-vf",
                f"fps={fps}",
                "-q:v",
                str(ffmpeg_quality),
                "-y" if overwrite else "-n",  # Перезаписывать или нет
                str(output_pattern),
            ]

            # Выполняем команду
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if result.returncode == 0:
                # Подсчитываем созданные кадры
                frames = list(output_path.glob(f"{video_name}_frame_*.jpg"))
                frame_count = len(frames)
                total_frames_count += frame_count
                processed_count += 1
                logger.debug(f"Обработано {video_file.name}: {frame_count} кадров")
            else:
                logger.error(f"Ошибка при обработке {video_file.name}: {result.stderr}")

        except Exception as e:
            logger.error(f"Ошибка при обработке {video_file.name}: {e}")
            continue

    logger.info(f"Извлечение кадров завершено:")
    logger.info(f"  - Обработано видео: {processed_count}/{total_videos}")
    logger.info(f"  - Всего кадров: {total_frames_count}")
    logger.info(f"  - Выходная папка: {output_path}")

    return {
        "total_videos": total_videos,
        "processed_videos": processed_count,
        "total_frames": total_frames_count,
        "output_dir": str(output_path),
    }


def check_ffmpeg() -> bool:
    """Проверка наличия ffmpeg в системе"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
