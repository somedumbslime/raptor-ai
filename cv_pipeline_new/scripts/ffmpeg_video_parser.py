import os
import subprocess
import yaml


with open("config/config.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)

# Папка с видео
VIDEO_DIR = data["paths"]["video_dir"]
# Папка для кадров
FRAMES_DIR = data["paths"]["frames_dir"]

FPS = data["preprocess"]["video_processing"]["fps"]
# Убедимся, что папка для кадров существует
os.makedirs(FRAMES_DIR, exist_ok=True)

# Перебираем все файлы в папке
for filename in os.listdir(VIDEO_DIR):
    if filename.lower().endswith(
        (".mp4", ".mov", ".avi", ".mkv")
    ):  # можно добавить форматы
        video_path = os.path.join(VIDEO_DIR, filename)
        video_name = os.path.splitext(filename)[0]
        output_folder = FRAMES_DIR

        os.makedirs(output_folder, exist_ok=True)

        # Команда ffmpeg для извлечения одного кадра каждые 3 секунды
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            f"fps={FPS}",
            os.path.join(output_folder, f"{video_name}_frame_%03d.jpg"),
        ]

        print(f"Обработка: {filename}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

total_frames = len([f for f in os.listdir(output_folder) if f.endswith(".jpg")])
print(f"\nГотово!")
print(f"\nИтого фотографий: {total_frames}")
