import os
import yaml
import torch
from ultralytics import YOLO

# --- КОНСТАНТЫ ---
DEFAULT_CONFIG = "config/config.yaml"

# --- ФУНКЦИИ ---


def load_config(path=DEFAULT_CONFIG):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_device(requested_device="cpu"):
    if requested_device == "cuda":
        if torch.cuda.is_available():
            return "cuda"
        else:
            print("--- [WARNING] CUDA не доступен. Используем CPU.")
            return "cpu"
    return "cpu"


def train_yolo_model(config_path=DEFAULT_CONFIG):
    """
    Запускает обучение или дообучение в зависимости от флага is_finetune.
    """
    cfg = load_config(config_path)

    # 1. Определяем, какую модель загружать
    training_cfg = cfg["training"]
    paths_cfg = cfg["paths"]

    # Собираем пути к моделям
    # Предполагаем, что модели лежат в папке, указанной в paths -> models_dir
    base_model_path = os.path.join(paths_cfg["models_dir"], training_cfg["model"])
    finetune_model_path = os.path.join(
        paths_cfg["models_dir"], training_cfg["finetune_model"]
    )

    # ЛОГИКА ВЫБОРА МОДЕЛИ
    if training_cfg.get("is_finetune", False):
        model_to_load = finetune_model_path
        print(f"--- [MODE] Режим ДООБУЧЕНИЯ (Fine-tune). Загружаем: {model_to_load}")
    else:
        model_to_load = base_model_path
        print(f"--- [MODE] Режим СТАНДАРТНОГО обучения. Загружаем: {model_to_load}")

    # 2. Инициализация
    model = YOLO(model_to_load)
    device = get_device(training_cfg["device"])
    dataset_path = os.path.join(paths_cfg["dataset_dir"], "data.yaml")

    # 3. Запуск обучения
    results = model.train(
        data=dataset_path,
        epochs=training_cfg["epochs"],
        imgsz=training_cfg["image_size"],
        batch=training_cfg["batch_size"],
        device=device,
        project=paths_cfg["output_dir"],
        name=training_cfg["exp_name"],
        pretrained=True,  # Для базовых моделей подгрузит веса, для своих — проигнорирует
    )

    print(
        f"--- [FINISH] Обучение завершено. Результаты в: {paths_cfg['output_dir']}/{training_cfg['exp_name']}"
    )
    return results


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    train_yolo_model()
