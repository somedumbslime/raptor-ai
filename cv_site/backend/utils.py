import os
import time


def cleanup_folder(folder, hours=24):
    now = time.time()
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            if now - os.path.getmtime(path) > hours * 3600:
                os.remove(path)


if __name__ == "__main__":
    cleanup_folder("uploads", hours=24)
    cleanup_folder("outputs", hours=24)
