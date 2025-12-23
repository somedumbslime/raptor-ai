# End-to-End YOLO Training Pipeline для детекции солдат

Профессиональный pipeline для обучения YOLO модели детекции солдат с автоматической подготовкой данных, разметкой и трекингом экспериментов.

## Структура проекта

```
rest/
├── README.md                 # Документация
├── requirements.txt          # Зависимости
├── config/
│   └── config.yaml          # Конфигурация pipeline
├── src/
│   ├── data_preparation/    # Процесс 1: Подготовка данных
│   │   ├── video_to_frames.py
│   │   └── remove_duplicates.py
│   ├── annotation/          # Процесс 2: Автоматическая разметка
│   │   └── auto_annotate.py
│   ├── training/            # Процесс 3: Обучение с MLflow
│   │   └── train_yolo.py
│   └── utils/               # Утилиты
│       ├── logger.py
│       └── config_loader.py
└── main.py                  # Главный скрипт запуска
```

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Убедитесь, что установлен FFmpeg для обработки видео

## Использование

### Проверка конфигурации перед запуском:

```bash
python check_config.py
```

Этот скрипт проверит:
- Наличие всех необходимых пакетов
- Наличие FFmpeg
- Валидность конфигурационного файла
- Существование необходимых путей

### Полный pipeline (все процессы):

```bash
python main.py --config config/config.yaml --stage all
```

### Отдельные процессы:

```bash
# Только подготовка данных
python main.py --config config/config.yaml --stage data_preparation

# Только разметка
python main.py --config config/config.yaml --stage annotation

# Только обучение
python main.py --config config/config.yaml --stage training
```

### С логированием в файл:

```bash
python main.py --config config/config.yaml --stage all --log-file logs/pipeline.log
```

## Процессы Pipeline

### Процесс 1: Подготовка данных
- Извлечение кадров из видео с настраиваемой частотой
- Фильтрация дубликатов с использованием perceptual hashing
- Статистика и логирование

### Процесс 2: Автоматическая разметка
- Использование предобученной YOLO модели для предварительной разметки
- Сохранение аннотаций в формате YOLO
- Возможность последующей ручной коррекции

### Процесс 3: Обучение модели
- Обучение YOLO модели с полным трекингом в MLflow
- Автоматическое логирование метрик, параметров и артефактов
- Сохранение лучшей модели
- **Дообучение существующих моделей** с поддержкой resume (см. [docs/FINE_TUNING.md](docs/FINE_TUNING.md))

## Конфигурация

Все параметры настраиваются в `config/config.yaml`:
- Пути к данным
- Параметры извлечения кадров
- Параметры фильтрации дубликатов
- Параметры обучения модели

## Организация моделей

Для удобства работы с моделями создана папка `models/`, где хранятся обученные модели с понятными именами.

### Рекомендуемый формат имен:
```
model_YYYY-MM-DD_description.pt
```
Например: `model_2025-12-20_soldier_detection_v1.pt`

### Организация существующих моделей:

Используйте утилиту для автоматической организации:
```bash
python utils/organize_models.py best.pt --description "soldier_detection_v1"
```

Или вручную переместите модель в `models/` с понятным именем.

### Использование модели из папки models:

В конфигурации укажите:
```yaml
resume_training:
  enabled: true
  model_path: "models/model_2025-12-20_soldier_detection_v1.pt"
```

Или просто имя файла (если модель в `models/`):
```yaml
resume_training:
  enabled: true
  model_path: "model_2025-12-20_soldier_detection_v1.pt"
```

## MLflow

### Запуск MLflow UI

После обучения для просмотра результатов в MLflow UI:

**Вариант 1: Локальный доступ (только с этого компьютера):**
```bash
mlflow ui --backend-store-uri rest/outputs/mlflow
```
Откройте в браузере: http://localhost:5000

**Вариант 2: Доступ из локальной сети (удобный скрипт):**
```bash
python start_mlflow_ui.py
```
Скрипт автоматически покажет:
- Локальный IP адрес: `http://<ваш-ip>:5000`
- Локальный доступ: `http://localhost:5000`

**Вариант 3: Ручной запуск с доступом из сети:**
```bash
mlflow ui --backend-store-uri rest/outputs/mlflow --host 0.0.0.0 --port 5000
```

### Определение IP адреса для доступа из сети

Чтобы узнать ваш IP адрес для доступа с других устройств:
- Windows: `ipconfig` (смотрите IPv4 Address)
- Linux/Mac: `ifconfig` или `ip addr`

MLflow UI будет доступен по адресу: `http://<ваш-ip>:5000`

