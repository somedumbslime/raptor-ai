import os
from ultralytics import YOLO
import yaml


with open("config/config.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)


MODEL_PATH = data["paths"]["models_dir"]
MODEL_NAME = data["predict"]["model"]

TEST_PATH = data["paths"]["test_dir"]
RESULT_FOLDER = data["paths"]["test_results"]

CONF = data["predict"]["conf"]
IOU = data["predict"]["iou"]

model = YOLO(f"{MODEL_PATH}/{MODEL_NAME}")

print(f"Загружаем модель: f'{MODEL_PATH}/{MODEL_NAME}'")
print(f"Используем тестовую папку: {TEST_PATH}")

# 3. Выполнение предсказаний на тестовых фотографиях
results = model.predict(
    source=TEST_PATH,
    save=True,  # Обязательно: сохраняет изображения с предсказаниями
    save_txt=False,  # (Опционально) сохраняет текстовые файлы с координатами предсказаний
    save_conf=True,  # (Опционально) сохраняет уверенность в текстовых файлах
    project=RESULT_FOLDER,  # Основная папка, куда сохранять результаты (по умолчанию runs/)
    # name=RESULT_FOLDER,  # Название подпапки для этого запуска предсказаний (например, runs/detect/test_predictions)
    conf=CONF,  # Порог уверенности: объекты с уверенностью ниже 0.25 не будут показаны.
    # Можно увеличить, если у вас много ложных срабатываний (например, до 0.5)
    iou=IOU,  # Порог IoU для Non-Maximum Suppression (помогает удалять дублирующиеся рамки)
)

print(f"\n--- Предсказания сохранены! ---")
print(
    f"Выходные изображения с предсказаниями вы найдете в папке: runs/detect/test_predictions"
)

# Вы можете также программно обработать результаты, если это необходимо
# for r in results:
#     print(f"Обработано изображение: {r.path}")
#     for box in r.boxes:
#         print(f"  Обнаружен объект класса {box.cls.item()} с уверенностью {box.conf.item():.2f} в координатах {box.xyxy[0].tolist()}")
