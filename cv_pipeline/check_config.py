"""Скрипт для проверки конфигурации перед запуском pipeline"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import load_config, validate_config
from src.data_preparation.video_to_frames import check_ffmpeg
from loguru import logger


def check_environment():
    """Проверка окружения перед запуском"""
    logger.info("Проверка окружения...")
    
    issues = []
    
    # Проверка FFmpeg
    if not check_ffmpeg():
        issues.append("❌ FFmpeg не найден. Установите FFmpeg для обработки видео.")
    else:
        logger.info("✅ FFmpeg установлен")
    
    # Проверка Python пакетов
    required_packages = [
        'ultralytics',
        'mlflow',
        'PIL',
        'imagehash',
        'sklearn',
        'loguru',
        'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'sklearn':
                __import__('sklearn')
            else:
                __import__(package)
            logger.info(f"✅ {package} установлен")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} не найден")
    
    if missing_packages:
        issues.append(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        issues.append("   Установите их командой: pip install -r requirements.txt")
    
    return issues


def check_configuration(config_path: str = "config/config.yaml"):
    """Проверка конфигурации"""
    logger.info(f"Проверка конфигурации: {config_path}")
    
    issues = []
    
    try:
        config = load_config(config_path)
        validate_config(config)
        logger.info("✅ Конфигурация валидна")
    except Exception as e:
        issues.append(f"❌ Ошибка конфигурации: {e}")
        return issues
    
    # Проверка путей
    paths = config.get('paths', {})
    base_path = Path(__file__).parent
    
    required_paths = ['video_dir', 'frames_dir', 'clean_frames_dir']
    for path_key in required_paths:
        if path_key not in paths:
            issues.append(f"❌ Отсутствует путь в конфигурации: paths.{path_key}")
        else:
            path_value = paths[path_key]
            # Проверяем, существует ли папка с видео (она должна быть)
            if path_key == 'video_dir':
                video_path = base_path / path_value if not Path(path_value).is_absolute() else Path(path_value)
                if not video_path.exists():
                    issues.append(f"⚠️  Папка с видео не найдена: {video_path}")
                    issues.append("   Создайте папку и поместите туда видео файлы")
    
    return issues


def main():
    """Главная функция проверки"""
    logger.info("=" * 80)
    logger.info("ПРОВЕРКА КОНФИГУРАЦИИ И ОКРУЖЕНИЯ")
    logger.info("=" * 80)
    
    all_issues = []
    
    # Проверка окружения
    env_issues = check_environment()
    all_issues.extend(env_issues)
    
    # Проверка конфигурации
    config_path = Path(__file__).parent / "config" / "config.yaml"
    if config_path.exists():
        config_issues = check_configuration(str(config_path))
        all_issues.extend(config_issues)
    else:
        all_issues.append(f"❌ Файл конфигурации не найден: {config_path}")
    
    # Итоги
    logger.info("=" * 80)
    if all_issues:
        logger.error("НАЙДЕНЫ ПРОБЛЕМЫ:")
        for issue in all_issues:
            logger.error(f"  {issue}")
        logger.error("\nИсправьте проблемы перед запуском pipeline")
        return 1
    else:
        logger.info("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        logger.info("Система готова к запуску pipeline")
        return 0


if __name__ == "__main__":
    sys.exit(main())

