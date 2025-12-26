import os
import yaml
import imagehash
from PIL import Image

# --- КОНСТАНТЫ ---
DEFAULT_CONFIG = "config/config.yaml"

# --- ФУНКЦИИ ---


def load_config(path=DEFAULT_CONFIG):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфиг не найден: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_hash_func(method_name):
    """Выбирает метод хеширования из библиотеки imagehash."""
    methods = {
        "phash": imagehash.phash,
        "ahash": imagehash.average_hash,
        "dhash": imagehash.dhash,
        "whash": imagehash.whash,
    }
    # Если в конфиге что-то странное, по умолчанию берем phash
    return methods.get(method_name.lower(), imagehash.phash)


def remove_duplicates(config_path=DEFAULT_CONFIG):
    """Удаляет визуально похожие кадры на основе перцептивного хеша."""

    # 1. Загрузка настроек
    cfg = load_config(config_path)

    folder = cfg["paths"]["frames_dir"]
    dedup_cfg = cfg["preprocess"]["deduplication"]

    threshold = dedup_cfg["hash_threshold"]
    hash_func = get_hash_func(dedup_cfg["hash_method"])
    min_size = dedup_cfg["min_image_size"]

    if not os.path.exists(folder):
        print(f"--- [ERROR] Папка не найдена: {folder}")
        return

    # 2. Подготовка
    hashes = {}  # {hash: filename}
    all_files = [
        f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    total_before = len(all_files)
    removed_count = 0

    print(f"--- [START] Дедупликация в папке: {folder}")
    print(f"--- Метод: {dedup_cfg['hash_method']}, Порог: {threshold}")

    # 3. Основной цикл
    for filename in sorted(
        all_files
    ):  # Сортировка важна для последовательного сравнения
        path = os.path.join(folder, filename)

        try:
            with Image.open(path) as img:
                # Проверка на минимальный размер (битые или слишком мелкие кадры)
                if img.width < min_size or img.height < min_size:
                    print(f"Удален слишком мелкий файл: {filename}")
                    os.remove(path)
                    removed_count += 1
                    continue

                # Вычисляем хеш
                current_hash = hash_func(img)

            # Сравниваем с уже имеющимися хешами
            is_duplicate = False
            for existing_hash in hashes:
                if abs(current_hash - existing_hash) <= threshold:
                    print(f"Дубликат: {filename} похож на {hashes[existing_hash]}")
                    os.remove(path)
                    removed_count += 1
                    is_duplicate = True
                    break

            if not is_duplicate:
                hashes[current_hash] = filename

        except Exception as e:
            print(f"Ошибка обработки {filename}: {e}")

    # 4. Итог
    print("\n" + "=" * 20)
    print(f"Итоги дедупликации:")
    print(f"   Было: {total_before}")
    print(f"   Удалено: {removed_count}")
    print(f"   Осталось: {total_before - removed_count}")
    print("=" * 20)


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    remove_duplicates()
