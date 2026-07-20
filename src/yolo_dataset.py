"""
yolo_dataset.py
===============
Prépare un dataset de classification compatible Ultralytics à partir de
l'organisation existante :

    data/raw/<valeur>/*.jpg

Ultralytics attend plutôt :

    data/yolo_cls/
        train/<valeur>/*.jpg
        val/<valeur>/*.jpg
        test/<valeur>/*.jpg
"""

from __future__ import annotations

import hashlib
import json
import random
import shutil
from pathlib import Path

from data_preparation import CLASSES, VALID_EXT


DEFAULT_YOLO_DATASET_DIR = Path("data/yolo_cls")
SPLITS = ("train", "val", "test")


def collect_class_images(raw_dir="data/raw"):
    raw_dir = Path(raw_dir)
    images_by_class = {}

    for class_value in CLASSES:
        class_dir = raw_dir / str(class_value)
        if not class_dir.exists():
            images_by_class[class_value] = []
            continue

        images_by_class[class_value] = sorted(
            path
            for path in class_dir.iterdir()
            if path.is_file() and path.suffix.lower() in VALID_EXT
        )

    return images_by_class


def _split_files(files, val_size=0.15, test_size=0.15, seed=42):
    files = list(files)
    rng = random.Random(seed)
    rng.shuffle(files)

    total = len(files)
    if total < 3:
        return {"train": files, "val": [], "test": []}

    n_test = max(1, round(total * test_size))
    n_val = max(1, round(total * val_size))

    if n_test + n_val >= total:
        n_test = 1
        n_val = 1 if total > 2 else 0

    return {
        "test": files[:n_test],
        "val": files[n_test:n_test + n_val],
        "train": files[n_test + n_val:],
    }


def _copy_image(source, destination_dir):
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name
    if destination.exists():
        digest = hashlib.sha1(str(source).encode("utf-8")).hexdigest()[:8]
        destination = destination_dir / f"{source.stem}_{digest}{source.suffix}"
    shutil.copy2(source, destination)
    return destination


def _dataset_has_images(dataset_dir):
    dataset_dir = Path(dataset_dir)
    return any((dataset_dir / "train").glob("*/*"))


def prepare_yolo_classification_dataset(
    raw_dir="data/raw",
    output_dir=DEFAULT_YOLO_DATASET_DIR,
    *,
    val_size=0.15,
    test_size=0.15,
    seed=42,
    rebuild=False,
):
    """Crée ou réutilise le dataset de classification Ultralytics."""
    raw_dir = Path(raw_dir)
    output_dir = Path(output_dir)

    if output_dir.exists() and _dataset_has_images(output_dir) and not rebuild:
        return output_dir

    if rebuild and output_dir.exists():
        shutil.rmtree(output_dir)

    images_by_class = collect_class_images(raw_dir)
    if not any(images_by_class.values()):
        raise RuntimeError(f"Aucune image trouvée dans {raw_dir}.")

    counts = {
        split_name: {str(class_value): 0 for class_value in CLASSES}
        for split_name in SPLITS
    }

    for class_value, images in images_by_class.items():
        if not images:
            print(f"[ATTENTION] Aucune image pour la classe {class_value}.")
            continue

        split_files = _split_files(images, val_size=val_size, test_size=test_size, seed=seed)
        for split_name, files in split_files.items():
            destination_dir = output_dir / split_name / str(class_value)
            for source in files:
                _copy_image(source, destination_dir)
            counts[split_name][str(class_value)] = len(files)

    info = {
        "source_dir": str(raw_dir),
        "classes": [str(class_value) for class_value in CLASSES],
        "splits": counts,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "dataset_info.json", "w", encoding="utf-8") as file:
        json.dump(info, file, indent=2, ensure_ascii=False)

    return output_dir


def iter_split_images(dataset_dir=DEFAULT_YOLO_DATASET_DIR, split="test"):
    split_dir = Path(dataset_dir) / split
    if not split_dir.exists():
        raise FileNotFoundError(f"Split introuvable : {split_dir}")

    for class_dir in sorted(split_dir.iterdir(), key=lambda path: int(path.name)):
        if not class_dir.is_dir():
            continue
        class_value = int(class_dir.name)
        for image_path in sorted(class_dir.iterdir()):
            if image_path.is_file() and image_path.suffix.lower() in VALID_EXT:
                yield image_path, class_value
