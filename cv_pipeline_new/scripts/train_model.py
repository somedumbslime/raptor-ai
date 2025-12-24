from ultralytics import YOLO
from torch.cuda import is_available
import yaml


with open("config/config.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)

dataset = data["paths"]["dataset_dir"]
output = data["paths"]["output_dir"]

model = data["training"]["model"]
finetune_model = data["training"]["finetune_model"]

epochs = data["training"]["epochs"]
batch_size = data["training"]["batch_size"]
image_size = data["training"]["image_size"]

device = "cuda" if is_available() else "cpu"

name = "train_5783f"

if __name__ == "__main__":
    model = YOLO(model)
    # 2. Запускаем обучение
    results = model.train(
        # data="DATASET/my_dataset_yolo12s.yaml",  # путь к твоему yaml
        data=f'{dataset}/data.yaml',
        epochs=epochs,
        imgsz=image_size,
        batch=batch_size,  # можно раскомментировать и подобрать под свою GPU
        # cache="disk",     # ускоряет обучение, если хватает места
        device=device,  # или "cpu" если нет GPU
        project=output,  # папка для логов и весов
        name=name,  # имя эксперимента
        pretrained=True,  # использовать предобученные веса
    )

    print(f"Обучение завершено! Лучшая модель будет в {output}/{name}/weights/best.pt")
