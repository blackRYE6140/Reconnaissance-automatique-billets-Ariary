const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  ImageRun, PageBreak, TableOfContents, LevelFormat, convertInchesToTwip,
  Header, Footer, PageNumber, NumberFormat,
} = require("docx");
const fs = require("fs");

// ---------- Utilitaires ----------
const COLOR_PRIMARY = "444444";   // gris sobre pour les titres
const COLOR_ACCENT = "666666";    // gris secondaire

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 },
    children: [new TextRun({ text, color: COLOR_PRIMARY })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 150 },
    children: [new TextRun({ text, color: COLOR_PRIMARY })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text })],
  });
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 160, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, font: "Times New Roman", size: 24, ...opts })],
  });
}
function bullet(text, level = 0) {
  return new Paragraph({
    bullet: { level },
    spacing: { after: 80 },
    children: [new TextRun({ text, font: "Times New Roman", size: 24 })],
  });
}
function caption(text) {
  return new Paragraph({
    spacing: { before: 80, after: 300 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, italics: true, size: 20, color: "555555" })],
  });
}
function imageParagraph(path, width, height) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200 },
    children: [
      new ImageRun({
        type: "png",
        data: fs.readFileSync(path),
        transformation: { width, height },
      }),
    ],
  });
}
function imageIfExists(path, width, height, captionText) {
  if (!fs.existsSync(path)) return [];
  return [imageParagraph(path, width, height), caption(captionText)];
}

function simpleTable(headerRow, rows, colWidths) {
  const total = colWidths.reduce((a, b) => a + b, 0);
  const mkCell = (text, isHeader) =>
    new TableCell({
      width: { size: colWidths[0], type: WidthType.DXA },
      shading: isHeader ? { type: ShadingType.CLEAR, fill: "EDEDED" } : undefined,
      margins: { top: 80, bottom: 80, left: 100, right: 100 },
      children: [
        new Paragraph({
          children: [
            new TextRun({ text: String(text), bold: isHeader, color: "000000", font: "Times New Roman", size: 24 }),
          ],
        }),
      ],
    });

  const buildRow = (cells, isHeader) =>
    new TableRow({
      children: cells.map((c, i) =>
        new TableCell({
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: isHeader ? { type: ShadingType.CLEAR, fill: "EDEDED" } : undefined,
          margins: { top: 80, bottom: 80, left: 100, right: 100 },
          children: [
            new Paragraph({
              children: [new TextRun({ text: String(c), bold: isHeader, color: "000000", font: "Times New Roman", size: 24 })],
            }),
          ],
        })
      ),
    });

  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [buildRow(headerRow, true), ...rows.map((r) => buildRow(r, false))],
  });
}

// ---------- Lecture des métriques réelles ----------
const metrics = JSON.parse(fs.readFileSync("results/metrics.json", "utf8"));
const perClass = JSON.parse(fs.readFileSync("results/per_class_metrics.json", "utf8"));
const datasetInfo = JSON.parse(fs.readFileSync("data/yolo_cls/dataset_info.json", "utf8"));
const splitTotal = (splitName) =>
  Object.values(datasetInfo.splits[splitName]).reduce((total, count) => total + count, 0);
const totalImages = Object.keys(datasetInfo.splits).reduce(
  (total, splitName) => total + splitTotal(splitName),
  0
);
const minTestByClass = Math.min(...Object.values(datasetInfo.splits.test));
const maxTestByClass = Math.max(...Object.values(datasetInfo.splits.test));
const percent = (value, decimals = 1) => `${(value * 100).toFixed(decimals)} %`;

// ---------- Construction du document ----------
const sections = [];

