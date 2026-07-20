"""
model.py
========
Chargement du modèle Ultralytics YOLO utilisé pour la reconnaissance des
billets d'ariary.

Le projet utilise par défaut un modèle de classification YOLOv8
(`yolov8n-cls.pt`) affiné sur les dossiers `data/raw/<valeur>/`.
Un modèle YOLO de détection personnalisé peut aussi être chargé pour la
prédiction si ses classes correspondent aux coupures d'ariary.
"""

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BASE_MODEL = "yolov8n-cls.pt"
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "ariary_yolo_cls.pt"


def _import_yolo():
    config_dir = ROOT_DIR / "results" / ".ultralytics"
    matplotlib_dir = ROOT_DIR / "results" / ".matplotlib"
    config_dir.mkdir(parents=True, exist_ok=True)
    matplotlib_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(config_dir))
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_dir))

    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Le paquet 'ultralytics' est introuvable. "
            "Installez les dépendances avec : pip install -r requirements.txt"
        ) from exc
    return YOLO


def build_yolo_model(base_model=DEFAULT_BASE_MODEL):
    """Construit un modèle Ultralytics depuis un checkpoint de base."""
    YOLO = _import_yolo()
    return YOLO(str(base_model))


def load_yolo_model(
    model_path=DEFAULT_MODEL_PATH,
    *,
    allow_base_fallback=False,
    base_model=DEFAULT_BASE_MODEL,
):
    """Charge le modèle entraîné.

    `allow_base_fallback=True` est utile pour l'entraînement, car Ultralytics
    télécharge alors le checkpoint de base si nécessaire. Pour la prédiction de
    billets, on préfère échouer clairement si le modèle entraîné n'existe pas.
    """
    model_path = Path(model_path)
    if model_path.exists():
        source = model_path
    elif allow_base_fallback:
        source = base_model
    else:
        raise FileNotFoundError(
            f"Modèle introuvable : {model_path}. "
            "Lancez d'abord : python src/train.py"
        )

    YOLO = _import_yolo()
    return YOLO(str(source))


if __name__ == "__main__":
    model = load_yolo_model(allow_base_fallback=True)
    print(model)
