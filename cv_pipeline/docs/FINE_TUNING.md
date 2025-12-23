# Дообучение (Fine-tuning) YOLO модели

Pipeline поддерживает дообучение существующих моделей вместо обучения с нуля. Это полезно для:
- Улучшения модели на новых данных
- Адаптации под специфичный домен
- Продолжения прерванного обучения

## Настройка дообучения

В `config/config.yaml` в секции `training` добавьте настройки `resume_training`:

```yaml
training:
  model: "yolo11n.pt"  # Базовая модель (будет использована если resume_training.enabled=false)
  
  resume_training:
    # Включить дообучение
    enabled: true
    
    # Путь к модели для дообучения
    model_path: "best.pt"  # или "last.pt", или полный путь
    
    # Продолжить обучение с последнего состояния (только для last.pt)
    resume_from_checkpoint: false
    
    # Learning rate для дообучения (опционально, обычно меньше чем для обучения с нуля)
    fine_tune_lr0: 0.001  # null или значение
```

## Варианты использования

### 1. Дообучение лучшей модели

Начните обучение с весами лучшей модели, но начнется с эпохи 0:

```yaml
resume_training:
  enabled: true
  model_path: "best.pt"  # Найдет в outputs/training/yolo_training/weights/best.pt
  resume_from_checkpoint: false
  fine_tune_lr0: 0.001  # Меньший LR для fine-tuning
```

### 2. Продолжение прерванного обучения

Продолжите обучение с того же места, где остановились:

```yaml
resume_training:
  enabled: true
  model_path: "last.pt"  # Последний чекпоинт с состоянием оптимизатора
  resume_from_checkpoint: true  # Продолжить с той же эпохи
```

### 3. Дообучение конкретной модели

Укажите путь к модели (рекомендуется использовать папку `models/`):

```yaml
resume_training:
  enabled: true
  model_path: "models/model_2025-12-20_soldier_detection_v1.pt"
  resume_from_checkpoint: false
  fine_tune_lr0: 0.0005
```

Или просто имя файла (автоматически найдет в `models/`):
```yaml
resume_training:
  enabled: true
  model_path: "model_2025-12-20_soldier_detection_v1.pt"
```

## Важные моменты

1. **best.pt vs last.pt**:
   - `best.pt` - лучшая модель по метрике валидации (обычно используется для inference)
   - `last.pt` - последний чекпоинт, содержит состояние оптимизатора (можно продолжить обучение)

2. **resume_from_checkpoint**:
   - `true` - продолжит обучение с той же эпохи, LR schedule, momentum и т.д.
   - `false` - начнется с эпохи 0, но используя веса модели (обычный fine-tuning)

3. **Learning Rate**:
   - Для fine-tuning обычно используется меньший LR (например, 0.001 вместо 0.01)
   - Можно указать `fine_tune_lr0` или оставить `null` для использования базового `lr0`

4. **Пути к модели**:
   - `"best.pt"` или `"last.pt"` - ищет в `outputs/training/yolo_training/weights/`
   - Полный путь - относительно папки `rest` или абсолютный

## Примеры использования

### Пример 1: Улучшение модели на новых данных

```yaml
training:
  model: "yolo11n.pt"
  resume_training:
    enabled: true
    model_path: "best.pt"
    resume_from_checkpoint: false
    fine_tune_lr0: 0.001  # Меньший LR для более плавного дообучения
  epochs: 50  # Меньше эпох для fine-tuning
  lr0: 0.01   # Игнорируется, используется fine_tune_lr0
```

### Пример 2: Продолжение прерванного обучения

```yaml
training:
  epochs: 100
  resume_training:
    enabled: true
    model_path: "last.pt"
    resume_from_checkpoint: true  # Продолжит с эпохи, на которой остановились
```

### Пример 3: Адаптация под новый домен

```yaml
training:
  resume_training:
    enabled: true
    model_path: "outputs/training/previous_experiment/weights/best.pt"
    resume_from_checkpoint: false
    fine_tune_lr0: 0.0005  # Очень маленький LR для консервативного дообучения
  epochs: 30
```

## MLflow трекинг

При дообучении в MLflow автоматически логируются:
- `is_resume_training: true`
- `resume_model_path` - путь к исходной модели
- `resume_from_checkpoint` - флаг продолжения
- `fine_tune_lr0` - использованный LR для fine-tuning

Это помогает отслеживать историю дообучения модели.