// ===== PAGE DE GARDE =====
sections.push({
  properties: { page: { size: { width: 11906, height: 16838 } } }, // A4
  children: [
    new Paragraph({ spacing: { before: 1600 }, children: [] }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "RAPPORT DE PROJET", bold: true, size: 32, color: COLOR_ACCENT })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200 },
      children: [new TextRun({ text: "Cours : RNA et Apprentissage automatique", size: 24, italics: true })],
    }),
    new Paragraph({ spacing: { before: 800 }, children: [] }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: "Reconnaissance automatique des billets d'ariary",
          bold: true,
          size: 44,
          color: COLOR_PRIMARY,
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 150 },
      children: [
        new TextRun({
          text: "Étude, implémentation et évaluation d'un modèle YOLOv8 de classification d'images,",
          size: 22,
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "avec interface graphique de démonstration (Tkinter)", size: 22 })],
    }),
    new Paragraph({ spacing: { before: 1200 }, children: [] }),
    new Paragraph({ children: [new PageBreak()] }),
  ],
});

// ===== SOMMAIRE =====
const tocEntries = [
  "1. Introduction et objectifs du projet",
  "2. Étude bibliographique",
  "3. Revue des travaux existants",
  "4. Méthodologie et implémentation",
  "5. Jeu de données",
  "6. Analyse des résultats",
  "7. Démonstration du modèle",
  "8. Conclusion",
  "9. Bibliographie",
];
sections.push({
  properties: {},
  children: [
    h1("Sommaire"),
    ...tocEntries.map(
      (t) =>
        new Paragraph({
          spacing: { after: 180 },
          tabStops: [{ type: "right", position: convertInchesToTwip(6.3) }],
          children: [new TextRun({ text: t, size: 24 })],
        })
    ),
    new Paragraph({ children: [new PageBreak()] }),
  ],
});

// ===== 1. INTRODUCTION =====
sections.push({
  properties: {},
  children: [
    h1("1. Introduction et objectifs du projet"),
    p(
      "Madagascar utilise depuis 2003 l'ariary (MGA) comme unité monétaire officielle, émise par la " +
        "Banky Foiben'i Madagasikara (BFM). Huit coupures sont actuellement en circulation : 100, 200, " +
        "500, 1 000, 2 000, 5 000, 10 000 et 20 000 ariary. La reconnaissance automatique de ces billets " +
        "à partir d'une simple photographie présente un intérêt pratique dans plusieurs contextes : " +
        "automatisation des systèmes de caisse et de tri monétaire, applications d'assistance aux " +
        "personnes malvoyantes, ou encore outils pédagogiques de vulgarisation de l'intelligence " +
        "artificielle appliquée à un problème local et concret."
    ),
    p(
      "L'objectif de ce projet est de concevoir, implémenter et évaluer un système de reconnaissance " +
        "automatique des billets d'ariary reposant sur un modèle Ultralytics YOLOv8 de classification d'images, " +
        "conformément aux notions vues dans le cours RNA et Apprentissage automatique. Le livrable " +
        "comprend :"
    ),
    bullet("une étude bibliographique sur les réseaux de neurones et la classification d'images ;"),
    bullet("une revue des travaux existants sur la reconnaissance automatique de billets de banque ;"),
    bullet("une implémentation complète en Python (prétraitement, entraînement, évaluation) ;"),
    bullet("un jeu de données documenté, avec méthodologie de collecte ;"),
    bullet("une analyse des résultats à l'aide de métriques standard (accuracy, precision, recall, F1-score, matrice de confusion) ;"),
    bullet("une démonstration interactive du modèle via une interface graphique Tkinter ;"),
    bullet("un code source commenté, organisé et versionné avec Git."),
  ],
});

