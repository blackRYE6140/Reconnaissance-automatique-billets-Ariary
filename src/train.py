"""
train.py
========
Entraîne un modèle Ultralytics YOLO pour reconnaître la valeur faciale des
billets d'ariary.

Usage :
    python src/train.py --epochs 50 --batch_size 16

Par défaut, le script entraîne un modèle de classification YOLOv8
(`yolov8n-cls.pt`) à partir de `data/raw/<valeur>/`.
"""

import argparse
import shutil
from pathlib import Path

from model import DEFAULT_BASE_MODEL, DEFAULT_MODEL_PATH, build_yolo_model
from yolo_dataset import DEFAULT_YOLO_DATASET_DIR, prepare_yolo_classification_dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="data/raw")
    parser.add_argument("--dataset_out", default=str(DEFAULT_YOLO_DATASET_DIR))
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--base_model", default=DEFAULT_BASE_MODEL)
    parser.add_argument("--model_out", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--project", default="results/yolo")
    parser.add_argument("--name", default="ariary_yolo_cls")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val_size", type=float, default=0.15)
    parser.add_argument("--test_size", type=float, default=0.15)
    parser.add_argument(
        "--rebuild_dataset",
        action="store_true",
        help="Reconstruit data/yolo_cls depuis data/raw même si le dossier existe déjà.",
    )
    args = parser.parse_args()

    Path("models").mkdir(exist_ok=True)
    Path(args.project).mkdir(parents=True, exist_ok=True)

    print("Préparation du dataset Ultralytics...")
    dataset_dir = prepare_yolo_classification_dataset(
        args.data_dir,
        args.dataset_out,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
        rebuild=args.rebuild_dataset,
    )
    print(f"Dataset prêt : {dataset_dir}")

    print(f"Chargement du modèle de base : {args.base_model}")
    model = build_yolo_model(args.base_model)

    model.train(
        data=str(dataset_dir),
        epochs=args.epochs,
        batch=args.batch_size,
        imgsz=args.imgsz,
        lr0=args.lr,
        project=args.project,
        name=args.name,
        seed=args.seed,
        task="classify",
    )

    save_dir = Path(getattr(model.trainer, "save_dir", Path(args.project) / args.name))
    weights_dir = save_dir / "weights"
    best_model = weights_dir / "best.pt"
    last_model = weights_dir / "last.pt"
    trained_model = best_model if best_model.exists() else last_model

    if not trained_model.exists():
        raise RuntimeError(f"Checkpoint entraîné introuvable dans {weights_dir}.")

    model_out = Path(args.model_out)
    model_out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(trained_model, model_out)
    print(f"Modèle sauvegardé : {model_out}")
    print(f"Résultats Ultralytics : {save_dir}")


if __name__ == "__main__":
    main()
