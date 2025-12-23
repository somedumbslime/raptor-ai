"""Обучение YOLO модели с интеграцией MLflow"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import mlflow
from ultralytics import YOLO
from loguru import logger


def train_yolo_with_mlflow(
    config: Dict[str, Any], data_yaml: str, output_dir: str, base_path: Path = None
) -> dict:
    """
    Обучение YOLO модели с полным трекингом в MLflow

    Args:
        config: Конфигурация обучения из config.yaml
        data_yaml: Путь к YAML файлу с конфигурацией датасета
        output_dir: Папка для сохранения результатов
        base_path: Базовый путь проекта (для поиска моделей)

    Returns:
        Словарь с результатами обучения
    """
    if base_path is None:
        base_path = Path(output_dir).parent

    # Настройки MLflow
    mlflow_config = config.get("mlflow", {})
    tracking_uri = mlflow_config.get("tracking_uri", "runs/mlflow")
    experiment_name = mlflow_config.get("experiment_name", "yolo_training")
    log_artifacts = mlflow_config.get("log_artifacts", True)
    log_images = mlflow_config.get("log_images", True)
    log_model = mlflow_config.get("log_model", True)

    # Создаем папку для MLflow
    tracking_path = Path(tracking_uri)
    tracking_path.mkdir(parents=True, exist_ok=True)

    # Настраиваем MLflow
    # MLflow требует file:// префикс для локальных путей
    # На Windows нужно использовать правильное кодирование пути с пробелами и кириллицей
    import platform
    from urllib.request import pathname2url

    abs_path = tracking_path.absolute()
    if platform.system() == "Windows":
        # Используем pathname2url для правильного кодирования пути
        # Это автоматически обработает пробелы и кириллицу
        encoded_path = pathname2url(str(abs_path))
        # Для Windows нужен формат file:///C:/path (3 слеша)
        mlflow_uri = f"file:{encoded_path}"
    else:
        mlflow_uri = f"file://{abs_path}"

    mlflow.set_tracking_uri(mlflow_uri)
    logger.debug(f"MLflow tracking URI установлен: {mlflow_uri}")

    # Создаем или получаем эксперимент
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"Создан новый эксперимент MLflow: {experiment_name}")
        else:
            experiment_id = experiment.experiment_id
            logger.info(
                f"Используется существующий эксперимент MLflow: {experiment_name}"
            )
    except Exception as e:
        logger.warning(f"Ошибка при работе с экспериментом MLflow: {e}. Создаем новый.")
        experiment_id = mlflow.create_experiment(experiment_name)

    # Параметры обучения
    model_name = config.get("model", "yolo11n.pt")
    epochs = config.get("epochs", 100)
    imgsz = config.get("imgsz", 640)
    batch = config.get("batch", 16)
    device = config.get("device", "cuda")
    workers = config.get("workers", 8)
    cache = config.get("cache", True)
    lr0 = config.get("lr0", 0.01)
    lrf = config.get("lrf", 0.01)
    save_period = config.get("save_period", 10)
    patience = config.get("patience", 50)

    # Параметры дообучения
    resume_config = config.get("resume_training", {})
    resume_enabled = resume_config.get("enabled", False)
    resume_model_path = resume_config.get("model_path", None)
    resume_from_checkpoint = resume_config.get("resume_from_checkpoint", False)
    fine_tune_lr0 = resume_config.get("fine_tune_lr0", None)

    # Параметры аугментации
    augment_config = config.get("augment", {})

    # Настройки проекта
    project_dir = Path(output_dir) / "training"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Получаем путь к папке models из конфигурации
    paths_config = config.get("paths", {}) if "paths" in config else {}
    models_dir_path = None
    if base_path and paths_config.get("models_dir"):
        models_dir_path = base_path / paths_config["models_dir"]
        # Создаем папку models, если её нет
        models_dir_path.mkdir(parents=True, exist_ok=True)

    # Определяем модель для загрузки (дообучение или с нуля)
    actual_model_path = model_name
    is_resume_training = False
    start_epoch = 0

    if resume_enabled:
        if resume_model_path:
            # Определяем полный путь к модели для дообучения
            if resume_model_path in ["best.pt", "last.pt"]:
                # Относительные пути - ищем в предыдущей директории обучения
                prev_training_dir = (
                    Path(output_dir) / "training" / "yolo_training" / "weights"
                )
                resume_model_full_path = prev_training_dir / resume_model_path

                if not resume_model_full_path.exists():
                    # Пробуем найти в других возможных местах
                    # Определяем базовую папку rest
                    rest_dir = (
                        Path(output_dir).parent
                        if "rest" in str(output_dir)
                        else Path(output_dir)
                    )
                    base_project_dir = (
                        rest_dir.parent if rest_dir.name == "rest" else rest_dir
                    )

                    possible_paths = []

                    # Добавляем папку models (приоритетная)
                    if models_dir_path:
                        possible_paths.append(models_dir_path / resume_model_path)

                    # Стандартные места обучения
                    possible_paths.extend(
                        [
                            Path(output_dir)
                            / "training"
                            / "yolo_training"
                            / "weights"
                            / resume_model_path,
                            rest_dir
                            / "outputs"
                            / "training"
                            / "yolo_training"
                            / "weights"
                            / resume_model_path,
                            rest_dir / "models" / resume_model_path,
                            rest_dir / resume_model_path,
                            base_project_dir / resume_model_path,
                            base_project_dir / "rest" / resume_model_path,
                            Path(output_dir).parent
                            / "training"
                            / "yolo_training"
                            / "weights"
                            / resume_model_path,
                        ]
                    )

                    # Также проверяем runs/detect для совместимости со старыми экспериментами
                    if base_project_dir:
                        runs_detect_dir = base_project_dir / "runs" / "detect"
                        if runs_detect_dir.exists():
                            for train_dir in runs_detect_dir.iterdir():
                                if train_dir.is_dir():
                                    weights_file = (
                                        train_dir / "weights" / resume_model_path
                                    )
                                    if weights_file.exists():
                                        possible_paths.append(weights_file)

                    logger.debug(
                        f"Поиск модели {resume_model_path} в следующих местах:"
                    )
                    for path in possible_paths:
                        logger.debug(f"  - {path}")
                        if path.exists():
                            resume_model_full_path = path
                            logger.info(f"✅ Модель найдена: {resume_model_full_path}")
                            break
                    else:
                        # Формируем список проверенных путей для сообщения об ошибке
                        checked_paths_str = "\n".join(
                            [f"  - {p}" for p in possible_paths[:5]]
                        )
                        raise FileNotFoundError(
                            f"Модель для дообучения '{resume_model_path}' не найдена.\n"
                            f"Проверенные места:\n{checked_paths_str}\n"
                            f"Рекомендация: переместите модель в папку 'rest/models/' или укажите полный путь в model_path"
                        )
            else:
                # Абсолютный или относительный путь
                resume_model_full_path = Path(resume_model_path)
                if not resume_model_full_path.is_absolute():
                    resume_model_full_path = Path(output_dir).parent / resume_model_path

                if not resume_model_full_path.exists():
                    raise FileNotFoundError(
                        f"Модель для дообучения не найдена: {resume_model_full_path}"
                    )

            actual_model_path = str(resume_model_full_path.absolute())
            is_resume_training = True

            # Проверяем, можно ли продолжить обучение (resume=True)
            if resume_from_checkpoint and resume_model_path == "last.pt":
                logger.info(
                    "🔄 Продолжение обучения с последнего чекпоинта (resume=True)"
                )
            else:
                logger.info(f"🔄 Дообучение модели: {actual_model_path}")
                logger.info("   (Обучение начнется с эпохи 0, используя веса модели)")
        else:
            # Используем базовую модель, но логируем что это дообучение
            logger.warning(
                "resume_training.enabled=True, но model_path не указан. Используется базовая модель."
            )
            is_resume_training = True

    logger.info("=" * 80)
    if is_resume_training:
        logger.info("НАЧАЛО ДООБУЧЕНИЯ YOLO МОДЕЛИ")
    else:
        logger.info("НАЧАЛО ОБУЧЕНИЯ YOLO МОДЕЛИ")
    logger.info("=" * 80)
    logger.info(f"Модель: {actual_model_path}")
    logger.info(f"Датасет: {data_yaml}")
    logger.info(f"Эпох: {epochs}")
    logger.info(f"Размер изображения: {imgsz}")
    logger.info(f"Batch size: {batch}")
    logger.info(f"Устройство: {device}")
    logger.info(f"MLflow эксперимент: {experiment_name}")

    # Используем fine-tune learning rate, если указан
    actual_lr0 = (
        fine_tune_lr0 if (fine_tune_lr0 is not None and is_resume_training) else lr0
    )
    if is_resume_training and fine_tune_lr0 is not None:
        logger.info(f"Learning rate для дообучения: {actual_lr0} (вместо {lr0})")

    # Начинаем MLflow run
    with mlflow.start_run(experiment_id=experiment_id) as run:
        run_id = run.info.run_id
        logger.info(f"MLflow Run ID: {run_id}")

        # Логируем параметры
        mlflow.log_params(
            {
                "model": actual_model_path if is_resume_training else model_name,
                "is_resume_training": is_resume_training,
                "epochs": epochs,
                "imgsz": imgsz,
                "batch": batch,
                "device": device,
                "workers": workers,
                "lr0": actual_lr0,  # Используем актуальный LR
                "lrf": lrf,
                "patience": patience,
            }
        )

        # Дополнительные параметры для дообучения
        if is_resume_training:
            mlflow.log_params(
                {
                    "resume_model_path": str(actual_model_path),
                    "resume_from_checkpoint": (
                        resume_from_checkpoint if resume_enabled else False
                    ),
                    "fine_tune_lr0": (
                        fine_tune_lr0 if fine_tune_lr0 is not None else "default"
                    ),
                }
            )

        # Логируем параметры аугментации
        if augment_config:
            mlflow.log_params({f"augment_{k}": v for k, v in augment_config.items()})

        # Логируем путь к датасету
        mlflow.log_param("data_yaml", str(Path(data_yaml).absolute()))

        try:
            # Загружаем модель
            logger.info(f"Загрузка модели {actual_model_path}...")
            model = YOLO(actual_model_path)

            # Подготавливаем параметры для обучения
            train_args = {
                "data": data_yaml,
                "epochs": epochs,
                "imgsz": imgsz,
                "batch": batch,
                "device": device,
                "workers": workers,
                "lr0": actual_lr0,  # Используем актуальный LR (может быть изменен для fine-tuning)
                "lrf": lrf,
                "patience": patience,
                "project": str(project_dir),
                "name": "yolo_training",
                "save_period": save_period,
                "exist_ok": True,
                "verbose": True,
            }

            # Добавляем resume параметр, если нужно продолжить обучение
            # В YOLO resume должен быть True или путь к last.pt чекпоинту
            if is_resume_training and resume_from_checkpoint:
                # Если используем last.pt, передаем путь к модели для resume
                if resume_model_path == "last.pt":
                    train_args["resume"] = actual_model_path
                    logger.info(
                        f"Параметр resume={actual_model_path} установлен - обучение продолжится с последнего состояния"
                    )
                else:
                    # Для других путей также можно использовать resume
                    train_args["resume"] = actual_model_path
                    logger.info(
                        f"Параметр resume={actual_model_path} установлен - попытка продолжить обучение"
                    )

            # Добавляем параметры кеширования
            if cache:
                train_args["cache"] = "ram" if device == "cuda" else "disk"

            # Добавляем параметры аугментации
            if augment_config:
                train_args.update(augment_config)

            # Запускаем обучение
            logger.info("Запуск обучения...")
            results = model.train(**train_args)

            # Получаем путь к лучшей модели
            best_model_path = (
                Path(project_dir) / "yolo_training" / "weights" / "best.pt"
            )

            # Также копируем лучшую модель в папку models с понятным именем (опционально)
            if models_dir_path and best_model_path.exists():
                try:
                    from datetime import datetime

                    date_str = datetime.now().strftime("%Y-%m-%d")
                    model_copy_name = f"model_{date_str}_soldier_detection.pt"
                    model_copy_path = models_dir_path / model_copy_name

                    # Проверяем, существует ли уже такая модель
                    counter = 1
                    while model_copy_path.exists():
                        model_copy_name = (
                            f"model_{date_str}_soldier_detection_v{counter}.pt"
                        )
                        model_copy_path = models_dir_path / model_copy_name
                        counter += 1

                    import shutil

                    shutil.copy2(str(best_model_path), str(model_copy_path))
                    logger.info(
                        f"📦 Копия лучшей модели сохранена в: {model_copy_path}"
                    )
                except Exception as e:
                    logger.warning(f"Не удалось скопировать модель в папку models: {e}")

            if not best_model_path.exists():
                # Пробуем альтернативный путь
                runs_dir = Path(project_dir) / "yolo_training"
                if runs_dir.exists():
                    weights_dir = list(runs_dir.glob("weights"))
                    if weights_dir:
                        best_model_path = weights_dir[0] / "best.pt"

            logger.info(f"Обучение завершено!")
            logger.info(f"Лучшая модель: {best_model_path}")

            # Логируем метрики из результатов обучения
            if hasattr(results, "results_dict"):
                metrics = results.results_dict
                # Фильтруем только числовые метрики
                numeric_metrics = {
                    k: v
                    for k, v in metrics.items()
                    if isinstance(v, (int, float)) and not k.startswith("_")
                }
                mlflow.log_metrics(numeric_metrics)
                logger.info("Метрики залогированы в MLflow")

            # Логируем артефакты
            if log_artifacts and best_model_path.exists():
                # Логируем лучшую модель
                if log_model:
                    mlflow.log_artifact(str(best_model_path), artifact_path="models")
                    logger.info("Модель залогирована в MLflow")

                # Логируем графики и результаты обучения
                train_dir = best_model_path.parent.parent
                for artifact_file in [
                    "results.png",
                    "confusion_matrix.png",
                    "F1_curve.png",
                    "PR_curve.png",
                    "results.csv",
                ]:
                    artifact_path = train_dir / artifact_file
                    if artifact_path.exists():
                        mlflow.log_artifact(
                            str(artifact_path), artifact_path="training_results"
                        )
                        logger.info(f"Артефакт залогирован: {artifact_file}")

                # Логируем валидационные изображения с предсказаниями
                if log_images:
                    val_images_dir = train_dir / "val_batch0_pred.jpg"
                    if val_images_dir.exists():
                        mlflow.log_artifact(
                            str(val_images_dir), artifact_path="validation_images"
                        )

            # Логируем data.yaml
            data_yaml_path = Path(data_yaml)
            if data_yaml_path.exists():
                mlflow.log_artifact(str(data_yaml_path), artifact_path="dataset")

            logger.info("=" * 80)
            logger.info("ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
            logger.info("=" * 80)
            logger.info(f"MLflow Run ID: {run_id}")
            logger.info(f"Для просмотра результатов запустите:")
            logger.info(f"  mlflow ui --backend-store-uri {tracking_path.absolute()}")

            return {
                "success": True,
                "run_id": run_id,
                "best_model_path": str(best_model_path),
                "metrics": numeric_metrics if "numeric_metrics" in locals() else {},
                "mlflow_uri": str(tracking_path.absolute()),
            }

        except Exception as e:
            logger.error(f"Ошибка при обучении: {e}")
            mlflow.log_param("error", str(e))
            raise


def load_best_model(model_path: str) -> YOLO:
    """
    Загрузка лучшей обученной модели

    Args:
        model_path: Путь к файлу модели .pt

    Returns:
        Загруженная YOLO модель
    """
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Модель не найдена: {model_path}")

    logger.info(f"Загрузка модели из {model_path}")
    model = YOLO(model_path)
    return model