// ===== 2. ETUDE BIBLIOGRAPHIQUE =====
sections.push({
  properties: {},
  children: [
    h1("2. Étude bibliographique"),
    h2("2.1 Apprentissage automatique et vision par ordinateur"),
    p(
      "L'apprentissage automatique regroupe l'ensemble des techniques permettant à une machine de " +
        "réaliser des tâches de perception ou de décision (perception visuelle, " +
        "compréhension du langage, prise de décision, etc.). L'apprentissage automatique (machine " +
        "learning) correspond aux méthodes dans lesquelles les machines apprennent à partir de données, " +
        "sans être explicitement programmées pour chaque cas. Le processus général comprend la " +
        "collecte des données, leur prétraitement, le choix d'un modèle, son entraînement, son " +
        "évaluation, puis son amélioration itérative - méthodologie directement suivie dans ce projet " +
        "(voir sections 4 et 6)."
    ),
    h2("2.2 Les réseaux de neurones artificiels (RNA)"),
    p(
      "Un réseau de neurones artificiels est un modèle computationnel inspiré du fonctionnement du " +
        "cerveau biologique. Il est composé de couches de neurones interconnectés : chaque neurone " +
        "reçoit des entrées pondérées (coefficients synaptiques), calcule une somme pondérée (le " +
        "potentiel d'activation) puis applique une fonction de transfert (ou fonction d'activation) pour " +
        "produire une sortie. L'apprentissage consiste à déterminer les coefficients synaptiques, " +
        "généralement par rétropropagation du gradient : les poids sont ajustés itérativement afin de " +
        "minimiser une fonction de coût mesurant l'écart entre la sortie prédite et la sortie souhaitée, " +
        "à partir d'exemples connus (base d'apprentissage)."
    ),
    p(
      "On distingue l'apprentissage supervisé (les sorties désirées sont connues) de l'apprentissage " +
        "non supervisé (aucune sortie de référence n'est fournie). Le présent projet relève de " +
        "l'apprentissage supervisé : chaque image de billet est associée à une étiquette connue (la " +
        "valeur faciale). Un risque classique de l'apprentissage supervisé est le sur-apprentissage " +
        "(overfitting) : le modèle mémorise la base d'apprentissage au lieu d'apprendre à généraliser, " +
        "ce qui se traduit par une erreur qui diminue sur les données d'entraînement mais augmente sur " +
        "les données de test. Ce phénomène est surveillé dans ce projet via un jeu de validation " +
        "distinct et des techniques de régularisation (dropout, arrêt anticipé - voir section 5.3)."
    ),
    h2("2.3 Les réseaux de neurones convolutifs (CNN)"),
    p(
      "Pour les tâches de vision par ordinateur, les réseaux de neurones convolutifs (Convolutional " +
        "Neural Networks, CNN) constituent l'architecture de référence depuis les travaux fondateurs de " +
        "LeCun et al. sur la reconnaissance de caractères manuscrits. Contrairement à un réseau " +
        "pleinement connecté classique, un CNN exploite des couches de convolution qui appliquent des " +
        "filtres glissants sur l'image afin d'en extraire des caractéristiques locales (contours, " +
        "textures, motifs), puis des couches de pooling qui réduisent la dimensionnalité tout en " +
        "conservant l'information pertinente. L'empilement de plusieurs blocs convolution/pooling " +
        "permet au réseau d'apprendre une hiérarchie de représentations, des motifs simples (bords, " +
        "couleurs) vers des concepts plus abstraits (formes, objets), avant une classification finale par " +
        "une ou plusieurs couches denses. Cette architecture est particulièrement adaptée à la " +
        "reconnaissance de billets de banque, où la couleur dominante, les motifs imprimés et les " +
        "éléments graphiques (chiffres, symboles, portraits, filigranes) constituent des indices visuels " +
        "discriminants entre coupures."
    ),
    h2("2.4 Prétraitement d'image et augmentation de données"),
    p(
      "La qualité d'un modèle de classification d'images dépend fortement du prétraitement appliqué : " +
        "redimensionnement à une taille uniforme, normalisation des valeurs de pixels, et éventuellement " +
        "conversion d'espace colorimétrique. Lorsque le jeu de données disponible est de taille limitée " +
        "- ce qui est fréquent pour des jeux de données spécialisés comme les billets de banque, plus " +
        "difficiles à collecter que des jeux de données génériques - l'augmentation de données " +
        "(rotations, zooms, variations de luminosité) permet d'accroître artificiellement la diversité " +
        "des exemples d'entraînement et de limiter le sur-apprentissage."
    ),
    h2("2.5 Métriques d'évaluation en classification"),
    p(
      "L'évaluation d'un modèle de classification multi-classes repose sur plusieurs métriques " +
        "complémentaires, calculées à partir de la matrice de confusion :"
    ),
    bullet("Accuracy (exactitude) : proportion de prédictions correctes sur l'ensemble des exemples."),
    bullet("Precision : parmi les exemples prédits comme appartenant à une classe, proportion réellement correcte."),
    bullet("Recall (rappel) : parmi les exemples réellement d'une classe, proportion correctement identifiée."),
    bullet("F1-score : moyenne harmonique de la precision et du recall, utile lorsque les classes sont déséquilibrées."),
    p(
      "Ces métriques sont particulièrement pertinentes pour la reconnaissance de billets, où une " +
        "confusion entre deux coupures proches (ex. 1 000 Ar et 2 000 Ar) peut avoir des conséquences " +
        "financières concrètes ; l'analyse par classe (et non la seule accuracy globale) permet donc " +
        "d'identifier les paires de coupures les plus sujettes à confusion."
    ),
  ],
});

