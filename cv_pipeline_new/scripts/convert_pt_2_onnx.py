import torch
from ultralytics import YOLO

# === Параметры ===
PT_MODEL_PATH = "runs/detect/train_yolov8n_50000f/weights/best.pt"         # Путь к твоей .pt модели
ONNX_EXPORT_PATH = "model_50000f.onnx"  # Имя итогового onnx-файла
IMG_SIZE = 640                       # Размер, на котором обучалась модель

if __name__ == "__main__":
    # 1. Загружаем PyTorch-модель
    model = YOLO(PT_MODEL_PATH)

    # 2. Экспортируем в ONNX
    model.export(
        format="onnx",
        imgsz=IMG_SIZE,
        opset=12,           # Совместимый opset
        simplify=True,      # Упрощение графа (можно False, если будут проблемы)
        dynamic=False,      # Фиксированный размер входа
        half=False,         # float32 (безопаснее)
        optimize=True,      # Оптимизация графа
        device="cpu",       # Экспорт на CPU
        # verbose=True      # Раскомментируй для подробного лога
        # task="detect"
        nms=True
    )

    print(f"Экспорт завершён! ONNX-модель сохранена в: {ONNX_EXPORT_PATH}")