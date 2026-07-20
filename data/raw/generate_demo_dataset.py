"""
generate_demo_dataset.py
=========================
Prépare un jeu de données de démonstration à partir des images modèles
existantes dont le nom commence par "model".

Le script génère plusieurs variantes en recadrant le billet, en l'ajoutant sur
des fonds colorés, puis en appliquant de légères variations de taille, position
et rotation. Il ne crée plus de faux billets synthétiques simples.

Usage :
    python data/raw/generate_demo_dataset.py
"""

import argparse
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image

MIN_PREPARED_SIZE = 400
MIN_BILL_WIDTH_RATIO = 0.85
MAX_BILL_WIDTH_RATIO = 0.96
BACKGROUND_COLOR_COUNT = 50
MODEL_SOURCE_PREFIX = "model"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def _build_background_palette(count=BACKGROUND_COLOR_COUNT):
    """Crée une palette de fonds clairs avec des teintes très différentes."""
    palette = []
    for idx in range(count):
        hue = (idx / count) % 1.0
        saturation = 0.52 + 0.22 * ((idx * 7) % 5) / 4
        value = 0.88 + 0.10 * ((idx * 11) % 4) / 3
        red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
        palette.append((int(red * 255), int(green * 255), int(blue * 255)))
    return palette


BACKGROUND_COLORS = _build_background_palette()


def _crop_to_content(img):
    """Supprime les marges sombres autour du sujet en recadrant sur le contenu visible."""
    rgba = img.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[:, :, 3]
    color = arr[:, :, :3]
    mask = (alpha > 0) & np.any(color > 25, axis=2)

    if not np.any(mask):
        return rgba

    coords = np.argwhere(mask)
    y_min, x_min = coords[:, 0].min(), coords[:, 1].min()
    y_max, x_max = coords[:, 0].max(), coords[:, 1].max()

    padding = 0
    y_min = max(0, y_min - padding)
    x_min = max(0, x_min - padding)
    y_max = min(rgba.height - 1, y_max + padding)
    x_max = min(rgba.width - 1, x_max + padding)

    return rgba.crop((x_min, y_min, x_max + 1, y_max + 1))