// ===== 3. REVUE DES TRAVAUX EXISTANTS =====
sections.push({
  properties: {},
  children: [
    h1("3. Revue des travaux existants"),
    p(
      "La reconnaissance automatique de billets de banque par apprentissage profond est un domaine de " +
        "recherche actif depuis le milieu des années 2010, avec plusieurs axes complémentaires : la " +
        "classification par dénomination, la détection de billets contrefaits et l'évaluation de " +
        "l'état d'usure (fitness classification)."
    ),
    h2("3.1 Classification multi-nationale par CNN"),
    p(
      "Kim et al. proposent l'une des premières approches par CNN pour la classification de billets " +
        "multi-nationaux, combinant une pré-classification par taille avec un classifieur convolutif " +
        "entraîné sur des images de billets de plusieurs pays comportant au total 62 dénominations, en " +
        "s'appuyant fortement sur l'augmentation de données pour compenser la difficulté de collecte " +
        "d'images réelles en grand nombre."
    ),
    h2("3.2 Classification de l'état d'usure (fitness)"),
    p(
      "D'autres travaux se concentrent sur l'évaluation de l'état physique des billets (propre, usé, " +
        "à retirer de la circulation) à l'aide de capteurs à lumière visible et infrarouge combinés à un " +
        "CNN, un problème complémentaire à la simple reconnaissance de la dénomination mais reposant " +
        "sur des architectures similaires."
    ),
    h2("3.3 Détection de faux billets par apprentissage par transfert"),
    p(
      "Pour la détection de contrefaçons, certaines études comparent des architectures CNN entraînées " +
        "depuis zéro (custom, de type AlexNet) à des stratégies d'apprentissage par transfert (transfer " +
        "learning) à partir de réseaux pré-entraînés (VGG, ResNet, Inception), en étudiant notamment le " +
        "point de gel des couches le plus pertinent selon l'architecture. Ces travaux montrent que le " +
        "transfert d'apprentissage permet souvent d'obtenir de bonnes performances même avec un jeu de " +
        "données réduit, ce qui est directement pertinent pour un contexte comme celui de ce projet, où " +
        "la collecte d'un grand nombre de photographies de billets d'ariary reste à réaliser."
    ),
    h2("3.4 Applications grand public"),
    p(
      "Sur le plan applicatif, plusieurs solutions commerciales existent pour l'assistance aux personnes " +
        "malvoyantes, comme Cash Reader ou LookTel Money Reader, qui utilisent la caméra d'un " +
        "smartphone pour annoncer vocalement la valeur d'un billet détecté en temps réel. Ces " +
        "applications couvrent des dizaines de devises mais, à la connaissance de l'auteur, aucune " +
        "solution grand public dédiée et documentée n'existe actuellement pour la reconnaissance " +
        "spécifique de l'ariary malgache, ce qui constitue une motivation supplémentaire pour ce projet."
    ),
    h2("3.5 Positionnement du projet"),
    p(
      "Le présent projet s'inscrit dans la continuité de ces travaux en proposant une solution fondée " +
        "sur YOLOv8n-cls, un modèle léger de classification d'images pré-entraîné puis affiné sur les " +
        "classes de billets d'ariary. Contrairement aux approches industrielles utilisant des capteurs spécialisés " +
        "(infrarouge, lumière ultraviolette pour la détection d'éléments de sécurité), ce projet se " +
        "limite volontairement à des images RGB standard (photographies de smartphone), afin de rester " +
        "reproductible avec un matériel accessible."
    ),
  ],
});

