"""Удаление дубликатов изображений с использованием perceptual hashing"""

import os
from pathlib import Path
from typing import Dict, Optional
from PIL import Image
import imagehash
from loguru import logger
from tqdm import tqdm


def remove_duplicates(
    input_dir: str,
    output_dir: Optional[str] = None,
    hash_threshold: int = 5,
    hash_method: str = "phash",
    min_image_size: int = 32,
    move_duplicates: bool = False,
) -> dict:
    """
    Удаление дубликатов изображений с использованием perceptual hashing

    Args:
        input_dir: Путь к папке с изображениями
        output_dir: Путь для сохранения очищенных изображений (если None - удаляем на месте)
        hash_threshold: Порог для сравнения хешей (0 = только точные дубликаты)
        hash_method: Метод хеширования ('phash', 'average_hash', 'dhash', 'whash')
        min_image_size: Минимальный размер изображения для обработки
        move_duplicates: Перемещать дубликаты в отдельную папку вместо удаления

    Returns:
        Словарь со статистикой:
        {
            'total_files': int,
            'removed_duplicates': int,
            'remaining_files': int,
            'output_dir': str
        }
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Папка с изображениями не найдена: {input_dir}")

    # Определяем метод хеширования
    hash_functions = {
        "phash": imagehash.phash,
        "average_hash": imagehash.average_hash,
        "dhash": imagehash.dhash,
        "whash": imagehash.whash,
    }

    if hash_method not in hash_functions:
        raise ValueError(
            f"Неизвестный метод хеширования: {hash_method}. Доступные: {list(hash_functions.keys())}"
        )

    hash_func = hash_functions[hash_method]

    # Создаем выходную папку, если указана
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path

    # Папка для дубликатов (если move_duplicates = True)
    duplicates_dir = None
    if move_duplicates:
        duplicates_dir = output_path / "duplicates"
        duplicates_dir.mkdir(parents=True, exist_ok=True)

    # Получаем список всех изображений
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    all_files = [
        f
        for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    total_files = len(all_files)
    logger.info(f"Найдено {total_files} изображений для проверки на дубликаты")

    if total_files == 0:
        return {
            "total_files": 0,
            "removed_duplicates": 0,
            "remaining_files": 0,
            "output_dir": str(output_path),
        }

    # Хранилище хешей (хеш -> имя файла)
    hashes: Dict[imagehash.ImageHash, str] = {}
    removed_count = 0
    processed_count = 0

    # Обрабатываем каждый файл
    for image_file in tqdm(all_files, desc="Поиск дубликатов"):
        try:
            # Открываем изображение
            with Image.open(image_file) as img:
                # Проверяем минимальный размер
                if min(img.size) < min_image_size:
                    logger.debug(
                        f"Пропускаем {image_file.name} - слишком маленький размер"
                    )
                    continue

                # Вычисляем хеш
                img_hash = hash_func(img)

            # Проверяем на дубликаты
            duplicate_found = False
            similar_hash = None

            for existing_hash, existing_file in hashes.items():
                # Вычисляем расстояние между хешами
                hash_distance = abs(img_hash - existing_hash)

                if hash_distance <= hash_threshold:
                    logger.debug(
                        f"Найден дубликат: {image_file.name} похож на {existing_file} (расстояние: {hash_distance})"
                    )

                    # Перемещаем или удаляем дубликат
                    if move_duplicates and duplicates_dir:
                        duplicate_path = duplicates_dir / image_file.name
                        image_file.rename(duplicate_path)
                        logger.debug(f"Дубликат перемещен в {duplicate_path}")
                    else:
                        image_file.unlink()

                    removed_count += 1
                    duplicate_found = True
                    similar_hash = existing_hash
                    break

            # Если не дубликат, сохраняем хеш
            if not duplicate_found:
                hashes[img_hash] = image_file.name

                # Если указана выходная папка и она отличается от входной, копируем файл
                if output_dir and output_path != input_path:
                    import shutil

                    shutil.copy2(image_file, output_path / image_file.name)

            processed_count += 1

        except Exception as e:
            logger.error(f"Ошибка при обработке {image_file.name}: {e}")
            continue

    remaining_files = total_files - removed_count

    logger.info(f"Удаление дубликатов завершено:")
    logger.info(f"  - Всего файлов: {total_files}")
    logger.info(f"  - Удалено дубликатов: {removed_count}")
    logger.info(f"  - Осталось файлов: {remaining_files}")
    logger.info(f"  - Выходная папка: {output_path}")

    return {
        "total_files": total_files,
        "removed_duplicates": removed_count,
        "remaining_files": remaining_files,
        "output_dir": str(output_path),
    }
