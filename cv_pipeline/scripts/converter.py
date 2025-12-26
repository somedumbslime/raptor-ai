import os
import yaml
from ultralytics import YOLO

# --- КОНСТАНТЫ ---
DEFAULT_CONFIG = "config/config.yaml"

# --- ФУНКЦИИ ---


def load_config(path=DEFAULT_CONFIG):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфиг не найден: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def pt2onnx(model_path=None, config_path=DEFAULT_CONFIG):
    """
    Экспортирует модель в формат ONNX.
    Если model_path не указан, берет путь к весам из конфига.
    """
    # 1. Загрузка настроек
    cfg = load_config(config_path)
    train_cfg = cfg["training"]
    paths_cfg = cfg["paths"]

    # Определяем путь к модели
    # Если мы только что обучили модель, она лежит в project/name/weights/best.pt
    if model_path is None:
        model_path = os.path.join(
            paths_cfg["output_dir"], train_cfg["exp_name"], "weights", "best.pt"
        )

    if not os.path.exists(model_path):
        print(f"--- [ERROR] Модель для экспорта не найдена по пути: {model_path}")
        return None

    # 2. Инициализация модели
    print(f"--- [START] Загрузка модели для экспорта: {model_path}")
    model = YOLO(model_path)

    # 3. Экспорт
    # Параметры берем из конфига (image_size) или используем стандарты
    onnx_path = model.export(
        format="onnx",
        imgsz=train_cfg.get("image_size", 640),
        opset=12,
        simplify=True,
        dynamic=False,
        half=False,
        optimize=True,
        device="cpu",  # Экспорт на CPU более стабилен
        nms=True,
    )

    print(f"--- [FINISH] Экспорт завершен! Файл сохранен: {onnx_path}")
    return onnx_path


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    pt2onnx()