// ===== 4. METHODOLOGIE / IMPLEMENTATION =====
sections.push({
  properties: {},
  children: [
    h1("4. Méthodologie et implémentation"),
    h2("4.1 Vue d'ensemble du pipeline"),
    p(
      "Le projet est organisé en modules Python indépendants, correspondant chacun à une étape du " +
        "pipeline d'apprentissage automatique décrit en section 2.1 :"
    ),
    bullet("src/data_preparation.py - constantes des classes et helpers historiques de préparation ;"),
    bullet("src/yolo_dataset.py - conversion de data/raw/<valeur>/ vers le format Ultralytics classification train/val/test ;"),
    bullet("src/model.py - chargement du modèle Ultralytics YOLO et du checkpoint entraîné ;"),
    bullet("src/train.py - entraînement YOLOv8 classification, sauvegarde du meilleur checkpoint et des résultats ;"),
    bullet("src/evaluate.py - calcul des métriques et de la matrice de confusion sur le jeu de test ;"),
    bullet("src/predict.py - prédiction en ligne de commande sur une image unique ;"),
    bullet("gui/app_tkinter.py - interface graphique de démonstration interactive."),
    h2("4.2 Prétraitement des données"),
    p(
      "Les images sources sont rangées dans data/raw/<valeur>/ puis préparées vers " +
        "data/yolo_cls/ au format attendu par Ultralytics : train/<valeur>/, val/<valeur>/ et " +
        "test/<valeur>/. Le découpage est réalisé par classe avec une graine fixe afin d'obtenir un " +
        "jeu reproductible : environ 70 % pour l'entraînement, 15 % pour la validation et 15 % pour le test."
    ),
    h2("4.3 Architecture du modèle"),
    p(
      "Le modèle retenu est YOLOv8n-cls, la variante de classification légère de la famille " +
        "Ultralytics YOLOv8. Le checkpoint de base yolov8n-cls.pt est affiné sur les 8 classes du projet, " +
        "ce qui permet de profiter de représentations visuelles déjà apprises tout en conservant un temps " +
        "d'entraînement raisonnable sur CPU :"
    ),
    bullet("modèle de base : yolov8n-cls.pt ;"),
    bullet("tâche : classification multi-classes ;"),
    bullet("taille d'image par défaut : 224×224 pixels ;"),
    bullet("sortie : 8 classes correspondant aux coupures 100 à 20 000 Ar."),
    p(
      "L'entraînement est lancé par src/train.py avec les paramètres exposés en ligne de commande " +
        "(epochs, batch_size, imgsz, lr, seed, modèle de base). Le meilleur checkpoint produit par " +
        "Ultralytics est copié dans models/ariary_yolo_cls.pt, puis réutilisé par l'évaluation, la " +
        "prédiction CLI et l'interface Tkinter."
    ),
    h2("4.4 Augmentation de données"),
    p(
      "Une légère augmentation est appliquée pendant l'entraînement (rotation, zoom et variation de " +
        "luminosité limitées) afin d'améliorer la robustesse du modèle aux petites variations de prise " +
        "de vue, tout en évitant des transformations trop agressives (pas de retournement horizontal ou " +
        "vertical, un billet ayant un sens de lecture fixe)."
    ),
    h2("4.5 Outils et bibliothèques"),
    simpleTable(
      ["Outil / bibliothèque", "Rôle dans le projet"],
      [
        ["Python 3.12", "Langage principal"],
        ["Ultralytics YOLO", "Entraînement et inférence du classifieur YOLOv8n-cls"],
        ["PyTorch / TorchVision", "Backend d'apprentissage profond utilisé par Ultralytics"],
        ["NumPy", "Manipulation des tableaux d'images"],
        ["OpenCV / Pillow", "Lecture, affichage et manipulation des images"],
        ["scikit-learn", "Découpage des données, calcul des métriques"],
        ["Matplotlib / Seaborn", "Visualisation des résultats et de la matrice de confusion"],
        ["Tkinter", "Interface graphique de démonstration"],
        ["Git", "Gestion de versions et publication du code source"],
      ],
      [4500, 5500]
    ),
  ],
});

