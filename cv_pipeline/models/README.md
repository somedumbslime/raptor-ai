# Папка для хранения обученных моделей

Эта папка предназначена для организованного хранения обученных YOLO моделей.

## Рекомендации по именованию

Используйте формат: `model_YYYY-MM-DD_description.pt`

### Примеры хороших имен:
- `model_2025-12-20_soldier_detection_v1.pt`
- `model_2025-12-20_soldier_detection_improved_lr.pt`
- `model_2025-12-21_fine_tuned_on_new_data.pt`

### Что указывать в описании:
- Версию модели (v1, v2, v3)
- Особенности обучения (improved_lr, more_epochs, etc.)
- Источник данных (new_data, augmented_data)
- Назначение (production, test, etc.)

## Организация моделей

### Автоматическая организация:

Используйте утилиту из корня `rest/`:
```bash
python utils/organize_models.py ../best.pt --description "soldier_detection_v1"
```

Или из текущей папки:
```bash
cd rest
python utils/organize_models.py best.pt --description "soldier_detection_v1"
```

### Ручная организация:

1. Скопируйте модель из `outputs/training/yolo_training/weights/best.pt`
2. Переименуйте с понятным именем
3. Поместите в эту папку

## Использование моделей

В `config/config.yaml` для дообучения укажите:

```yaml
resume_training:
  enabled: true
  model_path: "models/model_2025-12-20_soldier_detection_v1.pt"
```

Или просто имя файла (автоматически найдет в папке models):
```yaml
resume_training:
  enabled: true
  model_path: "model_2025-12-20_soldier_detection_v1.pt"
```

## Автоматическое сохранение

После обучения лучшая модель автоматически копируется в эту папку с именем:
`model_YYYY-MM-DD_soldier_detection.pt`

Если модель с таким именем уже существует, добавляется версия (v1, v2, etc.)

