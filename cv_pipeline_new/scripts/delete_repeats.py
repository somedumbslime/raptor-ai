import os
from PIL import Image
import imagehash
import yaml


with open("config/config.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)


# Папка с изображениями
folder = data["paths"]["frames_dir"]
hashes = {}
threshold = 5  # 0 = только точные дубликаты, 5 — более свободно

# Счётчики
total_files_before = 0
removed_duplicates = 0

# Получаем список файлов
all_files = [
    f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))
]
total_files_before = len(all_files)

for filename in all_files:
    path = os.path.join(folder, filename)
    try:
        image = Image.open(path)
        h = imagehash.phash(image)

        duplicate_found = False
        for existing_hash in hashes:
            if abs(h - existing_hash) <= threshold:
                print(f"❌ Похож на: {hashes[existing_hash]} -> удаляю: {filename}")
                os.remove(path)
                removed_duplicates += 1
                duplicate_found = True
                break

        if not duplicate_found:
            hashes[h] = filename

    except Exception as e:
        print(f"⚠️ Ошибка с файлом {filename}: {e}")

# Итоговая статистика
remaining_files = total_files_before - removed_duplicates
print("\n📊 Результаты:")
print(f"📂 Было файлов:     {total_files_before}")
print(f"🗑️  Удалено дубликатов: {removed_duplicates}")
print(f"📁 Осталось файлов: {remaining_files}")