// ===== 5. JEU DE DONNEES =====
sections.push({
  properties: {},
  children: [
    h1("5. Jeu de données"),
    h2("5.1 Classes cibles"),
    p(
      "Le modèle distingue les 8 coupures officiellement en circulation émises par la Banky Foiben'i " +
        "Madagasikara : 100, 200, 500, 1 000, 2 000, 5 000, 10 000 et 20 000 ariary."
    ),
    h2("5.2 Organisation"),
    p(
      "Les images sont organisées dans data/raw/<valeur>/, un sous-dossier par classe, ce qui permet un " +
        "chargement automatique et un étiquetage implicite par nom de dossier (voir data/README.md pour " +
        "le détail complet)."
    ),
    h2("5.3 Jeu de données livré : un jeu synthétique de démonstration"),
    p(
      "Point important. Le dépôt contient un jeu de démonstration organisé par valeur faciale dans " +
        "data/raw/, puis converti en data/yolo_cls/ pour Ultralytics. Ce jeu sert à valider l'ensemble " +
        "du pipeline : préparation, entraînement, évaluation, prédiction et interface graphique."
    ),
    p(
      `Le jeu converti contient ${totalImages} images au total : ${splitTotal("train")} pour l'entraînement, ` +
        `${splitTotal("val")} pour la validation et ${splitTotal("test")} pour le test. Les performances ` +
        "obtenues avec ce jeu doivent être interprétées comme une validation expérimentale du pipeline ; " +
        "un déploiement réel demanderait davantage de photographies variées, prises sous plusieurs angles, " +
        "éclairages et états d'usure."
    ),
    h2("5.4 Vers un jeu de données réel"),
    p(
      "La méthodologie recommandée pour constituer un jeu de données réel - décrite en détail dans " +
        "data/README.md - consiste à photographier chaque coupure sous plusieurs angles, conditions " +
        "d'éclairage et états d'usure (idéalement 150 à 300 images par classe), à ranger chaque photo " +
        "dans le dossier correspondant à sa valeur faciale, puis à relancer directement " +
        "src/train.py et src/evaluate.py sans modification du code."
    ),
  ],
});