def _build_colored_background(size, rng, color_index=None):
    """Crée un fond coloré légèrement texturé pour varier les prises de vue."""
    if color_index is None:
        color_index = int(rng.integers(0, len(BACKGROUND_COLORS)))
    base_color = np.array(BACKGROUND_COLORS[color_index % len(BACKGROUND_COLORS)], dtype=np.float32)
    tint = rng.uniform(-10, 10, size=3).astype(np.float32)
    arr = np.ones((size, size, 3), dtype=np.float32) * (base_color + tint)
    grad_y = np.linspace(rng.uniform(-8, 2), rng.uniform(2, 10), size).reshape(size, 1, 1)
    grad_x = np.linspace(rng.uniform(-5, 2), rng.uniform(2, 7), size).reshape(1, size, 1)
    noise = rng.normal(0, 2.5, size=(size, size, 3))
    arr += grad_y + grad_x + noise
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _write_prepared_variant(source_path, output_path, rng, background_index=None):
    """Écrit une image de 400x400 avec fond coloré et billet occupant au moins 85% en largeur."""
    with Image.open(source_path) as img:
        cropped = _crop_to_content(img)
        img_rgba = cropped.convert("RGBA")

        canvas = _build_colored_background(MIN_PREPARED_SIZE, rng, color_index=background_index)
        target_width = rng.uniform(
            MIN_PREPARED_SIZE * MIN_BILL_WIDTH_RATIO,
            MIN_PREPARED_SIZE * MAX_BILL_WIDTH_RATIO,
        )
        scale = target_width / img_rgba.width
        new_width = max(1, int(img_rgba.width * scale))
        new_height = max(1, int(img_rgba.height * scale))
        resized = img_rgba.resize((new_width, new_height), Image.Resampling.LANCZOS)

        angle = rng.uniform(-3.0, 3.0)
        if abs(angle) > 0.3:
            resized = resized.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))

        max_allowed = int(MIN_PREPARED_SIZE * 0.98)
        if resized.width > max_allowed or resized.height > max_allowed:
            fit_scale = min(max_allowed / resized.width, max_allowed / resized.height)
            resized = resized.resize(
                (max(1, int(resized.width * fit_scale)), max(1, int(resized.height * fit_scale))),
                Image.Resampling.LANCZOS,
            )

        max_x = max(0, MIN_PREPARED_SIZE - resized.width)
        max_y = max(0, MIN_PREPARED_SIZE - resized.height)
        center_jitter_x = int(rng.uniform(-max_x * 0.25, max_x * 0.25)) if max_x else 0
        center_jitter_y = int(rng.uniform(-max_y * 0.25, max_y * 0.25)) if max_y else 0
        x = max(0, min(max_x, (max_x // 2) + center_jitter_x))
        y = max(0, min(max_y, (max_y // 2) + center_jitter_y))

        canvas.paste(resized, (x, y), resized)
        canvas.save(output_path, quality=95)
        print(f"Image préparée: {output_path}")


def _find_model_source_images(class_dir):
    """Retourne toutes les images sources nommées model* dans le dossier de classe."""
    return sorted(
        path
        for path in class_dir.iterdir()
        if (
            path.is_file()
            and path.stem.lower().startswith(MODEL_SOURCE_PREFIX)
            and path.suffix.lower() in IMAGE_EXTENSIONS
        )
    )


def _class_sort_key(class_dir):
    """Trie les classes numériques par valeur, puis les autres par nom."""
    if class_dir.name.isdigit():
        return (0, int(class_dir.name))
    return (1, class_dir.name.lower())


def _find_class_dirs(out_root):
    """Retourne les dossiers de classes disponibles dans data/raw."""
    if not out_root.exists():
        raise FileNotFoundError(f"Le dossier '{out_root}' n'existe pas.")

    return sorted(
        (
            path
            for path in out_root.iterdir()
            if path.is_dir() and not path.name.startswith(".") and not path.name.startswith("__")
        ),
        key=_class_sort_key,
    )


def _prompt_for_class(out_root):
    """Affiche les classes disponibles et demande la classe à utiliser."""
    class_dirs = _find_class_dirs(out_root)

    if not class_dirs:
        raise FileNotFoundError(f"Aucune classe trouvée dans '{out_root}'.")

    print(f"\nClasses disponibles dans '{out_root}':")
    for idx, class_dir in enumerate(class_dirs, start=1):
        source_count = len(_find_model_source_images(class_dir))
        source_label = f"{source_count} image(s) model*" if source_count else "aucune image model*"
        print(f"  {idx}. {class_dir.name} ({source_label})")

    while True:
        choice = input("\nChoisissez une classe (numero ou valeur): ").strip()

        if choice.isdigit():
            selected_index = int(choice)
            if 1 <= selected_index <= len(class_dirs):
                return class_dirs[selected_index - 1].name

        matching_dir = next((class_dir for class_dir in class_dirs if class_dir.name == choice), None)
        if matching_dir is not None:
            return matching_dir.name

        print("Choix invalide. Entrez le numero affiche ou le nom exact de la classe.")


def _prompt_for_image_count():
    """Demande le nombre d'images à générer."""
    while True:
        raw_value = input("Nombre d'images a generer: ").strip()
        try:
            image_count = int(raw_value)
        except ValueError:
            print("Veuillez entrer un nombre entier.")
            continue

        if image_count > 0:
            return image_count

        print("Le nombre d'images doit etre superieur a 0.")


def prepare_reference_images(out_root, class_value=5000, count=100, seed=200):
    """Prépare plusieurs variantes d'images à partir des sources existantes."""
    class_dir = out_root / str(class_value)

    if not class_dir.exists():
        raise FileNotFoundError(f"La classe '{class_value}' n'existe pas dans '{out_root}'.")

    source_paths = _find_model_source_images(class_dir)

    if not source_paths:
        raise FileNotFoundError(
            f"Impossible de trouver des images sources dans {class_dir}. "
            f"Ajoutez des fichiers nommés model* avec une extension: {sorted(IMAGE_EXTENSIONS)}"
        )

    print(f"\nClasse choisie: {class_value}")
    print(f"Nombre d'images a generer: {count}")
    print("Images sources utilisees:")
    for source_path in source_paths:
        print(f"  - {source_path.name}")

    output_paths = []
    for idx in range(count):
        source_path = source_paths[idx % len(source_paths)]
        output_path = class_dir / f"{class_value}Ar__{idx + 1:03d}.jpg"
        _write_prepared_variant(
            source_path,
            output_path,
            rng=np.random.default_rng(seed + idx),
            background_index=idx,
        )
        output_paths.append(output_path)

    return output_paths


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Affiche les classes disponibles, demande la classe à utiliser, "
            "puis prépare des variantes d'images depuis les fichiers model*."
        )
    )
    parser.add_argument("--out", type=str, default="data/raw", help="Dossier de sortie")
    parser.add_argument("--seed", type=int, default=200)
    args = parser.parse_args()

    out_root = Path(args.out)
    class_value = _prompt_for_class(out_root)
    image_count = _prompt_for_image_count()

    output_paths = prepare_reference_images(
        out_root,
        class_value=class_value,
        count=image_count,
        seed=args.seed,
    )
    print(f"\nTotal : {len(output_paths)} images préparées dans '{out_root / str(class_value)}'.")


if __name__ == "__main__":
    main()
