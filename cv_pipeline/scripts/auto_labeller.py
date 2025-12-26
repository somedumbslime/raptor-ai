import os
import yaml
import shutil
import random
import cv2
import matplotlib.pyplot as plt
import math
import zipfile
from ultralytics import YOLO

# --- КОНСТАНТЫ ---
DEFAULT_CONFIG = "config/config.yaml"

def load_config(path=DEFAULT_CONFIG):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфиг не найден: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def setup_yolo_structure(base_path):
    """Создает стандартную иерархию папок YOLO (train/val/test)."""
    subdirs = [
        "images/train", "images/val", "images/test",
        "labels/train", "labels/val", "labels/test",
    ]
    for subdir in subdirs:
        os.makedirs(os.path.join(base_path, subdir), exist_ok=True)

# ==========================================
# ЭТАП 1: АВТОРАЗМЕТКА И СОЗДАНИЕ ZIP ДЛЯ CVAT
# ==========================================

def run_auto_annotation(config_path=DEFAULT_CONFIG):
    """
    Создает структуру YOLO 1.1 и упаковывает в archive.zip для CVAT.
    """
    cfg = load_config(config_path)
    frames_in = cfg["paths"]["frames_dir"]
    raw_anno_dir = cfg["paths"]["annotations_dir"] # "data/auto_annotations"
    class_name = cfg["annotation"]["class_name"]
    
    # Очищаем/Создаем рабочую директорию
    if os.path.exists(raw_anno_dir):
        shutil.rmtree(raw_anno_dir)
    os.makedirs(raw_anno_dir, exist_ok=True)

    # Согласно вашему примеру, используем подпапку obj_train_data внутри архива
    subset_folder = "obj_train_data"
    subset_path = os.path.join(raw_anno_dir, subset_folder)
    os.makedirs(subset_path, exist_ok=True)

    # Загрузка модели
    model_path = os.path.join(cfg["paths"]["models_dir"], cfg["annotation"]["pretrained_model"])
    model = YOLO(model_path)

    all_images = [f for f in os.listdir(frames_in) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    train_txt_lines = []

    print(f"--- [START] Авторазметка для CVAT: {len(all_images)} изображений ---")

    for filename in all_images:
        img_path = os.path.join(frames_in, filename)
        results = model.predict(img_path, conf=cfg["annotation"]["confidence_threshold"], 
                                iou=cfg["annotation"]["iou_threshold"], verbose=False)

        # Копируем изображение в подпапку подмножества
        shutil.copy(img_path, os.path.join(subset_path, filename))
        train_txt_lines.append(f"{subset_folder}/{filename}")

        # Собираем аннотации
        yolo_lines = []
        for r in results:
            for box in r.boxes:
                xywh = box.xywhn.cpu().numpy()[0]
                cls = int(box.cls.cpu().numpy()[0])
                yolo_lines.append(f"{cls} {xywh[0]:.6f} {xywh[1]:.6f} {xywh[2]:.6f} {xywh[3]:.6f}")

        # Создаем .txt файл разметки (даже если пустой, для CVAT это нормально)
        lbl_name = filename.rsplit(".", 1)[0] + ".txt"
        with open(os.path.join(subset_path, lbl_name), "w") as f:
            f.write("\n".join(yolo_lines))

    # Создаем служебные файлы для CVAT
    # 1. obj.names
    with open(os.path.join(raw_anno_dir, "obj.names"), "w") as f:
        f.write(f"{class_name}\n")

    # 2. train.txt (список путей к картинкам)
    with open(os.path.join(raw_anno_dir, "train.txt"), "w") as f:
        f.write("\n".join(train_txt_lines))

    # 3. obj.data
    with open(os.path.join(raw_anno_dir, "obj.data"), "w") as f:
        f.write(f"classes = 1\n")
        f.write(f"names = obj.names\n")
        f.write(f"train = train.txt\n")
        f.write(f"backup = backup/\n")

    # Упаковка в archive.zip
    zip_path = os.path.join(raw_anno_dir, "archive.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Добавляем файлы из корня annotations_dir
        for root, _, files in os.walk(raw_anno_dir):
            for file in files:
                if file == "archive.zip": continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, raw_anno_dir)
                zipf.write(full_path, rel_path)

    print(f"--- [INFO] Авторазметка завершена. Архив создан: {zip_path}")

# ==========================================
# ЭТАП 2: КОНВЕРТАЦИЯ В TRAINING DATASET
# ==========================================

def create_training_dataset(config_path=DEFAULT_CONFIG, keep_empty_images=True):
    """
    Конвертирует структуру из auto_annotations в train/val/test для обучения.
    """
    cfg = load_config(config_path)
    src_folder = os.path.join(cfg["paths"]["annotations_dir"], "obj_train_data")
    dst_dir = cfg["paths"]["dataset_dir"]
    
    if not os.path.exists(src_folder):
        print(f"--- [ERROR] Исходная папка {src_folder} не найдена. Сначала запустите разметку.")
        return

    setup_yolo_structure(dst_dir)
    all_images = [f for f in os.listdir(src_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    random.seed(cfg["split"]["seed"])
    random.shuffle(all_images)

    # Split
    tr_end = int(len(all_images) * cfg["split"]["train"])
    vl_end = tr_end + int(len(all_images) * cfg["split"]["val"])

    splits = {
        "train": all_images[:tr_end],
        "val": all_images[tr_end:vl_end],
        "test": all_images[vl_end:]
    }

    print(f"--- [START] Создание датасета для обучения в {dst_dir} ---")

    for usage, files in splits.items():
        for filename in files:
            base_name = filename.rsplit(".", 1)[0]
            src_img = os.path.join(src_folder, filename)
            src_lbl = os.path.join(src_folder, base_name + ".txt")

            # Проверяем наличие объектов (размер файла > 0)
            has_obj = os.path.exists(src_lbl) and os.path.getsize(src_lbl) > 0

            if has_obj or keep_empty_images:
                shutil.copy(src_img, os.path.join(dst_dir, "images", usage, filename))
                if os.path.exists(src_lbl):
                    shutil.copy(src_lbl, os.path.join(dst_dir, "labels", usage, base_name + ".txt"))

    # Генерация data.yaml
    data_yaml = {
        "train": "images/train", "val": "images/val", "test": "images/test",
        "nc": 1, "names": [cfg["annotation"]["class_name"]]
    }
    with open(os.path.join(dst_dir, "data.yaml"), "w") as f:
        yaml.dump(data_yaml, f)
    print("--- [INFO] Датасет готов к обучению.")

# ==========================================
# ВИЗУАЛИЗАЦИЯ
# ==========================================

def visualize_annotations(num_images=5, dataset_path=None, keep_empty_images=True):
    """
    Визуализирует данные из папки авторазметки (obj_train_data).
    """
    cfg = load_config()
    if dataset_path is None:
        dataset_path = os.path.join(cfg["paths"]["annotations_dir"], "obj_train_data")

    if not os.path.exists(dataset_path):
        print(f"--- [ERROR] Путь {dataset_path} не существует.")
        return

    all_files = [f for f in os.listdir(dataset_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    if not keep_empty_images:
        img_selection = [f for f in all_files if os.path.exists(os.path.join(dataset_path, f.rsplit(".", 1)[0] + ".txt")) 
                         and os.path.getsize(os.path.join(dataset_path, f.rsplit(".", 1)[0] + ".txt")) > 0]
    else:
        img_selection = all_files

    if not img_selection:
        print("--- [WARNING] Нет подходящих изображений для визуализации.")
        return

    selected = random.sample(img_selection, min(num_images, len(img_selection)))
    
    cols = 4
    rows = math.ceil(len(selected) / cols)
    plt.figure(figsize=(20, 5 * rows))

    for i, filename in enumerate(selected):
        img = cv2.imread(os.path.join(dataset_path, filename))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        lbl_path = os.path.join(dataset_path, filename.rsplit(".", 1)[0] + ".txt")

        if os.path.exists(lbl_path):
            with open(lbl_path, "r") as f:
                for line in f:
                    parts = line.split()
                    if not parts: continue
                    cls, x, y, bw, bh = map(float, parts)
                    h, w, _ = img.shape
                    x1, y1 = int((x - bw/2) * w), int((y - bh/2) * h)
                    x2, y2 = int((x + bw/2) * w), int((y + bh/2) * h)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
        plt.subplot(rows, cols, i + 1)
        plt.imshow(img)
        plt.title(f"{filename}")
        plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_auto_annotation()