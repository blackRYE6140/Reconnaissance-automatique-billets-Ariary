# Reconnaissance automatique des billets d'ariary

Le système utilise Ultralytics YOLO et OpenCV pour identifier automatiquement
la valeur faciale d'un billet d'ariary (monnaie de Madagascar, MGA) à partir
d'une photographie, avec une interface graphique de démonstration (Tkinter).

## 1. Sujet

> Reconnaissance automatique des billets d'ariary — fournir un ouvrage
> contenant une étude bibliographique, une revue des travaux existants, une
> implémentation en Python, un jeu de données documenté, une analyse des
> résultats avec métriques, une démonstration du modèle, et le code source
> commenté et publié sur un dépôt Git.

Les 8 coupures reconnues (série en circulation, BFM) : **100, 200, 500,
1 000, 2 000, 5 000, 10 000, 20 000 Ariary**.

## 2. Structure du dépôt

```
projet_ariary/
├── [data/](data)
│   ├── [raw/](data/raw)                  # images brutes classées par dossier (label = valeur faciale)
│   │   ├── [100/](data/raw/100)
│   │   ├── [200/](data/raw/200)
│   │   ├── [500/](data/raw/500)
│   │   ├── [1000/](data/raw/1000)
│   │   ├── [2000/](data/raw/2000)
│   │   ├── [5000/](data/raw/5000)
│   │   ├── [10000/](data/raw/10000)
│   │   └── [20000/](data/raw/20000)
│   └── [yolo_cls/](data/yolo_cls)             # dataset au format Ultralytics classification
│       ├── [dataset_info.json](data/yolo_cls/dataset_info.json)
│       ├── [test/](data/yolo_cls/test)
│       │   ├── [100/](data/yolo_cls/test/100)
│       │   ├── [200/](data/yolo_cls/test/200)
│       │   ├── [500/](data/yolo_cls/test/500)
│       │   ├── [1000/](data/yolo_cls/test/1000)
│       │   ├── [2000/](data/yolo_cls/test/2000)
│       │   ├── [5000/](data/yolo_cls/test/5000)
│       │   ├── [10000/](data/yolo_cls/test/10000)
│       │   └── [20000/](data/yolo_cls/test/20000)
│       ├── [train/](data/yolo_cls/train)
│       │   ├── [100/](data/yolo_cls/train/100)
│       │   ├── [200/](data/yolo_cls/train/200)
│       │   ├── [500/](data/yolo_cls/train/500)
│       │   ├── [1000/](data/yolo_cls/train/1000)
│       │   ├── [2000/](data/yolo_cls/train/2000)
│       │   ├── [5000/](data/yolo_cls/train/5000)
│       │   ├── [10000/](data/yolo_cls/train/10000)
│       │   └── [20000/](data/yolo_cls/train/20000)
│       └── [val/](data/yolo_cls/val)
│           ├── [100/](data/yolo_cls/val/100)
│           ├── [200/](data/yolo_cls/val/200)
│           ├── [500/](data/yolo_cls/val/500)
│           ├── [1000/](data/yolo_cls/val/1000)
│           ├── [2000/](data/yolo_cls/val/2000)
│           ├── [5000/](data/yolo_cls/val/5000)
│           ├── [10000/](data/yolo_cls/val/10000)
│           └── [20000/](data/yolo_cls/val/20000)
├── [src/](src)
│   ├── [data_preparation.py](src/data_preparation.py)       # constantes des classes et helpers historiques
│   ├── [yolo_dataset.py](src/yolo_dataset.py)           # conversion data/raw -> data/yolo_cls
│   ├── [model.py](src/model.py)                  # chargement du modèle Ultralytics YOLO
│   ├── [train.py](src/train.py)                  # entraînement YOLO classification
│   ├── [evaluate.py](src/evaluate.py)               # évaluation + métriques + matrice de confusion
│   └── [predict.py](src/predict.py)                # prédiction en ligne de commande sur une image
├── [gui/](gui)
│   └── [app_tkinter.py](gui/app_tkinter.py)        # interface graphique de démonstration (Tkinter)
├── [models/](models)
│   └── [ariary_yolo_cls.pt](models/ariary_yolo_cls.pt)    # modèle YOLO entraîné (généré par train.py)
├── [results/](results)                  # métriques, courbes, matrice de confusion (générés)
├── [rapport/](rapport)                  # rapport du projet (étude bibliographique, résultats, etc.)
├── [requirements.txt](requirements.txt)
└── [README.md](README.md)
```

## 3. Installation

```bash
python3 -m venv venv
source venv/bin/activate          # sous ubuntu : env\Scripts\activate
pip install -r requirements.txt
```

Prérequis : Python 3.10+. `tkinter` doit être disponible (inclus par défaut
sous Windows/macOS ; sous Ubuntu/Debian : `sudo apt install python3-tk`).

## 4. Utilisation

### 4.1 Préparer les données

Les images brutes du jeu de données sont organisées dans `data/raw/` par classe 
(valeur faciale du billet) : `100/`, `200/`, `500/`, `1000/`, `2000/`, `5000/`, 
`10000/`, `20000/`.

### 4.2 Entraîner le modèle

```bash

./env/bin/python3 src/train.py --epochs 25 --batch_size 8 --imgsz 160 --rebuild_dataset
```

Options utiles : `--data_dir`, `--dataset_out`, `--epochs`, `--batch_size`,
`--imgsz`, `--lr`, `--base_model`, `--model_out`. Le script crée
automatiquement `data/yolo_cls/` au format Ultralytics classification
(`train/`, `val/`, `test/`). Le modèle final est sauvegardé dans
`models/ariary_yolo_cls.pt`, et les résultats d'entraînement Ultralytics dans
`results/yolo/`.

Par défaut, le modèle de base est `yolov8n-cls.pt`. Vous pouvez fournir un
autre checkpoint Ultralytics compatible via `--base_model`.

### 4.3 Évaluer le modèle

```bash
./env/bin/python3 src/evaluate.py
```

Génère :
- `results/classification_report.txt` (precision, recall, f1-score par classe)
- `results/metrics.json` (résumé chiffré)
- `results/matrice_confusion.png` et `results/confusion_matrix.csv`

### 4.4 Démonstration (interface graphique Tkinter)

```bash
./env/bin/python3 gui/app_tkinter.py
```

Permet de charger une photo de billet, de lancer la prédiction, et de
visualiser le score du modèle pour chacune des 8 classes.

### 4.5 Prédiction en ligne de commande

```bash
./env/bin/python3 src/predict.py chemin/vers/image.jpg
```

## 5. Résultats

Voir `results/metrics.json` et le rapport (`rapport/`) pour l'analyse
complète. **Important** : les métriques obtenues dépendent de la qualité et de
la représentativité du jeu de données dans `data/raw/`.
