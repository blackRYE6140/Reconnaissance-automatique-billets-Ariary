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
│   ├── raw/                  # images brutes classées par dossier (label = valeur faciale)
│   │   └── generate_demo_dataset.py  # prépare des variantes depuis les images model*
│   └── README.md             # documentation détaillée du jeu de données
├── src/
│   ├── data_preparation.py       # constantes des classes et helpers historiques
│   ├── yolo_dataset.py           # conversion data/raw -> data/yolo_cls
│   ├── model.py                  # chargement du modèle Ultralytics YOLO
│   ├── train.py                  # entraînement YOLO classification
│   ├── evaluate.py               # évaluation + métriques + matrice de confusion
│   └── predict.py                # prédiction en ligne de commande sur une image
├── gui/
│   └── app_tkinter.py        # interface graphique de démonstration (Tkinter)
├── models/
│   └── ariary_yolo_cls.pt    # modèle YOLO entraîné (généré par train.py)
├── results/                  # métriques, courbes, matrice de confusion (générés)
├── rapport/                  # rapport du projet (étude bibliographique, résultats, etc.)
├── requirements.txt
└── README.md
```

## 3. Installation

```bash
python3 -m venv venv
source venv/bin/activate          # sous Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Prérequis : Python 3.10+. `tkinter` doit être disponible (inclus par défaut
sous Windows/macOS ; sous Ubuntu/Debian : `sudo apt install python3-tk`).

## 4. Utilisation

### 4.1 Préparer le jeu de données de démonstration (optionnel)

Le dépôt ne contient pas toutes les images (poids trop lourd pour Git). Pour
tester rapidement le pipeline, placez des images de référence dans
`data/raw/<valeur>/` avec des noms qui commencent par `model` (`model1.jpg`,
`model2.png`, `model_recto.jpeg`, etc.), puis lancez le script. Il affichera
les classes disponibles et demandera la classe puis le nombre d'images à
générer :

```bash
python data/raw/generate_demo_dataset.py
```

Voir `data/README.md` pour la méthodologie de collecte d'un **vrai** jeu
de données à partir de photographies de billets.

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
complète. **Important** : les métriques obtenues avec un jeu de démonstration
généré depuis quelques images modèles ne sont pas représentatives de la
performance sur de vraies photographies variées — voir `data/README.md`,
section 3.
