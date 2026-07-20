"""
predict.py
==========
Prédiction en ligne de commande sur une image unique avec Ultralytics YOLO et
OpenCV.

Usage :
    python src/predict.py chemin/vers/image.jpg
"""

import argparse
import re
from pathlib import Path

import numpy as np

from data_preparation import CLASSES
from model import DEFAULT_MODEL_PATH, load_yolo_model


CLASS_SET = set(CLASSES)


def _import_cv2():
    try:
        import cv2
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Le paquet 'opencv-python' est introuvable. "
            "Installez les dépendances avec : pip install -r requirements.txt"
        ) from exc
    return cv2


def read_image_bgr(image_source):
    if isinstance(image_source, np.ndarray):
        return image_source

    cv2 = _import_cv2()
    image_path = Path(image_source)
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Impossible de lire l'image : {image_path}")
    return image


def _class_value_from_name(name):
    if isinstance(name, (int, np.integer)):
        return CLASSES[int(name)] if 0 <= int(name) < len(CLASSES) else None

    match = re.search(r"\d+", str(name).replace(" ", ""))
    if not match:
        return None

    value = int(match.group(0))
    return value if value in CLASS_SET else None


def _name_for_index(names, index):
    if isinstance(names, dict):
        return names.get(index, index)
    if isinstance(names, (list, tuple)) and 0 <= index < len(names):
        return names[index]
    return index


def _scores_from_classification(result):
    probs = getattr(result, "probs", None)
    if probs is None:
        return None

    raw_probs = probs.data.detach().cpu().numpy().astype(float)
    names = getattr(result, "names", {}) or {}
    scores = {class_value: 0.0 for class_value in CLASSES}

    for index, probability in enumerate(raw_probs):
        class_value = _class_value_from_name(_name_for_index(names, index))
        if class_value is not None:
            scores[class_value] = float(probability)

    return scores if any(scores.values()) else None


def _scores_from_detection(result):
    boxes = getattr(result, "boxes", None)
    if boxes is None or boxes.cls is None or boxes.conf is None:
        return None

    names = getattr(result, "names", {}) or {}
    scores = {class_value: 0.0 for class_value in CLASSES}

    class_ids = boxes.cls.detach().cpu().numpy().astype(int)
    confidences = boxes.conf.detach().cpu().numpy().astype(float)
    for class_id, confidence in zip(class_ids, confidences):
        class_value = _class_value_from_name(_name_for_index(names, int(class_id)))
        if class_value is not None:
            scores[class_value] = max(scores[class_value], float(confidence))

    return scores if any(scores.values()) else None


def scores_from_result(result):
    scores = _scores_from_classification(result)
    if scores is None:
        scores = _scores_from_detection(result)
    if scores is None:
        raise ValueError(
            "Le modèle YOLO ne contient pas de classes Ariary reconnues "
            "(100, 200, 500, 1000, 2000, 5000, 10000, 20000)."
        )
    return scores


def predict_image(image_source, model=None, model_path=DEFAULT_MODEL_PATH):
    if model is None:
        model = load_yolo_model(model_path)

    image = read_image_bgr(image_source)
    result = model.predict(source=image, verbose=False)[0]
    scores = scores_from_result(result)

    pred_class = max(scores, key=scores.get)
    confidence = float(scores[pred_class])
    probabilities = np.array([scores[class_value] for class_value in CLASSES], dtype=np.float32)
    return pred_class, confidence, probabilities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH))
    args = parser.parse_args()

    pred_class, confidence, probabilities = predict_image(args.image_path, model_path=args.model)
    print(f"Billet prédit : {pred_class} Ariary (confiance : {confidence * 100:.1f}%)")
    print("\nDétail des scores :")
    for class_value, probability in zip(CLASSES, probabilities):
        print(f"  {class_value:>6} Ar : {probability * 100:5.1f}%")


if __name__ == "__main__":
    main()
