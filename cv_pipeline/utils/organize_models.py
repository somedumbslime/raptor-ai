"""Утилита для организации моделей в папке models"""
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import argparse
from loguru import logger


def organize_model(
    model_path: str,
    models_dir: str = "models",
    description: str = "",
    move: bool = False
) -> Path:
    """
    Организует модель в папке models с понятным именем
    
    Args:
        model_path: Путь к модели
        models_dir: Папка для моделей
        description: Описание модели (будет добавлено в имя файла)
        move: Переместить (True) или скопировать (False)
        
    Returns:
        Путь к новой модели
    """
    source_path = Path(model_path)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Модель не найдена: {model_path}")
    
    # Создаем папку models
    models_path = Path(models_dir)
    models_path.mkdir(parents=True, exist_ok=True)
    
    # Формируем имя файла: model_YYYY-MM-DD_description.pt
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_name = source_path.stem
    
    if description:
        new_name = f"model_{date_str}_{description}.pt"
    else:
        # Пытаемся извлечь описание из исходного имени
        new_name = f"model_{date_str}_{base_name}.pt"
    
    dest_path = models_path / new_name
    
    # Если файл уже существует, добавляем номер
    counter = 1
    while dest_path.exists():
        if description:
            new_name = f"model_{date_str}_{description}_v{counter}.pt"
        else:
            new_name = f"model_{date_str}_{base_name}_v{counter}.pt"
        dest_path = models_path / new_name
        counter += 1
    
    # Копируем или перемещаем
    if move:
        shutil.move(str(source_path), str(dest_path))
        logger.info(f"Модель перемещена: {source_path} -> {dest_path}")
    else:
        shutil.copy2(str(source_path), str(dest_path))
        logger.info(f"Модель скопирована: {source_path} -> {dest_path}")
    
    return dest_path


def main():
    """CLI для организации моделей"""
    parser = argparse.ArgumentParser(
        description="Организация моделей в папке models"
    )
    parser.add_argument(
        "model_path",
        type=str,
        help="Путь к модели для организации"
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default="models",
        help="Папка для моделей (по умолчанию: models)"
    )
    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Описание модели (будет добавлено в имя файла)"
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Переместить модель вместо копирования"
    )
    
    args = parser.parse_args()
    
    try:
        result_path = organize_model(
            model_path=args.model_path,
            models_dir=args.models_dir,
            description=args.description,
            move=args.move
        )
        print(f"\n✅ Модель организована: {result_path}")
        print(f"\nДля использования в конфигурации укажите:")
        print(f"  model_path: \"{result_path.name}\"")
        print(f"или полный путь:")
        print(f"  model_path: \"{result_path}\"")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

