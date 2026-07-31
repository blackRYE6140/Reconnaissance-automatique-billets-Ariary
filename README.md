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
├── data/
│   ├── raw/                           # images brutes classées par dossier (label = valeur faciale)
│   │   ├── 100/
│   │   ├── 200/
│   │   ├── 500/
│   │   ├── 1000/
│   │   ├── 2000/
│   │   ├── 5000/
│   │   ├── 10000/
│   │   └── 20000/
│   └── yolo_cls/                      # dataset au format Ultralytics classification
│       ├── dataset_info.json
│       ├── test/
│       │   ├── 100/ … 20000/
│       ├── train/
│       │   ├── 100/ … 20000/
│       └── val/
│           ├── 100/ … 20000/
├── src/
│   ├── data_preparation.py            # constantes des classes et helpers historiques
│   ├── yolo_dataset.py                # conversion data/raw -> data/yolo_cls
│   ├── model.py                       # chargement du modèle Ultralytics YOLO
│   ├── train.py                       # entraînement YOLO classification
│   ├── evaluate.py                    # évaluation + métriques + matrice de confusion
│   └── predict.py                     # prédiction en ligne de commande sur une image
├── gui/
│   └── app_tkinter.py                 # interface graphique de démonstration (Tkinter)
├── models/
│   └── ariary_yolo_cls.pt             # modèle YOLO entraîné (généré par train.py)
├── results/                           # métriques, courbes, matrice de confusion (générés)
│   ├── classification_report.txt
│   ├── confusion_matrix.csv
│   ├── matrice_confusion.png
│   ├── metrics.json
│   └── per_class_metrics.json
├── runs/                              # sorties complètes d'entraînement Ultralytics
│   └── classify/results/yolo/ariary_yolo_cls/
│       ├── args.yaml
│       ├── results.csv
│       ├── results.png
│       ├── confusion_matrix.png
│       ├── confusion_matrix_normalized.png
│       ├── train_batch0.jpg
│       ├── train_batch1.jpg
│       ├── train_batch2.jpg
│       ├── train_batch1170.jpg
│       ├── train_batch1171.jpg
│       ├── train_batch1172.jpg
│       ├── val_batch0_labels.jpg
│       ├── val_batch0_pred.jpg
│       ├── val_batch1_labels.jpg
│       ├── val_batch1_pred.jpg
│       ├── val_batch2_labels.jpg
│       ├── val_batch2_pred.jpg
│       └── weights/
│           ├── best.pt
│           └── last.pt
├── rapport/                           # rapport du projet
│   ├── Rapport_Projet_RNA_Ariary.pdf
│   └── demo_screenshot.png
├── requirements.txt
└── README.md
```

### Liens rapides vers les dossiers et fichiers principaux

| Élément | Lien |
|---------|------|
| **Données brutes** | [data/raw/](data/raw) |
| **Dataset YOLO** | [data/yolo_cls/](data/yolo_cls) |
| **Info dataset** | [data/yolo_cls/dataset_info.json](data/yolo_cls/dataset_info.json) |
| **Code source** | [src/](src) |
| **Préparation** | [src/data_preparation.py](src/data_preparation.py) |
| **Conversion YOLO** | [src/yolo_dataset.py](src/yolo_dataset.py) |
| **Modèle** | [src/model.py](src/model.py) |
| **Entraînement** | [src/train.py](src/train.py) |
| **Évaluation** | [src/evaluate.py](src/evaluate.py) |
| **Prédiction** | [src/predict.py](src/predict.py) |
| **Interface graphique** | [gui/app_tkinter.py](gui/app_tkinter.py) |
| **Modèle entraîné** | [models/ariary_yolo_cls.pt](models/ariary_yolo_cls.pt) |
| **Résultats** | [results/](results) |
| **Runs YOLO** | [runs/classify/results/yolo/ariary_yolo_cls/](runs/classify/results/yolo/ariary_yolo_cls) |
| **Rapport PDF** | [rapport/Rapport_Projet_RNA_Ariary.pdf](rapport/Rapport_Projet_RNA_Ariary.pdf) |
| **Requirements** | [requirements.txt](requirements.txt) |

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
`runs/classify/results/yolo/ariary_yolo_cls/`.

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

## 6. Sorties d'entraînement (`runs/`)

Le dossier [`runs/classify/results/yolo/ariary_yolo_cls/`](runs/classify/results/yolo/ariary_yolo_cls) contient toutes les sorties générées automatiquement par Ultralytics YOLO lors de l'entraînement du modèle de classification.

### 6.1 Configuration

| Fichier | Description |
|---------|-------------|
| [`args.yaml`](runs/classify/results/yolo/ariary_yolo_cls/args.yaml) | Hyperparamètres et configuration utilisés pour l'entraînement (epochs, batch size, learning rate, image size, etc.) |

### 6.2 Métriques et courbes d'entraînement

| Fichier | Description |
|---------|-------------|
| [`results.csv`](runs/classify/results/yolo/ariary_yolo_cls/results.csv) | Métriques par époque : loss d'entraînement, loss de validation, accuracy top-1, accuracy top-5 |
| [`results.png`](runs/classify/results/yolo/ariary_yolo_cls/results.png) | Graphiques des courbes d'entraînement (loss et accuracy au fil des époques) |

### 6.3 Matrices de confusion

| Fichier | Description |
|---------|-------------|
| [`confusion_matrix.png`](runs/classify/results/yolo/ariary_yolo_cls/confusion_matrix.png) | Matrice de confusion (valeurs absolues) sur le jeu de validation |
| [`confusion_matrix_normalized.png`](runs/classify/results/yolo/ariary_yolo_cls/confusion_matrix_normalized.png) | Matrice de confusion normalisée (pourcentages) sur le jeu de validation |

### 6.4 Visualisation des batches d'entraînement

Ces images montrent des exemples de lots (batches) utilisés pendant l'entraînement, avec les augmentations de données appliquées :

| Fichier | Description |
|---------|-------------|
| [`train_batch0.jpg`](runs/classify/results/yolo/ariary_yolo_cls/train_batch0.jpg) | Premier batch d'entraînement (début de l'entraînement) |
| [`train_batch1.jpg`](runs/classify/results/yolo/ariary_yolo_cls/train_batch1.jpg) | Deuxième batch d'entraînement |
| [`train_batch2.jpg`](runs/classify/results/yolo/ariary_yolo_cls/train_batch2.jpg) | Troisième batch d'entraînement |
| [`train_batch1170.jpg`](runs/classify/results/yolo/ariary_yolo_cls/train_batch1170.jpg) | Batch d'entraînement en fin d'entraînement |
| [`train_batch1171.jpg`](runs/classify/results/yolo/ariary_yolo_cls/train_batch1171.jpg) | Batch d'entraînement en fin d'entraînement |
| [`train_batch1172.jpg`](runs/classify/results/yolo/ariary_yolo_cls/train_batch1172.jpg) | Dernier batch d'entraînement |

### 6.5 Visualisation des batches de validation

Ces images comparent les labels réels et les prédictions du modèle sur le jeu de validation :

| Fichier | Description |
|---------|-------------|
| [`val_batch0_labels.jpg`](runs/classify/results/yolo/ariary_yolo_cls/val_batch0_labels.jpg) | Batch de validation 0 — labels réels (ground truth) |
| [`val_batch0_pred.jpg`](runs/classify/results/yolo/ariary_yolo_cls/val_batch0_pred.jpg) | Batch de validation 0 — prédictions du modèle |
| [`val_batch1_labels.jpg`](runs/classify/results/yolo/ariary_yolo_cls/val_batch1_labels.jpg) | Batch de validation 1 — labels réels |
| [`val_batch1_pred.jpg`](runs/classify/results/yolo/ariary_yolo_cls/val_batch1_pred.jpg) | Batch de validation 1 — prédictions du modèle |
| [`val_batch2_labels.jpg`](runs/classify/results/yolo/ariary_yolo_cls/val_batch2_labels.jpg) | Batch de validation 2 — labels réels |
| [`val_batch2_pred.jpg`](runs/classify/results/yolo/ariary_yolo_cls/val_batch2_pred.jpg) | Batch de validation 2 — prédictions du modèle |

### 6.6 Poids du modèle

| Fichier | Description |
|---------|-------------|
| [`weights/best.pt`](runs/classify/results/yolo/ariary_yolo_cls/weights/best.pt) | Meilleurs poids du modèle (accuracy de validation maximale) |
| [`weights/last.pt`](runs/classify/results/yolo/ariary_yolo_cls/weights/last.pt) | Poids du modèle à la dernière époque d'entraînement |
