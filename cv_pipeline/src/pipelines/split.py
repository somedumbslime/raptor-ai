"""Простейший сплит датасета на train/val/test."""

import random
import shutil
from pathlib import Path
from loguru import logger


class DatasetSplitPipeline:
    """Делит уже размеченный датасет на три части."""

    def __init__(self, config: dict):
        self.config = config.get("split", {})

    def _copy_pair(self, img_path: Path, lbl_path: Path, dest_img: Path, dest_lbl: Path):
        dest_img.parent.mkdir(parents=True, exist_ok=True)
        dest_lbl.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img_path, dest_img)
        if lbl_path.exists():
            shutil.copy2(lbl_path, dest_lbl)

    def run(self, dataset_root: Path):
        images_dir = dataset_root / "images"
        labels_dir = dataset_root / "labels"
        if not images_dir.exists():
            logger.warning(f"Папка {images_dir} не найдена, сплит пропускаем")
            return

        imgs = [p for p in images_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        if not imgs:
            logger.warning("Нет изображений для сплита")
            return

        train_r = float(self.config.get("train", 0.8))
        val_r = float(self.config.get("val", 0.1))
        seed = int(self.config.get("seed", 42))
        random.seed(seed)
        random.shuffle(imgs)

        train_cut = int(len(imgs) * train_r)
        val_cut = int(len(imgs) * (train_r + val_r))

        splits = {
            "train": imgs[:train_cut],
            "val": imgs[train_cut:val_cut],
            "test": imgs[val_cut:],
        }

        for split_name, files in splits.items():
            for img in files:
                lbl = labels_dir / f"{img.stem}.txt"
                self._copy_pair(
                    img,
                    lbl,
                    dataset_root / split_name / "images" / img.name,
                    dataset_root / split_name / "labels" / f"{img.stem}.txt",
                )

        logger.info(
            f"Сплит готов: train={len(splits['train'])}, val={len(splits['val'])}, test={len(splits['test'])}"
        )

