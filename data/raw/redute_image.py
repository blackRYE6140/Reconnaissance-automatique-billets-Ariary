"""
redute_image.py
===============
Réduit uniquement les images trop lourdes dans data/raw, puis remplace
directement les fichiers ciblés.

Par défaut, le script traite les images de plus de 1 Mo et essaie de les
ramener entre 900 Ko et 1 Mo, en gardant une qualité visuelle élevée.

Usage :
    python data/raw/redute_image.py

Aperçu sans modifier les fichiers :
    python data/raw/redute_image.py --dry-run
"""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path

from PIL import Image, ImageOps


IMAGE_EXTENSIONS = {".jpg", ".jpeg"}
DEFAULT_RAW_DIR = Path(__file__).resolve().parent
ONE_KO = 1024
ONE_MO = 1024 * 1024


def file_size_kb(path: Path) -> float:
    return path.stat().st_size / ONE_KO


def iter_images(raw_dir: Path):
    for path in sorted(raw_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def save_jpeg_to_bytes(image: Image.Image, quality: int) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


def resize_keep_ratio(image: Image.Image, scale: float) -> Image.Image:
    width = max(1, int(image.width * scale))
    height = max(1, int(image.height * scale))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def build_reduced_image_bytes(
    source_path: Path,
    *,
    min_size: int,
    max_size: int,
    min_quality: int,
    start_quality: int,
    resize_step: float,
    min_width: int,
) -> tuple[bytes, int, tuple[int, int]]:
    with Image.open(source_path) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        working_image = image
        quality = start_quality

        while True:
            best_bytes = save_jpeg_to_bytes(working_image, quality)

            if min_size <= len(best_bytes) <= max_size:
                return best_bytes, quality, working_image.size

            if len(best_bytes) < min_size:
                return best_bytes, quality, working_image.size

            if quality > min_quality:
                quality = max(min_quality, quality - 3)
                continue

            if working_image.width <= min_width:
                return best_bytes, quality, working_image.size

            working_image = resize_keep_ratio(working_image, resize_step)
            quality = start_quality


def replace_file(path: Path, data: bytes):
    temp_path = path.with_name(f"{path.stem}.tmp_reduce.jpg")
    temp_path.write_bytes(data)
    os.replace(temp_path, path)


def reduce_images(
    raw_dir: Path,
    *,
    threshold: int,
    min_target: int,
    max_target: int,
    min_quality: int,
    start_quality: int,
    resize_step: float,
    min_width: int,
    dry_run: bool,
):
    processed = 0
    skipped = 0
    reduced = 0

    for image_path in iter_images(raw_dir):
        processed += 1
        original_size = image_path.stat().st_size

        if original_size <= threshold:
            skipped += 1
            continue

        reduced_bytes, quality, dimensions = build_reduced_image_bytes(
            image_path,
            min_size=min_target,
            max_size=max_target,
            min_quality=min_quality,
            start_quality=start_quality,
            resize_step=resize_step,
            min_width=min_width,
        )

        new_size = len(reduced_bytes)

        if new_size >= original_size:
            skipped += 1
            print(
                f"[ignore] {image_path} - {file_size_kb(image_path):.0f} Ko "
                "(reduction non utile)"
            )
            continue

        reduced += 1
        print(
            f"[ok] {image_path} - {original_size / ONE_KO:.0f} Ko -> "
            f"{new_size / ONE_KO:.0f} Ko, qualite {quality}, taille {dimensions[0]}x{dimensions[1]}"
        )

        if not dry_run:
            replace_file(image_path, reduced_bytes)

    print("\nResume")
    print(f"- Images analysees : {processed}")
    print(f"- Images ignorees  : {skipped}")
    print(f"- Images reduites  : {reduced}")
    if dry_run:
        print("- Mode dry-run : aucun fichier n'a ete modifie.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Dossier data/raw a traiter.")
    parser.add_argument("--threshold-kb", type=int, default=1024, help="Traite seulement les images au-dessus de cette taille.")
    parser.add_argument("--min-target-kb", type=int, default=900, help="Taille cible minimale.")
    parser.add_argument("--max-target-kb", type=int, default=1024, help="Taille cible maximale.")
    parser.add_argument("--start-quality", type=int, default=92, help="Qualite JPEG initiale.")
    parser.add_argument("--min-quality", type=int, default=85, help="Qualite JPEG minimale avant reduction des dimensions.")
    parser.add_argument("--resize-step", type=float, default=0.9, help="Facteur de reduction des dimensions.")
    parser.add_argument("--min-width", type=int, default=640, help="Largeur minimale conservee.")
    parser.add_argument("--dry-run", action="store_true", help="Affiche les actions sans modifier les fichiers.")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    if not raw_dir.exists():
        raise FileNotFoundError(f"Dossier introuvable : {raw_dir}")

    reduce_images(
        raw_dir,
        threshold=args.threshold_kb * ONE_KO,
        min_target=args.min_target_kb * ONE_KO,
        max_target=args.max_target_kb * ONE_KO,
        min_quality=args.min_quality,
        start_quality=args.start_quality,
        resize_step=args.resize_step,
        min_width=args.min_width,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
