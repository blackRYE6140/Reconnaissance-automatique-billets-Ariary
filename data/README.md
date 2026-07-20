# Documentation du jeu de données

## 1. Objectif

Le modèle doit reconnaître automatiquement, à partir d'une photographie, la
valeur faciale d'un billet d'ariary parmi les **8 coupures actuellement en
circulation** émises par la Banky Foiben'i Madagasikara (BFM) :

| Classe | Valeur faciale |
|--------|-----------------|
| 0 | 100 Ar |
| 1 | 200 Ar |
| 2 | 500 Ar |
| 3 | 1 000 Ar |
| 4 | 2 000 Ar |
| 5 | 5 000 Ar |
| 6 | 10 000 Ar |
| 7 | 20 000 Ar |

## 2. Organisation du dossier

```
data/raw/
    100/        images du billet de 100 Ar
    200/
    500/
    1000/
    2000/
    5000/
    10000/
    20000/
```

Chaque sous-dossier contient des images `.jpg` / `.png` de la coupure
correspondante. Le nom du dossier fait office d'étiquette (label) et est lu
automatiquement par `src/data_preparation.py`.

## 3. Jeu de données de démonstration depuis les images model*

Faute d'accès à un corpus complet de photographies de billets d'ariary,
`data/raw/generate_demo_dataset.py` prépare un jeu de démonstration à partir
des images modèles placées dans `data/raw/<valeur>/` dont le nom commence
par `model`, par exemple :

- `model1.png`, `model1.jpg` ou `model1.jpeg` ;
- `model2.png`, `model_recto.jpg` ou `model_verso.jpeg`.

Le script recadre ces images, les place sur des fonds colorés, puis applique
de légères variations de taille, position et rotation. Ce jeu sert uniquement à :

- valider que l'ensemble du pipeline fonctionne (chargement, entraînement,
  évaluation, interface graphique) ;
- fournir une base de démonstration reproductible pour la soutenance.

Sans option, le script affiche les classes disponibles dans `data/raw`, puis
demande la classe à utiliser et le nombre d'images à générer :

```bash
python data/raw/generate_demo_dataset.py
```

Les performances obtenues sur ce jeu (voir `results/metrics.json`) ne sont
donc **pas représentatives** de la performance qu'aurait le modèle sur de
vraies photographies variées. Elles démontrent seulement que l'architecture et
le pipeline d'entraînement fonctionnent correctement.

## 4. Méthodologie recommandée pour constituer un vrai jeu de données

Pour un déploiement réel, il est recommandé de :

1. **Collecte** : photographier chaque coupure (recto et verso si possible)
   sous plusieurs conditions : luminosité (jour/artificielle), angles de
   prise de vue, arrière-plans, états d'usure du billet (neuf/usé/plié).
   Viser au minimum 150 à 300 images par classe pour un CNN entraîné from
   scratch (davantage si l'on souhaite éviter le sur-apprentissage, ou
   moins si l'on utilise l'apprentissage par transfert - transfer learning).
2. **Étiquetage** : ranger chaque photo dans le sous-dossier `data/raw/<valeur>/`
   correspondant à sa valeur faciale.
3. **Contrôle qualité** : vérifier l'absence de doublons, la netteté des
   images, et l'équilibre du nombre d'images entre classes (classes
   déséquilibrées → biais du modèle, cf. section "Analyse des résultats" du
   rapport).
4. **Anonymisation / droits** : s'assurer que les photos ne contiennent pas
   d'informations personnelles identifiables (ex. reflet d'une pièce
   d'identité) et respecter les règles en vigueur sur la reproduction de
   monnaie à des fins pédagogiques/de recherche.
5. **Augmentation de données** : le pipeline (`src/train.py`) applique déjà
   une légère augmentation (rotation, zoom, luminosité) pour améliorer la
   généralisation, complémentaire à la diversité des prises de vue réelles.
6. **Découpage** : le script `src/data_preparation.py` effectue
   automatiquement un split stratifié train (70 %) / validation (15 %) /
   test (15 %).

## 5. Remplacer le jeu de démonstration par de vraies photos

```bash
# 1. Supprimer les images de démonstration
rm -rf data/raw/*

# 2. Recréer les dossiers de classes
python -c "from pathlib import Path
for c in [100,200,500,1000,2000,5000,10000,20000]:
    Path(f'data/raw/{c}').mkdir(parents=True, exist_ok=True)"

# 3. Copier vos photographies dans les dossiers correspondants
# 4. Relancer l'entraînement
python src/train.py
python src/evaluate.py
```
