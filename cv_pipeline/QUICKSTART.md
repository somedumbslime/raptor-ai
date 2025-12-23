# Быстрый старт

## Шаг 1: Установка зависимостей

```bash
cd rest
pip install -r requirements.txt
```

## Шаг 2: Проверка окружения

```bash
python check_config.py
```

Убедитесь, что:
- ✅ FFmpeg установлен
- ✅ Все Python пакеты установлены
- ✅ Конфигурация валидна

## Шаг 3: Настройка конфигурации

Отредактируйте `config/config.yaml`:

1. Укажите путь к папке с видео:
```yaml
paths:
  video_dir: "../job_with_videos/downloaded_videos"  # или абсолютный путь
```

2. При необходимости измените параметры:
   - Частота извлечения кадров (`data_preparation.video_processing.fps`)
   - Порог удаления дубликатов (`data_preparation.deduplication.hash_threshold`)
   - Параметры обучения модели (`training`)

## Шаг 4: Запуск полного pipeline

```bash
python main.py --config config/config.yaml --stage all
```

Это выполнит:
1. Извлечение кадров из видео
2. Удаление дубликатов
3. Автоматическую разметку
4. Обучение модели с трекингом в MLflow

## Шаг 5: Просмотр результатов

### MLflow UI

После обучения запустите:

```bash
mlflow ui --backend-store-uri rest/outputs/training/mlflow
```

И откройте в браузере: http://localhost:5000

### Результаты обучения

- Модель: `rest/outputs/training/yolo_training/weights/best.pt`
- Графики: `rest/outputs/training/yolo_training/`
- Датасет: `rest/data/dataset/`

## Пошаговый запуск (опционально)

Если хотите запустить процессы отдельно:

### 1. Только подготовка данных

```bash
python main.py --config config/config.yaml --stage data_preparation
```

Результат: очищенные кадры в `data/clean_frames/`

### 2. Только разметка

```bash
python main.py --config config/config.yaml --stage annotation
```

Результат: размеченный датасет в `data/dataset/`

### 3. Только обучение

```bash
python main.py --config config/config.yaml --stage training
```

## Ручная корректировка разметки

После автоматической разметки вы можете:
1. Просмотреть аннотации в формате YOLO (файлы `.txt` в `data/dataset/train/labels/`)
2. Использовать инструменты для ручной правки (например, CVAT, LabelImg)
3. После корректировки запустить только обучение

## Советы

- Для большого количества видео запускайте pipeline в несколько этапов
- Проверяйте качество автоматической разметки перед обучением
- Используйте разные модели для разметки (`yolo11n.pt`, `yolo11s.pt`, `yolo11m.pt`) для сравнения
- Экспериментируйте с параметрами аугментации в конфигурации

