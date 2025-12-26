import os
import subprocess
import yaml
import shutil

# --- КОНСТАНТЫ ---
DEFAULT_CONFIG = "config/config.yaml"

# --- ФУНКЦИИ ---


def load_config(path=DEFAULT_CONFIG):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфиг не найден по пути: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def check_ffmpeg():
    """Проверка наличия установленного ffmpeg."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "Ошибка: 'ffmpeg' не найден в системе. Установите его для продолжения."
        )


def extract_frames(config_path=DEFAULT_CONFIG):
    """
    Извлекает кадры из видео, используя параметры из блока preprocess.video_processing.
    """
    # 1. Загрузка параметров
    check_ffmpeg()
    cfg = load_config(config_path)

    # Настройки из конфига
    proc_cfg = cfg["preprocess"]["video_processing"]
    paths_cfg = cfg["paths"]

    video_dir = paths_cfg["video_dir"]
    frames_dir = paths_cfg["frames_dir"]

    fps = proc_cfg["fps"]
    formats = tuple(proc_cfg["video_formats"])

    # Конвертируем качество 1-100 в шкалу ffmpeg q:v (1-31, где 1 - лучшее)
    # Формула для примерного соответствия: q = (100 - quality) / 3 + 1
    # Для 95 это будет примерно 2-3
    q_scale = max(1, int((100 - proc_cfg.get("jpeg_quality", 95)) / 3) + 1)

    os.makedirs(frames_dir, exist_ok=True)

    # Список файлов
    video_files = [f for f in os.listdir(video_dir) if f.lower().endswith(formats)]

    if not video_files:
        print(f"--- [INFO] Видео файлы не найдены в {video_dir}")
        return 0

    print(f"--- [START] Извлечение кадров: FPS={fps}, Качество (q:v)={q_scale}")

    # 2. Обработка
    for filename in video_files:
        video_path = os.path.join(video_dir, filename)
        video_name = os.path.splitext(filename)[0]
        output_pattern = os.path.join(frames_dir, f"{video_name}_f%04d.jpg")

        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            f"fps={fps}",
            "-q:v",
            str(q_scale),
            output_pattern,
            "-y",
        ]

        print(f"Обработка: {filename}...")

        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True
        )

        if result.returncode != 0:
            print(f"--- [ERROR] Ошибка в файле {filename}: {result.stderr}")

    # 3. Результат
    total_frames = len(
        [f for f in os.listdir(frames_dir) if f.lower().endswith(".jpg")]
    )
    print(f"\n--- [FINISH] Обработка завершена!")
    print(f"Всего кадров в папке: {total_frames}")
    return total_frames


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    extract_frames()
