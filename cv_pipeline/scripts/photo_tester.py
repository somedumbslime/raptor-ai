import os
import yaml
from ultralytics import YOLO

# --- КОНСТАНТЫ ПО УМОЛЧАНИЮ ---
# Используем их только как значения "на случай, если пользователь ничего не передал"
DEFAULT_CONFIG = "config/config.yaml"

# --- ФУНКЦИИ-ПОМОЩНИКИ ---


def load_settings(config_path=DEFAULT_CONFIG):
    """Безопасно загружает настройки из YAML."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Конфиг не найден по пути: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def run_prediction(config_path=DEFAULT_CONFIG):
    """
    Основная функция инференса.
    """
    data = load_settings(config_path)

    # Извлекаем параметры из конфига
    model_full_path = os.path.join(
        data["paths"]["models_dir"], data["predict"]["model"]
    )
    test_path = data["paths"]["test_photo_dir"]
    result_folder = data["paths"]["test_photo_results"]

    # Инициализация модели
    model = YOLO(model_full_path)

    print(f"Загружаем модель: {model_full_path}")

    results = model.predict(
        source=test_path,
        save=True,
        project=result_folder,
        conf=data["predict"]["conf"],
        iou=data["predict"]["iou"],
        # Можно добавить дополнительные параметры из data["predict"]
    )

    print(f"--- Предсказания сохранены в {result_folder} ---")
    return results


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    run_prediction()