// ===== 6. RESULTATS =====
sections.push({
  properties: {},
  children: [
    h1("6. Analyse des résultats"),
    p(
      "Les métriques ci-dessous sont issues de l'exécution de src/evaluate.py sur le jeu de test " +
        `(${metrics.n_test_samples} images, entre ${minTestByClass} et ${maxTestByClass} images par classe), ` +
        "à partir du modèle sauvegardé dans models/ariary_yolo_cls.pt."
    ),
    h2("6.1 Métriques globales"),
    simpleTable(
      ["Métrique", "Valeur"],
      [
        ["Accuracy globale", percent(metrics.accuracy, 2)],
        ["Precision (macro)", percent(metrics.precision_macro, 2)],
        ["Recall (macro)", percent(metrics.recall_macro, 2)],
        ["F1-score (macro)", percent(metrics.f1_macro, 2)],
      ],
      [5000, 5000]
    ),
    p(
      `Le modèle atteint une accuracy de ${percent(metrics.accuracy, 2)} sur le jeu de test. Ce résultat ` +
        "est très élevé et valide le bon fonctionnement du pipeline sur les données disponibles. Il doit " +
        "néanmoins rester interprété avec prudence : le jeu de démonstration est limité et moins varié " +
        "qu'un corpus réel de photographies prises dans des conditions non contrôlées.",
      { italics: false }
    ),
    h2("6.2 Rapport de classification détaillé (par coupure)"),
    simpleTable(
      ["Coupure", "Precision", "Recall", "F1-score", "Support (n)"],
      perClass.map((r) => [
        `${r.classe} Ar`,
        percent(r.precision, 1),
        percent(r.recall, 1),
        percent(r.f1, 1),
        r.support,
      ]),
      [2200, 2000, 2000, 2000, 1800]
    ),
    h2("6.3 Matrice de confusion"),
    p(
      "La matrice de confusion (figure ci-dessous) permet d'identifier les paires de classes les plus " +
        "sujettes à confusion. Sur le jeu de test, la principale erreur observée concerne les classes " +
        "100 Ar et 200 Ar, tandis que les autres coupures sont correctement séparées."
    ),
    imageParagraph("results/matrice_confusion.png", 480, 360),
    caption("Figure 1 - Matrice de confusion sur le jeu de test"),
    h2("6.4 Résultats d'entraînement Ultralytics"),
    p(
      "Ultralytics produit des artefacts d'entraînement dans runs/classify/results/yolo/ariary_yolo_cls/ : " +
        "courbes de performance, batches d'entraînement, matrices de confusion et comparaisons labels/prédictions. " +
        "Ces fichiers complètent les métriques consolidées enregistrées dans results/."
    ),
    ...imageIfExists(
      "runs/classify/results/yolo/ariary_yolo_cls/results.png",
      500,
      250,
      "Figure 2 - Courbes d'entraînement Ultralytics"
    ),
    h2("6.5 Limites et perspectives d'amélioration"),
    bullet("Remplacer le jeu de données synthétique par de vraies photographies (voir section 5.4) et ré-évaluer le modèle dans des conditions réalistes ;"),
    bullet("Comparer YOLOv8n-cls avec d'autres modèles pré-entraînés (MobileNet, ResNet, EfficientNet) pour améliorer la généralisation avec un nombre d'images limité ;"),
    bullet("Élargir l'augmentation de données (variations d'éclairage plus fortes, occlusions partielles, arrière-plans variés) pour mieux simuler les conditions d'usage réelles ;"),
    bullet("Ajouter une étape de détection/recadrage automatique du billet dans l'image avant classification, pour s'affranchir de l'arrière-plan ;"),
    bullet("Étendre le système à la détection de faux billets, à l'image des travaux cités en section 3.3."),
  ],
});

// ===== 7. DEMONSTRATION =====
sections.push({
  properties: {},
  children: [
    h1("7. Démonstration du modèle"),
    p(
      "Une interface graphique développée avec Tkinter (gui/app_tkinter.py) permet de démontrer le " +
        "modèle de façon interactive, sans ligne de commande. Elle propose :"
    ),
    bullet("le chargement d'une image de billet depuis le disque, avec aperçu ;"),
    bullet("le lancement de la prédiction d'un simple clic ;"),
    bullet("l'affichage de la valeur prédite et du niveau de confiance du modèle ;"),
    bullet("le détail des probabilités estimées pour chacune des 8 classes (barres de progression) ;"),
    bullet("un historique des prédictions effectuées durant la session."),
    imageParagraph("rapport/demo_screenshot.png", 480, 360),
    caption("Figure 3 - Capture d'écran de l'interface Tkinter lors d'une prédiction (billet de 10 000 Ar correctement identifié)"),
    p(
      "L'interface se lance avec la commande « python gui/app_tkinter.py » depuis la racine du projet. " +
        "Une version en ligne de commande (src/predict.py) est également fournie pour des tests rapides " +
        "ou une intégration dans d'autres scripts."
    ),
  ],
});

