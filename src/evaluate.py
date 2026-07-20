"""
evaluate.py
===========
Évalue le modèle YOLO entraîné sur le split de test et produit :
  - Accuracy, Precision, Recall, F1-score (macro et par classe)
  - Matrice de confusion (image + CSV)
  - Rapport de classification complet (results/classification_report.txt)
  - results/metrics.json (résumé chiffré, utile pour le rapport)

Usage :
    python src/evaluate.py
"""

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("results") / ".matplotlib"))

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
)

from data_preparation import CLASSES, CLASS_TO_IDX
from model import DEFAULT_MODEL_PATH, load_yolo_model
from predict import predict_image
from yolo_dataset import DEFAULT_YOLO_DATASET_DIR, iter_split_images, prepare_yolo_classification_dataset


def evaluate_model(model_path, dataset_dir, results_dir):
    results_dir = Path(results_dir)
    results_dir.mkdir(exist_ok=True)

    model = load_yolo_model(model_path)
    y_true = []
    y_pred = []

    test_images = list(iter_split_images(dataset_dir, split="test"))
    if not test_images:
        raise RuntimeError(f"Aucune image de test trouvée dans {Path(dataset_dir) / 'test'}.")

    for image_path, true_class in test_images:
        pred_class, _, _ = predict_image(image_path, model=model)
        y_true.append(CLASS_TO_IDX[true_class])
        y_pred.append(CLASS_TO_IDX[pred_class])

    y_true = np.array(y_true, dtype=np.int64)
    y_pred = np.array(y_pred, dtype=np.int64)

    acc = accuracy_score(y_true, y_pred)
    prec_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
    rec_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)

    labels_str = [str(class_value) for class_value in CLASSES]
    label_indices = list(range(len(CLASSES)))

    report_txt = classification_report(
        y_true,
        y_pred,
        labels=label_indices,
        target_names=labels_str,
        zero_division=0,
    )
    print(report_txt)
    print(f"Accuracy globale : {acc:.4f}")
    print(f"Precision (macro): {prec_macro:.4f}")
    print(f"Recall    (macro): {rec_macro:.4f}")
    print(f"F1-score  (macro): {f1_macro:.4f}")

    with open(results_dir / "classification_report.txt", "w", encoding="utf-8") as file:
        file.write(report_txt)

    metrics_summary = {
        "accuracy": float(acc),
        "precision_macro": float(prec_macro),
        "recall_macro": float(rec_macro),
        "f1_macro": float(f1_macro),
        "n_test_samples": int(len(y_true)),
        "model_path": str(model_path),
        "dataset_dir": str(dataset_dir),
    }
    with open(results_dir / "metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics_summary, file, indent=2)

    per_class = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=label_indices,
        zero_division=0,
    )
    per_class_list = []
    for index, class_value in enumerate(CLASSES):
        per_class_list.append({
            "classe": class_value,
            "precision": float(per_class[0][index]),
            "recall": float(per_class[1][index]),
            "f1": float(per_class[2][index]),
            "support": int(per_class[3][index]),
        })
    with open(results_dir / "per_class_metrics.json", "w", encoding="utf-8") as file:
        json.dump(per_class_list, file, indent=2)

    cm = confusion_matrix(y_true, y_pred, labels=label_indices)
    np.savetxt(results_dir / "confusion_matrix.csv", cm, fmt="%d", delimiter=",")

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels_str, yticklabels=labels_str)
    plt.xlabel("Classe prédite")
    plt.ylabel("Classe réelle")
    plt.title("Matrice de confusion - YOLO Ariary")
    plt.tight_layout()
    plt.savefig(results_dir / "matrice_confusion.png", dpi=150)
    print(f"\nRésultats enregistrés dans '{results_dir}/'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="data/raw")
    parser.add_argument("--dataset_dir", default=str(DEFAULT_YOLO_DATASET_DIR))
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--results_dir", default="results")
    parser.add_argument("--rebuild_dataset", action="store_true")
    args = parser.parse_args()

    dataset_dir = prepare_yolo_classification_dataset(
        args.data_dir,
        args.dataset_dir,
        rebuild=args.rebuild_dataset,
    )
    evaluate_model(args.model, dataset_dir, args.results_dir)


if __name__ == "__main__":
    main()
