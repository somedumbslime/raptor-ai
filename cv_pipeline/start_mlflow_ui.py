"""Скрипт для запуска MLflow UI с доступом из локальной сети"""
import subprocess
import sys
import socket
from pathlib import Path


def get_local_ip():
    """Получить локальный IP адрес компьютера"""
    try:
        # Создаем временное подключение к внешнему серверу
        # чтобы узнать наш локальный IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    """Запуск MLflow UI"""
    # Путь к MLflow хранилищу (относительно корня rest)
    mlflow_path = Path(__file__).parent / "outputs" / "mlflow"
    
    if not mlflow_path.exists():
        print(f"⚠️  Папка MLflow не найдена: {mlflow_path}")
        print("Сначала запустите обучение, чтобы создать эксперименты MLflow")
        sys.exit(1)
    
    local_ip = get_local_ip()
    port = 5000
    
    print("=" * 80)
    print("ЗАПУСК MLFLOW UI")
    print("=" * 80)
    print(f"📂 Путь к MLflow: {mlflow_path.absolute()}")
    print(f"🌐 Локальный доступ: http://localhost:{port}")
    print(f"🌐 Доступ из сети: http://{local_ip}:{port}")
    print("=" * 80)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 80)
    
    # Запускаем MLflow UI с доступом из сети (0.0.0.0)
    cmd = [
        "mlflow",
        "ui",
        "--backend-store-uri",
        str(mlflow_path.absolute()),
        "--host",
        "0.0.0.0",  # Позволяет доступ из сети
        "--port",
        str(port),
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nMLflow UI остановлен")


if __name__ == "__main__":
    main()