// ===== 8. CONCLUSION =====
sections.push({
  properties: {},
  children: [
    h1("8. Conclusion"),
    p(
      "Ce projet a permis de mettre en œuvre l'ensemble de la chaîne d'un projet d'apprentissage " +
        "automatique appliqué à la vision par ordinateur : étude bibliographique des réseaux de " +
        "neurones et des CNN, revue des travaux existants sur la reconnaissance de billets de banque, " +
        "conception et implémentation d'un pipeline complet en Python (prétraitement, entraînement, " +
        "évaluation), et développement d'une interface graphique de démonstration avec Tkinter."
    ),
    p(
      "Le pipeline a été validé de bout en bout à l'aide du jeu de données de " +
        `démonstration disponible, sur lequel le modèle atteint une accuracy de ${percent(metrics.accuracy, 2)}. La prochaine étape ` +
        "naturelle de ce projet est la constitution d'un véritable corpus de photographies de billets " +
        "d'ariary (voir méthodologie détaillée en section 5.4) afin d'évaluer et d'améliorer la " +
        "performance du modèle en conditions réelles, potentiellement en s'appuyant sur l'apprentissage " +
        "par transfert pour compenser la taille limitée du jeu de données réel."
    ),
    p(
      "Au-delà de sa valeur pédagogique dans le cadre du cours RNA et Apprentissage automatique, ce " +
        "projet illustre une application concrète et localement pertinente de l'intelligence " +
        "artificielle à Madagascar, avec des prolongements possibles vers l'assistance aux personnes " +
        "malvoyantes ou l'automatisation de systèmes de caisse."
    ),
  ],
});

// ===== 9. BIBLIOGRAPHIE =====
sections.push({
  properties: {},
  children: [
    h1("9. Bibliographie"),
    p("Références recherchées et vérifiables via Google Scholar / Google Académique."),
    p(
      "LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). Gradient-based learning applied " +
        "to document recognition. Proceedings of the IEEE, 86(11), 2278-2324. " +
        "https://doi.org/10.1109/5.726791"
    ),
    p(
      "Jocher, G., Chaurasia, A., & Qiu, J. (2023). Ultralytics YOLOv8 (Version 8.0.0) " +
        "[Computer software]. GitHub repository. https://github.com/ultralytics/ultralytics"
    ),
    p(
      "Kim, T. M., Kang, J. S., & Lee, S. W. (2017). Multi-national banknote classification " +
        "based on visible-light line sensor and convolutional neural network. Sensors."
    ),
    p(
      "Nam, S. H., Choi, J. Y., & Park, K. R. (2018). Deep learning-based banknote fitness " +
        "classification using reflection images by a visible-light one-dimensional line image sensor. Sensors."
    ),
    p(
      "Pham, T. D., Lee, D. E., & Park, K. R. (2019). Deep learning-based multinational banknote " +
        "type and fitness classification with visible-light reflection and infrared-light transmission images. Sensors."
    ),
    p(
      "Pham, T. D., Park, C., Nguyen, D. T., Batchuluun, G., & Park, K. R. (2021). " +
        "Fake banknote recognition using deep learning. Applied Sciences, 11(3), 1281."
    ),
    p(
      "Banky Foiben'i Madagasikara (BFM). Informations officielles sur les billets d'ariary " +
        "en circulation."
    ),
  ],
});

// ---------- Génération du document ----------
const doc = new Document({
  creator: "Projet RNA - Reconnaissance des billets d'ariary",
  title: "Reconnaissance automatique des billets d'ariary",
  features: { updateFields: true },
  styles: {
    default: {
      document: { run: { font: "Times New Roman", size: 24 } }, // 12pt
    },
  },
  sections,
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("rapport/Rapport_Projet_RNA_Ariary.docx", buffer);
  console.log("Rapport cree : rapport/Rapport_Projet_RNA_Ariary.docx");
});
