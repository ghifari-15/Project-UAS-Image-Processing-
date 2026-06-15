import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np

from dataset_tools import load_labels, save_label

from backend_controller import run_stage


APP_TITLE = "Dataset Preprocessing Studio"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

COLORS = {
    "canvas": "#faf9f5",
    "surface_soft": "#f5f0e8",
    "surface_card": "#efe9de",
    "surface_dark": "#181715",
    "surface_dark_elevated": "#252320",
    "surface_dark_soft": "#1f1e1b",
    "primary": "#cc785c",
    "primary_active": "#a9583e",
    "hairline": "#e6dfd8",
    "ink": "#141413",
    "body": "#3d3d3a",
    "muted": "#6c6a64",
    "muted_soft": "#8e8b82",
    "on_primary": "#ffffff",
    "on_dark": "#faf9f5",
    "on_dark_soft": "#a09d96",
    "accent_teal": "#5db8a6",
    "accent_amber": "#e8a55a",
}

DISPLAY_FONT = ("Georgia", 35)
DISPLAY_FONT_SMALL = ("Georgia", 18)
BODY_FONT = ("Segoe UI", 10)
BODY_FONT_MEDIUM = ("Segoe UI", 10, "bold")
CAPTION_FONT = ("Segoe UI", 9)
CODE_FONT = ("Consolas", 10)


class PreprocessingApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1920x1080")
        self.minsize(1020, 650)

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.selected_image = tk.StringVar()
        self.preview_info = tk.StringVar(value="Belum ada gambar hasil preprocessing.")
        self.status_text = tk.StringVar(value="Pilih folder input berisi gambar .jpg untuk memulai.")
        self.pooling_method = tk.StringVar(value="average")
        self.resize_rows = tk.StringVar(value="20")
        self.resize_cols = tk.StringVar(value="30")
        self.threshold_value = tk.StringVar(value="128")
        self.label_value = tk.StringVar()
        self.labels_name = tk.StringVar(value="labels.csv")
        self.dataset_name = tk.StringVar(value="dataset.csv")

        self.preview_before_image = None
        self.preview_after_image = None
        self.stage_items = []
        self.stage_running = False
        self.stage_source_folders = {}

        self._configure_style()
        self._build_layout()

    def _configure_style(self):
        self.configure(bg=COLORS["canvas"])

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["canvas"])
        style.configure("Card.TFrame", background=COLORS["surface_card"], relief="flat")
        style.configure("Soft.TFrame", background=COLORS["surface_soft"], relief="flat")
        style.configure("Dark.TFrame", background=COLORS["surface_dark"], relief="flat")

        style.configure("TLabel", background=COLORS["canvas"], foreground=COLORS["ink"], font=BODY_FONT)
        style.configure("Card.TLabel", background=COLORS["surface_card"], foreground=COLORS["body"], font=BODY_FONT)
        style.configure("Dark.TLabel", background=COLORS["surface_dark"], foreground=COLORS["on_dark"], font=BODY_FONT)
        style.configure("Muted.TLabel", background=COLORS["canvas"], foreground=COLORS["muted"], font=BODY_FONT)
        style.configure("CardMuted.TLabel", background=COLORS["surface_card"], foreground=COLORS["muted"], font=CAPTION_FONT)
        style.configure("Title.TLabel", background=COLORS["canvas"], foreground=COLORS["ink"], font=DISPLAY_FONT)
        style.configure("Section.TLabel", background=COLORS["surface_card"], foreground=COLORS["ink"], font=DISPLAY_FONT_SMALL)
        style.configure("DarkTitle.TLabel", background=COLORS["surface_dark"], foreground=COLORS["on_dark"], font=DISPLAY_FONT_SMALL)
        style.configure("Badge.TLabel", background=COLORS["surface_card"], foreground=COLORS["ink"], font=("Segoe UI", 9, "bold"), padding=(10, 4))

        style.configure("TEntry", fieldbackground=COLORS["canvas"], foreground=COLORS["ink"], bordercolor=COLORS["hairline"], lightcolor=COLORS["hairline"], darkcolor=COLORS["hairline"], padding=(10, 7))
        style.map("TEntry", bordercolor=[("focus", COLORS["primary"])])
        style.configure("TCombobox", fieldbackground=COLORS["canvas"], foreground=COLORS["ink"], arrowcolor=COLORS["ink"], bordercolor=COLORS["hairline"], padding=(8, 6))

        style.configure("TButton", background=COLORS["canvas"], foreground=COLORS["ink"], bordercolor=COLORS["hairline"], font=BODY_FONT_MEDIUM, padding=(12, 8))
        style.map("TButton", background=[("active", COLORS["surface_soft"])])
        style.configure("Dark.TButton", background=COLORS["surface_dark_elevated"], foreground=COLORS["on_dark"], bordercolor=COLORS["surface_dark_elevated"], font=BODY_FONT_MEDIUM, padding=(12, 8))

        style.configure("TRadiobutton", background=COLORS["surface_card"], foreground=COLORS["body"], font=BODY_FONT)

    def _build_layout(self):
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)

        self._build_header(root)

        content = ttk.Frame(root)
        content.pack(fill="both", expand=True, pady=(22, 0))
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left_shell = ttk.Frame(content, style="Card.TFrame", padding=0)
        left_shell.grid(row=0, column=0, sticky="nsw", padx=(0, 18))
        left_shell.configure(width=420)
        left_shell.grid_propagate(False)
        left_shell.rowconfigure(0, weight=1)
        left_shell.columnconfigure(0, weight=1)

        left_canvas = tk.Canvas(
            left_shell,
            bg=COLORS["surface_card"],
            highlightthickness=0,
            width=420,
        )
        left_scrollbar = ttk.Scrollbar(left_shell, orient="vertical", command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        left_canvas.grid(row=0, column=0, sticky="nsew")
        left_scrollbar.grid(row=0, column=1, sticky="ns")

        left = ttk.Frame(left_canvas, style="Card.TFrame", padding=22)
        left_window = left_canvas.create_window((0, 0), window=left, anchor="nw")

        def sync_left_scroll(_event=None):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            left_canvas.itemconfigure(left_window, width=left_canvas.winfo_width())

        def scroll_left(event):
            left_canvas.yview_scroll(-1 * (event.delta // 120), "units")

        left.bind("<Configure>", sync_left_scroll)
        left_canvas.bind("<Configure>", sync_left_scroll)
        left_canvas.bind("<Enter>", lambda _event: left_canvas.bind_all("<MouseWheel>", scroll_left))
        left_canvas.bind("<Leave>", lambda _event: left_canvas.unbind_all("<MouseWheel>"))

        right = ttk.Frame(content, style="Dark.TFrame", padding=22)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        self._build_folder_panel(left)
        self._build_preprocessing_panel(left)
        self._build_dataset_panel(left)
        self._build_preview_panel(right)

        status_bar = tk.Label(root, textvariable=self.status_text, anchor="w", bg=COLORS["surface_soft"], fg=COLORS["body"], font=BODY_FONT, padx=14, pady=10)
        status_bar.pack(fill="x", pady=(14, 0))

    def _build_header(self, parent):
        header = ttk.Frame(parent)
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)

        brand = ttk.Frame(header)
        brand.grid(row=0, column=0, sticky="w")
        ttk.Label(brand, text=APP_TITLE, style="Title.TLabel").pack(side="left")

       

    def _build_folder_panel(self, parent):
        ttk.Label(parent, text="1. Folder kerja", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Label(parent, text="Input otomatis mengikuti hasil tahap terakhir. Output adalah folder induk untuk hasil grayscale, resize, dan binarization.", style="CardMuted.TLabel", wraplength=360).pack(anchor="w", pady=(0, 8))
        self._folder_row(parent, "Input", self.input_folder, self.choose_input_folder)
        self._folder_row(parent, "Output", self.output_folder, self.choose_output_folder)

    def _folder_row(self, parent, label, variable, command):
        ttk.Label(parent, text=label, style="CardMuted.TLabel").pack(anchor="w", pady=(8, 3))
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        ttk.Entry(row, textvariable=variable).grid(row=0, column=0, sticky="ew")
        ttk.Button(row, text="Browse", command=command).grid(row=0, column=1, sticky="e", padx=(8, 0))

    def _build_preprocessing_panel(self, parent):
        ttk.Label(parent, text="2. Preprocessing", style="Section.TLabel").pack(anchor="w", pady=(22, 6))
        ttk.Label(parent, text="Jalankan bertahap: mentah ke grayscale, grayscale ke resize, resize ke binary.", style="CardMuted.TLabel", wraplength=360).pack(anchor="w", pady=(0, 8))
        self._stage_button(parent, "01", "Color-to-Grayscale Conversion", "Konversi warna ke intensitas abu-abu.", self.run_grayscale)

        box = ttk.Frame(parent, style="Card.TFrame")
        box.pack(fill="x", pady=(10, 10))
        self._stage_label(box, "02", "Resizing", "Pilih metode pooling dan ukuran target.")

        method_row = ttk.Frame(box, style="Card.TFrame")
        method_row.pack(fill="x", pady=(8, 6))
        ttk.Radiobutton(method_row, text="Average Pooling", value="average", variable=self.pooling_method).pack(side="left")
        ttk.Radiobutton(method_row, text="Max Pooling", value="max", variable=self.pooling_method).pack(side="left", padx=(16, 0))

        size_row = ttk.Frame(box, style="Card.TFrame")
        size_row.pack(fill="x")
        ttk.Label(size_row, text="Row", style="Card.TLabel").pack(side="left")
        ttk.Entry(size_row, textvariable=self.resize_rows, width=7).pack(side="left", padx=(6, 12))
        ttk.Label(size_row, text="Col", style="Card.TLabel").pack(side="left")
        ttk.Entry(size_row, textvariable=self.resize_cols, width=7).pack(side="left", padx=(6, 12))
        self._primary_button(size_row, "Start", self.run_resize).pack(side="right")

        bin_row = ttk.Frame(parent, style="Card.TFrame")
        bin_row.pack(fill="x", pady=(10, 0))
        self._stage_label(bin_row, "03", "Binarization", "Threshold 0 sampai 255.")
        action = ttk.Frame(bin_row, style="Card.TFrame")
        action.pack(fill="x", pady=(8, 0))
        ttk.Entry(action, textvariable=self.threshold_value, width=9).pack(side="left")
        self._primary_button(action, "Start", self.run_binarization).pack(side="right")

    def _build_dataset_panel(self, parent):
        ttk.Label(parent, text="3. Dataset ANN", style="Section.TLabel").pack(anchor="w", pady=(22, 6))
        ttk.Label(parent, text="Class diambil otomatis dari nama file. Hasilnya inputs, labels, dan class_map untuk ANN.", style="CardMuted.TLabel", wraplength=360).pack(anchor="w", pady=(0, 8))

        self._stage_button(parent, "03", "Dataset & Label", "Buat inputs_*.npy, labels_*.npy, class_map, dan dataset.csv.", self.run_create_dataset)
        self._stage_button(parent, "04", "Randomize Dataset", "Buat random_inputs_*.npy dan random_labels_*.npy.", self.run_randomize_dataset)

    def _stage_label(self, parent, number, title, description):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x")
        tk.Label(row, text=number, bg=COLORS["primary"], fg=COLORS["on_primary"], font=("Segoe UI", 9, "bold"), padx=8, pady=3).pack(side="left", padx=(0, 8))
        text = ttk.Frame(row, style="Card.TFrame")
        text.pack(side="left", fill="x", expand=True)
        ttk.Label(text, text=title, style="Card.TLabel", font=BODY_FONT_MEDIUM).pack(anchor="w")
        ttk.Label(text, text=description, style="CardMuted.TLabel").pack(anchor="w")

    def _stage_button(self, parent, number, title, description, command):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=6)
        self._stage_label(row, number, title, description)
        self._primary_button(row, "Start", command).pack(anchor="e", pady=(8, 0))

    def _primary_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS["primary"],
            fg=COLORS["on_primary"],
            activebackground=COLORS["primary_active"],
            activeforeground=COLORS["on_primary"],
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            font=BODY_FONT_MEDIUM,
        )
        return button

    def _build_preview_panel(self, parent):
        ttk.Label(parent, text="Overview hasil preprocessing", style="DarkTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(parent, text="Panel ini hanya menampilkan gambar dari folder Output.", style="Dark.TLabel", foreground=COLORS["on_dark_soft"], padding=(0, 4, 0, 14)).grid(row=1, column=0, sticky="w")
      

        top_row = ttk.Frame(parent, style="Dark.TFrame")
        top_row.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        top_row.columnconfigure(0, weight=1)

        self.image_combo = ttk.Combobox(top_row, textvariable=self.selected_image, state="readonly")
        self.image_combo.grid(row=0, column=0, sticky="ew")
        self.image_combo.bind("<<ComboboxSelected>>", lambda _event: self.show_selected_image())
        ttk.Button(top_row, text="Prev", style="Dark.TButton", command=self.show_previous_image).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(top_row, text="Next", style="Dark.TButton", command=self.show_next_image).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(top_row, text="Refresh", style="Dark.TButton", command=self.refresh_image_list).grid(row=0, column=3, padx=(8, 0))

        ttk.Label(parent, textvariable=self.preview_info, style="Dark.TLabel", foreground=COLORS["on_dark_soft"]).grid(row=3, column=0, sticky="w", pady=(0, 12))

        preview_wrap = tk.Frame(parent, bg=COLORS["surface_dark_soft"], highlightbackground=COLORS["surface_dark_elevated"], highlightthickness=1)
        preview_wrap.grid(row=4, column=0, sticky="nsew")
        preview_wrap.rowconfigure(1, weight=1)
        preview_wrap.columnconfigure(0, weight=1)
        preview_wrap.columnconfigure(1, weight=1)

        tk.Label(preview_wrap, text="Before", bg=COLORS["surface_dark_soft"], fg=COLORS["on_dark_soft"], font=BODY_FONT_MEDIUM).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))
        tk.Label(preview_wrap, text="After", bg=COLORS["surface_dark_soft"], fg=COLORS["on_dark_soft"], font=BODY_FONT_MEDIUM).grid(row=0, column=1, sticky="w", padx=12, pady=(10, 0))

        self.before_canvas = tk.Canvas(preview_wrap, bg=COLORS["surface_dark_soft"], highlightthickness=0)
        self.before_canvas.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=12)

        self.after_canvas = tk.Canvas(preview_wrap, bg=COLORS["surface_dark_soft"], highlightthickness=0)
        self.after_canvas.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=12)

        self.before_canvas.bind("<Configure>", lambda _event: self.show_selected_image())
        self.after_canvas.bind("<Configure>", lambda _event: self.show_selected_image())

    def choose_input_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder Input")
        if not folder:
            return
        self.input_folder.set(folder)
        if not self.output_folder.get():
            self.output_folder.set(folder)
        self.refresh_image_list()
        self.set_status("Folder input dipilih.")

    def choose_output_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder Output")
        if not folder:
            return
        self.output_folder.set(folder)
        self.refresh_image_list()
        self.set_status("Folder output dipilih.")

    def refresh_image_list(self):
        folders = [self.output_folder.get()]
        image_paths = []
        for folder in folders:
            if not folder or not os.path.isdir(folder):
                continue
            for current_folder, _subfolders, filenames in os.walk(folder):
                for filename in sorted(filenames):
                    if filename.lower().endswith(IMAGE_EXTENSIONS):
                        image_paths.append(os.path.join(current_folder, filename))

        unique_paths = sorted(dict.fromkeys(image_paths))
        self.image_combo["values"] = unique_paths
        if unique_paths and self.selected_image.get() not in unique_paths:
            self.selected_image.set(unique_paths[0])
            self.show_selected_image()
            self.load_current_label()
        elif not unique_paths:
            self.selected_image.set("")
            self.preview_info.set("Belum ada gambar hasil preprocessing di folder output.")
            self.clear_preview("Belum ada gambar hasil preprocessing di folder output.")

    def show_selected_image(self):
        path = self.selected_image.get()
        if not path:
            self.clear_preview("Pilih gambar untuk preview.")
            return
        before_path = self.match_before_image(path)
        try:
            after_image = self.load_preview_array(path)
        except Exception as error:
            self.clear_preview(f"Gagal membuka gambar:\n{error}")
            return

        self.draw_image(self.after_canvas, after_image, "after")
        if before_path and os.path.isfile(before_path):
            try:
                before_image = self.load_preview_array(before_path)
            except Exception:
                self.clear_canvas(self.before_canvas, "Before tidak bisa dibuka.")
            else:
                self.draw_image(self.before_canvas, before_image, "before")
        else:
            self.clear_canvas(self.before_canvas, "Before tidak ditemukan di folder input.")
        self.load_current_label()
        self.update_preview_info()

    def match_before_image(self, after_path):
        after_folder = os.path.dirname(after_path)
        input_folder = self.stage_source_folders.get(self.folder_key(after_folder), self.input_folder.get().strip())
        if not input_folder or not os.path.isdir(input_folder) or self.same_folder(input_folder, after_folder):
            input_folder = self.infer_before_folder(after_folder)
        if not input_folder or not os.path.isdir(input_folder) or self.same_folder(input_folder, after_folder):
            return ""

        filename = os.path.basename(after_path)
        direct_path = os.path.join(input_folder, filename)
        if os.path.isfile(direct_path):
            return direct_path

        base, ext = os.path.splitext(filename)
        if base.endswith("_ready"):
            ready_source = os.path.join(input_folder, base[:-6] + ext)
            if os.path.isfile(ready_source):
                return ready_source
        for marker in ("_bin", "_average_", "_max_", "_gray"):
            if marker in base:
                source_base = base.split(marker)[0]
                source_path = os.path.join(input_folder, source_base + ext)
                if os.path.isfile(source_path):
                    return source_path
        return ""

    def infer_before_folder(self, after_folder):
        folder_name = os.path.basename(after_folder).lower()
        output_root = os.path.dirname(after_folder)
        if folder_name == "grayscale":
            return ""
        if folder_name == "resize":
            return os.path.join(output_root, "grayscale")
        if folder_name == "binarization":
            resize_folder = os.path.join(output_root, "resize")
            if os.path.isdir(resize_folder):
                return resize_folder
            return os.path.join(output_root, "grayscale")
        return self.input_folder.get().strip()

    def folder_key(self, folder):
        return os.path.normcase(os.path.abspath(folder))

    def same_folder(self, first, second):
        return self.folder_key(first) == self.folder_key(second)

    def draw_image(self, canvas, image, slot):
        canvas_width = max(canvas.winfo_width() - 24, 1)
        canvas_height = max(canvas.winfo_height() - 24, 1)
        photo = self.array_to_photo(image, canvas_width, canvas_height)
        if slot == "before":
            self.preview_before_image = photo
        else:
            self.preview_after_image = photo

        canvas.delete("all")
        x = max((canvas.winfo_width() - photo.width()) // 2, 0)
        y = max((canvas.winfo_height() - photo.height()) // 2, 0)
        canvas.create_image(x, y, anchor="nw", image=photo)

    def load_preview_array(self, path):
        image = plt.imread(path)
        if image.dtype != np.uint8:
            image = np.clip(image * 255 if image.max() <= 1.0 else image, 0, 255).astype(np.uint8)
        if image.ndim == 2:
            image = np.repeat(image[:, :, np.newaxis], 3, axis=2)
        return image[:, :, :3]

    def array_to_photo(self, image, max_width, max_height):
        height, width = image.shape[:2]
        scale = min(max_width / width, max_height / height, 1)
        target_width = max(int(width * scale), 1)
        target_height = max(int(height * scale), 1)
        row_idx = np.linspace(0, height - 1, target_height).astype(int)
        col_idx = np.linspace(0, width - 1, target_width).astype(int)
        resized = image[row_idx][:, col_idx]
        header = f"P6 {target_width} {target_height} 255\n".encode("ascii")
        return tk.PhotoImage(data=header + resized.astype(np.uint8).tobytes(), format="PPM")

    def clear_canvas(self, canvas, text):
        canvas.delete("all")
        canvas.create_text(22, 22, anchor="nw", fill=COLORS["on_dark"], text=text, font=CODE_FONT)

    def show_previous_image(self):
        self.shift_selected_image(-1)

    def show_next_image(self):
        self.shift_selected_image(1)

    def shift_selected_image(self, step):
        image_paths = list(self.image_combo["values"])
        if not image_paths:
            self.clear_preview("Belum ada gambar .jpg yang ditemukan.")
            return

        current_path = self.selected_image.get()
        try:
            current_index = image_paths.index(current_path)
        except ValueError:
            current_index = 0 if step >= 0 else len(image_paths) - 1
        else:
            current_index = (current_index + step) % len(image_paths)

        self.selected_image.set(image_paths[current_index])
        self.show_selected_image()
        self.set_status(f"Preview gambar {current_index + 1} dari {len(image_paths)}.")

    def update_preview_info(self):
        image_paths = list(self.image_combo["values"])
        path = self.selected_image.get()
        if not image_paths or not path:
            self.preview_info.set("Belum ada gambar hasil preprocessing.")
            return

        try:
            current_index = image_paths.index(path) + 1
        except ValueError:
            current_index = 1

        label = self.label_value.get().strip()
        label_text = label if label else "belum dilabeli"
        self.preview_info.set(f"{current_index}/{len(image_paths)}  |  {os.path.basename(path)}  |  Label: {label_text}")

    def clear_preview(self, text):
        self.preview_before_image = None
        self.preview_after_image = None
        self.clear_canvas(self.before_canvas, text)
        self.clear_canvas(self.after_canvas, text)

    def validate_common_folders(self):
        input_folder = self.input_folder.get().strip()
        output_folder = self.output_folder.get().strip()
        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showerror("Folder Input Tidak Valid", "Pilih folder input yang benar terlebih dahulu.")
            return None
        if not output_folder or not os.path.isdir(output_folder):
            messagebox.showerror("Folder Output Tidak Valid", "Pilih folder output yang benar terlebih dahulu.")
            return None
        return input_folder, output_folder

    def validate_positive_int(self, value, field_name):
        try:
            number = int(value)
        except ValueError:
            messagebox.showerror("Input Tidak Valid", f"{field_name} harus berupa bilangan bulat positif.")
            return None
        if number <= 0:
            messagebox.showerror("Input Tidak Valid", f"{field_name} harus lebih dari 0.")
            return None
        return number

    def set_status(self, text):
        self.status_text.set(text)
        self.update_idletasks()

    def labels_csv_path(self):
        output_folder = self.output_folder.get().strip()
        labels_name = self.labels_name.get().strip() or "labels.csv"
        base, ext = os.path.splitext(labels_name)
        filename = labels_name if ext.lower() == ".csv" else f"{base or labels_name}.csv"
        return os.path.join(output_folder, filename)

    def load_current_label(self):
        path = self.selected_image.get()
        output_folder = self.output_folder.get().strip()
        if not path or not output_folder:
            return
        labels_path = self.labels_csv_path()
        if not os.path.isfile(labels_path):
            return
        try:
            labels = load_labels(labels_path)
        except Exception:
            return
        self.label_value.set(labels.get(os.path.basename(path), ""))
        self.update_preview_info()

    def save_current_label(self):
        folders = self.validate_common_folders()
        if not folders:
            return
        path = self.selected_image.get()
        if not path:
            messagebox.showerror("Gambar Belum Dipilih", "Pilih gambar yang akan diberi label terlebih dahulu.")
            return
        label = self.label_value.get().strip()
        if not label:
            messagebox.showerror("Label Kosong", "Isi label untuk gambar yang dipilih terlebih dahulu.")
            return
        labels_name = self.labels_name.get().strip()
        if not labels_name:
            messagebox.showerror("Nama CSV Kosong", "Isi nama file label CSV terlebih dahulu.")
            return
        labels_path = self.labels_csv_path()
        save_label(labels_path, os.path.basename(path), label)
        self.set_status(f"Label '{label}' disimpan untuk {os.path.basename(path)} ke {labels_path}.")
        self.update_preview_info()

    def save_current_label_and_next(self):
        before = self.selected_image.get()
        self.save_current_label()
        if before == self.selected_image.get():
            self.show_next_image()

    def execute_stage(self, stage, **kwargs):
        if self.stage_running:
            messagebox.showinfo("Proses Sedang Berjalan", "Tunggu proses sebelumnya selesai terlebih dahulu.")
            return

        self.stage_running = True

        def worker():
            try:
                result = run_stage(stage, **kwargs)
            except NotImplementedError as error:
                self.after(0, self.handle_stage_not_implemented, stage, str(error))
            except Exception as error:
                self.after(0, self.handle_stage_error, stage, str(error))
            else:
                self.after(0, self.handle_stage_success_result, stage, result, self.stage_output_folder(stage, kwargs.get("output_folder")), kwargs.get("input_folder"))

        threading.Thread(target=worker, daemon=True).start()

    def handle_stage_not_implemented(self, stage, error_text):
        self.stage_running = False
        messagebox.showinfo("Backend belum diisi", error_text)
        self.set_status(f"Tahap '{stage}' sudah terhubung ke modul backend, tetapi implementasinya belum diisi.")

    def handle_stage_error(self, stage, error_text):
        self.stage_running = False
        messagebox.showerror("Proses gagal", error_text)
        self.set_status(f"Tahap '{stage}' gagal.")

    def handle_stage_success_result(self, stage, result, output_folder, input_folder):
        self.stage_running = False
        self.remember_stage_source_folder(stage, output_folder, input_folder)
        self.use_stage_output_as_next_input(stage, output_folder)
        self.refresh_image_list()
        self.select_latest_output_image(output_folder)
        self.set_status(result)
        self.show_stage_success(stage, result)

    def remember_stage_source_folder(self, stage, output_folder, input_folder):
        if stage not in {"grayscale", "resize", "binarization"}:
            return
        if output_folder and input_folder and os.path.isdir(output_folder) and os.path.isdir(input_folder):
            self.stage_source_folders[self.folder_key(output_folder)] = input_folder

    def use_stage_output_as_next_input(self, stage, output_folder):
        if stage not in {"grayscale", "resize", "binarization"}:
            return
        if output_folder and os.path.isdir(output_folder):
            self.input_folder.set(output_folder)

    def stage_output_folder(self, stage, output_folder):
        if not output_folder:
            return output_folder
        folder_names = {
            "grayscale": "grayscale",
            "resize": "resize",
            "binarization": "binarization",
        }
        folder_name = folder_names.get(stage)
        if not folder_name:
            return output_folder
        return os.path.join(output_folder, folder_name)

    def show_stage_success(self, stage, result):
        titles = {
            "grayscale": "Grayscale Berhasil",
            "resize": "Resizing Berhasil",
            "binarization": "Binarization Berhasil",
            "create_dataset": "Dataset & Label Berhasil",
            "randomize_dataset": "Randomize Dataset Berhasil",
        }
        messagebox.showinfo(titles.get(stage, "Proses Berhasil"), result)

    def select_latest_output_image(self, output_folder):
        if not output_folder or not os.path.isdir(output_folder):
            return

        image_paths = [
            os.path.join(output_folder, filename)
            for filename in os.listdir(output_folder)
            if filename.lower().endswith(IMAGE_EXTENSIONS)
        ]
        if not image_paths:
            return

        latest_path = max(image_paths, key=os.path.getmtime)
        self.selected_image.set(latest_path)
        self.show_selected_image()

    def run_grayscale(self):
        folders = self.validate_common_folders()
        if not folders:
            return
        input_folder, output_folder = folders
        self.set_status("Menjalankan Color-to-Grayscale Conversion...")
        self.execute_stage("grayscale", input_folder=input_folder, output_folder=output_folder)

    def run_resize(self):
        folders = self.validate_common_folders()
        if not folders:
            return
        rows = self.validate_positive_int(self.resize_rows.get(), "Row")
        cols = self.validate_positive_int(self.resize_cols.get(), "Col")
        if rows is None or cols is None:
            return
        input_folder, output_folder = folders
        self.set_status("Menjalankan resizing...")
        self.execute_stage("resize", input_folder=input_folder, output_folder=output_folder, method=self.pooling_method.get(), rows=rows, cols=cols)

    def run_binarization(self):
        folders = self.validate_common_folders()
        if not folders:
            return
        threshold = self.validate_positive_int(self.threshold_value.get(), "Threshold")
        if threshold is None:
            return
        if threshold > 255:
            messagebox.showerror("Input Tidak Valid", "Threshold harus berada pada rentang 0 sampai 255.")
            return
        input_folder, output_folder = folders
        self.set_status("Menjalankan binarization...")
        self.execute_stage("binarization", input_folder=input_folder, output_folder=output_folder, threshold=threshold)

    def run_create_dataset(self):
        folders = self.validate_common_folders()
        if not folders:
            return
        dataset_name = self.dataset_name.get().strip()
        if not dataset_name:
            messagebox.showerror("Nama File Kosong", "Isi nama file dataset terlebih dahulu.")
            return
        input_folder, output_folder = folders
        self.set_status("Membuat dataset dan label otomatis...")
        self.execute_stage("create_dataset", input_folder=input_folder, output_folder=output_folder, labels_folder=output_folder, labels_name=self.labels_name.get(), dataset_name=dataset_name)

    def run_randomize_dataset(self):
        folders = self.validate_common_folders()
        if not folders:
            return
        dataset_name = self.dataset_name.get().strip()
        if not dataset_name:
            messagebox.showerror("Nama File Kosong", "Isi nama file dataset yang akan diacak.")
            return
        _input_folder, output_folder = folders
        self.set_status("Mengacak dataset...")
        self.execute_stage("randomize_dataset", output_folder=output_folder, dataset_name=dataset_name)
