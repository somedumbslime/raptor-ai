"""Загрузка и валидация конфигурации"""
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Загрузка конфигурации из YAML файла
    
    Args:
        config_path: Путь к файлу конфигурации
        
    Returns:
        Словарь с конфигурацией
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"Конфигурация загружена из {config_path}")
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Базовая валидация конфигурации
    
    Args:
        config: Словарь с конфигурацией
        
    Returns:
        True если конфигурация валидна
    """
    required_sections = ['paths', 'data_preparation', 'annotation', 'training']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Отсутствует обязательная секция конфигурации: {section}")
    
    logger.info("Конфигурация валидна")
    return True


def get_path(config: Dict[str, Any], key: str, base_path: Path = None) -> Path:
    """
    Получить путь из конфигурации и преобразовать в Path объект
    
    Args:
        config: Словарь с конфигурацией
        key: Ключ пути (например, 'paths.video_dir')
        base_path: Базовый путь для относительных путей
        
    Returns:
        Path объект
    """
    keys = key.split('.')
    value = config
    for k in keys:
        value = value[k]
    
    path = Path(value)
    
    # Если путь относительный и указан базовый путь
    if not path.is_absolute() and base_path:
        path = base_path / path
    
    return path

