"""
data_preparation.py
====================
Chargement, prétraitement et découpage (train / validation / test) du jeu de
données d'images de billets d'ariary.

Organisation attendue du dossier data/raw :

    data/raw/
        100/    *.jpg | *.png
        200/
        500/
        1000/
        2000/
        5000/
        10000/
        20000/

Chaque sous-dossier porte le nom de la valeur faciale (label) et contient les
photographies (ou images de démonstration) correspondantes.
"""

import os
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

IMG_SIZE = 96
CLASSES = [100, 200, 500, 1000, 2000, 5000, 10000, 20000]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}
IDX_TO_CLASS = {i: c for i, c in enumerate(CLASSES)}

VALID_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


def load_image(path, size=IMG_SIZE):
    """Charge une image, la convertit en RGB et la redimensionne."""
    img = Image.open(path).convert("RGB")
    img = img.resize((size, size))
    return np.asarray(img, dtype=np.float32) / 255.0


def load_dataset(raw_dir="data/raw", size=IMG_SIZE):
    """Parcourt data/raw/<classe>/*.ext et construit les tableaux X, y."""
    raw_dir = Path(raw_dir)
    X, y, paths = [], [], []

    for class_value in CLASSES:
        class_dir = raw_dir / str(class_value)
        if not class_dir.exists():
            print(f"[ATTENTION] Dossier manquant pour la classe {class_value} : {class_dir}")
            continue
        files = [f for f in class_dir.iterdir() if f.suffix.lower() in VALID_EXT]
        for f in files:
            try:
                X.append(load_image(f, size))
                y.append(CLASS_TO_IDX[class_value])
                paths.append(str(f))
            except Exception as e:
                print(f"[ERREUR] Impossible de lire {f} : {e}")

    if not X:
        raise RuntimeError(
            "Aucune image trouvée dans data/raw. "
            "Générez d'abord un jeu de démonstration avec "
            "'python src/generate_demo_dataset.py' ou placez vos propres photos."
        )

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    return X, y, paths


def split_dataset(X, y, test_size=0.15, val_size=0.15, seed=42):
    """Découpe en train / validation / test de façon stratifiée."""
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(test_size + val_size), stratify=y, random_state=seed
    )
    relative_val = val_size / (test_size + val_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=(1 - relative_val), stratify=y_temp, random_state=seed
    )
    return X_train, y_train, X_val, y_val, X_test, y_test


if __name__ == "__main__":
    X, y, paths = load_dataset()
    print(f"Images chargées : {X.shape}, labels : {y.shape}")
    X_train, y_train, X_val, y_val, X_test, y_test = split_dataset(X, y)
    print(f"Train : {X_train.shape[0]}  Val : {X_val.shape[0]}  Test : {X_test.shape[0]}")
