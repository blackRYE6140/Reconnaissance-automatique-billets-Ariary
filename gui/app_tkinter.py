"""
app_tkinter.py
==============
Interface graphique (Tkinter) permettant de démontrer le modèle YOLO de
reconnaissance automatique des billets d'ariary.

Fonctionnalités :
  - Charger une image de billet depuis le disque (bouton "Charger une image")
  - Afficher l'aperçu de l'image
  - Lancer la prédiction (bouton "Analyser le billet")
  - Afficher la classe prédite (valeur faciale en Ariary), la confiance du
    modèle, et le détail des scores pour les 8 classes (barres)
  - Historique des dernières prédictions de la session

Lancement :
    python gui/app_tkinter.py
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from data_preparation import CLASSES  # noqa: E402
from model import DEFAULT_MODEL_PATH, load_yolo_model  # noqa: E402
from predict import predict_image, read_image_bgr  # noqa: E402

MODEL_PATH = DEFAULT_MODEL_PATH


class AriaryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reconnaissance automatique des billets d'ariary")
        self.geometry("760x620")
        self.minsize(700, 580)
        self.configure(bg="#f4f6f8")

        self.model = None
        self.current_image_path = None
        self.current_image_bgr = None
        self.history = []

        self._build_style()
        self._build_layout()
        self._load_model_async()

    # ------------------------------------------------------------------ UI
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f4f6f8")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10), background="#f4f6f8", foreground="#555")
        style.configure("Result.TLabel", font=("Segoe UI", 22, "bold"), background="#ffffff", foreground="#1a7a3c")
        style.configure("Conf.TLabel", font=("Segoe UI", 11), background="#ffffff", foreground="#333")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)

    def _build_layout(self):
        header = ttk.Frame(self, padding=(20, 15, 20, 5))
        header.pack(fill="x")
        ttk.Label(header, text="Reconnaissance automatique des billets d'ariary",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(header,
                  text="Démonstration YOLO Ultralytics + OpenCV - Projet RNA / Apprentissage automatique",
                  style="SubHeader.TLabel").pack(anchor="w")

        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # --- Colonne gauche : image
        left = ttk.LabelFrame(main, text="Image du billet", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.image_canvas = tk.Label(left, bg="#e9ecef", text="Aucune image chargée",
                                      width=40, height=15, relief="groove")
        self.image_canvas.pack(fill="both", expand=True, pady=(0, 10))

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Charger une image",
                   command=self.load_image).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(btn_frame, text="Analyser le billet",
                   command=self.predict).pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.status_var = tk.StringVar(value="Chargement du modèle...")
        ttk.Label(left, textvariable=self.status_var, style="SubHeader.TLabel").pack(anchor="w", pady=(8, 0))

        # --- Colonne droite : résultats
        right = ttk.LabelFrame(main, text="Résultat de la prédiction", padding=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        result_card = tk.Frame(right, bg="white", relief="groove", bd=1)
        result_card.pack(fill="x", pady=(0, 10))
        ttk.Label(result_card, text="Valeur prédite", style="Conf.TLabel",
                  background="white").pack(anchor="w", padx=10, pady=(8, 0))
        self.result_var = tk.StringVar(value="—")
        ttk.Label(result_card, textvariable=self.result_var, style="Result.TLabel",
                  background="white").pack(anchor="w", padx=10, pady=(0, 4))
        self.conf_var = tk.StringVar(value="Confiance : —")
        ttk.Label(result_card, textvariable=self.conf_var, style="Conf.TLabel",
                  background="white").pack(anchor="w", padx=10, pady=(0, 8))

        ttk.Label(right, text="Scores par classe :", style="SubHeader.TLabel").pack(anchor="w", pady=(4, 4))
        self.bars_frame = ttk.Frame(right)
        self.bars_frame.pack(fill="x")
        self.class_bars = {}
        self._build_probability_bars()

        ttk.Label(right, text="Historique de la session :", style="SubHeader.TLabel").pack(anchor="w", pady=(15, 4))
        self.history_list = tk.Listbox(right, height=8)
        self.history_list.pack(fill="both", expand=True)

        footer = ttk.Frame(self, padding=(20, 5, 20, 10))
        footer.pack(fill="x")
        ttk.Label(footer,
                  text="Modèle YOLO entraîné sur un jeu de démonstration synthétique — à ré-entraîner sur de vraies "
                       "photographies de billets avant tout usage réel.",
                  style="SubHeader.TLabel", foreground="#b45309").pack(anchor="w")

    def _build_probability_bars(self):
        for c in CLASSES:
            row = ttk.Frame(self.bars_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"{c} Ar", width=8).pack(side="left")
            pb = ttk.Progressbar(row, orient="horizontal", length=200, mode="determinate", maximum=100)
            pb.pack(side="left", padx=5, fill="x", expand=True)
            val_lbl = ttk.Label(row, text="0 %", width=6)
            val_lbl.pack(side="left")
            self.class_bars[c] = (pb, val_lbl)

    # ------------------------------------------------------------- actions
    def _load_model_async(self):
        self.after(100, self._load_model)

    def _load_model(self):
        try:
            if not MODEL_PATH.exists():
                self.status_var.set("Modèle YOLO introuvable. Lancez d'abord src/train.py.")
                return
            self.model = load_yolo_model(MODEL_PATH)
            self.status_var.set("Modèle YOLO chargé. Chargez une image pour commencer.")
        except Exception as e:
            self.status_var.set(f"Erreur de chargement du modèle : {e}")

    def load_image(self):
        path = filedialog.askopenfilename(
            title="Choisir une image de billet",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("Tous les fichiers", "*.*")],
        )
        if not path:
            return
        try:
            image_bgr = read_image_bgr(path)
            cv2 = __import__("cv2")
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(image_rgb)
            self.current_image_path = path
            self.current_image_bgr = image_bgr

            display_img = img.copy()
            display_img.thumbnail((360, 360))
            tk_img = ImageTk.PhotoImage(display_img)
            self.image_canvas.configure(image=tk_img, text="")
            self.image_canvas.image = tk_img
            self.status_var.set(f"Image chargée : {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image :\n{e}")

    def predict(self):
        if self.model is None:
            messagebox.showwarning("Modèle indisponible", "Le modèle n'est pas chargé.")
            return
        if self.current_image_bgr is None:
            messagebox.showwarning("Aucune image", "Veuillez d'abord charger une image de billet.")
            return

        try:
            pred_class, confidence_value, probs = predict_image(self.current_image_bgr, model=self.model)
        except Exception as e:
            messagebox.showerror("Erreur de prédiction", f"Impossible d'analyser l'image :\n{e}")
            return

        confidence = confidence_value * 100

        self.result_var.set(f"{pred_class:,} Ariary".replace(",", " "))
        self.conf_var.set(f"Confiance : {confidence:.1f} %")

        for i, c in enumerate(CLASSES):
            pb, lbl = self.class_bars[c]
            pct = float(probs[i]) * 100
            pb["value"] = pct
            lbl.configure(text=f"{pct:.1f} %")

        entry = f"{Path(self.current_image_path).name}  →  {pred_class} Ar  ({confidence:.1f}%)"
        self.history.append(entry)
        self.history_list.insert(0, entry)
        self.status_var.set("Prédiction effectuée.")


def main():
    app = AriaryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
