"""Наивное обучение YOLO через PyTorch DataLoader."""

from pathlib import Path
from typing import List, Tuple

import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from loguru import logger
from ultralytics import YOLO


class YoloDetectionDataset(Dataset):
    """Очень простой датасет: читает изображения и YOLO txt лейблы."""

    def __init__(self, images_dir: Path, labels_dir: Path, image_size: int = 640):
        self.images: List[Path] = [
            p for p in images_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]
        self.labels_dir = labels_dir
        self.image_size = image_size

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx: int):
        img_path = self.images[idx]
        lbl_path = self.labels_dir / f"{img_path.stem}.txt"

        img = Image.open(img_path).convert("RGB").resize((self.image_size, self.image_size))
        import numpy as np

        arr = np.array(img, dtype=np.float32) / 255.0  # HWC
        img_tensor = torch.from_numpy(arr).permute(2, 0, 1)  # CHW

        boxes = []
        if lbl_path.exists():
            with open(lbl_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    _, x, y, w, h = map(float, parts)
                    boxes.append([x, y, w, h])

        if boxes:
            boxes_tensor = torch.tensor(boxes, dtype=torch.float32)
        else:
            boxes_tensor = torch.zeros((0, 4), dtype=torch.float32)

        cls_tensor = torch.zeros((boxes_tensor.shape[0], 1), dtype=torch.float32)

        target = {
            "bboxes": boxes_tensor,
            "cls": cls_tensor,
            "batch_idx": torch.zeros((boxes_tensor.shape[0], 1), dtype=torch.float32),
        }
        return img_tensor, target


def simple_collate(batch: List[Tuple[torch.Tensor, dict]]):
    images, targets = zip(*batch)
    images = torch.stack(images, dim=0)

    all_boxes = []
    all_cls = []
    all_batch_idx = []
    for i, t in enumerate(targets):
        if t["bboxes"].shape[0] == 0:
            continue
        all_boxes.append(t["bboxes"])
        all_cls.append(t["cls"])
        all_batch_idx.append(torch.full((t["bboxes"].shape[0], 1), float(i)))

    if all_boxes:
        boxes = torch.cat(all_boxes, dim=0)
        cls = torch.cat(all_cls, dim=0)
        batch_idx = torch.cat(all_batch_idx, dim=0)
    else:
        boxes = torch.zeros((0, 4), dtype=torch.float32)
        cls = torch.zeros((0, 1), dtype=torch.float32)
        batch_idx = torch.zeros((0, 1), dtype=torch.float32)

    return images, {"bboxes": boxes, "cls": cls, "batch_idx": batch_idx}


class YoloTrainPipeline:
    """Минимальный цикл обучения для YOLO модели."""

    def __init__(self, config: dict):
        self.config = config.get("training", {})

    def _build_loader(self, dataset_root: Path):
        train_dir = dataset_root / "train"
        images_dir = train_dir / "images"
        labels_dir = train_dir / "labels"
        ds = YoloDetectionDataset(images_dir, labels_dir, self.config.get("image_size", 640))
        loader = DataLoader(
            ds,
            batch_size=self.config.get("batch_size", 8),
            shuffle=True,
            num_workers=self.config.get("num_workers", 2),
            collate_fn=simple_collate,
        )
        return loader

    def run(self, dataset_root: Path, output_dir: Path, finetune: bool = False):
        train_loader = self._build_loader(dataset_root)
        device = self.config.get("device", "cuda")

        if finetune:
            finetune_path = self.config.get("finetune_model", "models/best.pt")
            model = YOLO(finetune_path)
            logger.info(f"Файнтюним модель из {finetune_path}")
        else:
            model_name = self.config.get("model", "yolo11n.pt")
            model = YOLO(model_name)
            logger.info(f"Обучаем с нуля модель {model_name}")

        model.model.to(device)
        model.model.train()

        optimizer = torch.optim.Adam(
            model.model.parameters(),
            lr=self.config.get("lr", 1e-3),
            weight_decay=self.config.get("weight_decay", 5e-4),
        )

        epochs = self.config.get("epochs", 5)
        output_dir.mkdir(parents=True, exist_ok=True)
        weights_dir = output_dir / "training"
        weights_dir.mkdir(parents=True, exist_ok=True)

        for epoch in range(epochs):
            total_loss = 0.0
            for images, targets in train_loader:
                images = images.to(device)
                targets = {
                    "img": images,
                    "bboxes": targets["bboxes"].to(device),
                    "cls": targets["cls"].to(device),
                    "batch_idx": targets["batch_idx"].to(device),
                }

                optimizer.zero_grad()
                preds = model.model(images)
                loss, _ = model.model.loss(preds, targets)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / max(len(train_loader), 1)
            logger.info(f"Эпоха {epoch+1}/{epochs} | loss={avg_loss:.4f}")

            # Сохраняем веса после каждой эпохи (по-простому)
            torch.save(model.model.state_dict(), weights_dir / f"epoch_{epoch+1}.pt")

        logger.info(f"Обучение завершено, веса в {weights_dir}")

