import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

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
        self.status_text = tk.StringVar(value="Pilih folder input berisi gambar .jpg untuk memulai.")
        self.pooling_method = tk.StringVar(value="average")
        self.resize_rows = tk.StringVar(value="20")
        self.resize_cols = tk.StringVar(value="30")
        self.threshold_value = tk.StringVar(value="128")
        self.label_value = tk.StringVar()
        self.dataset_name = tk.StringVar(value="dataset.csv")

        self.preview_image = None
        self.stage_items = []

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

        left = ttk.Frame(content, style="Card.TFrame", padding=22)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 18))

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
        ttk.Label(parent, text="Folder gambar", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._folder_row(parent, "Input", self.input_folder, self.choose_input_folder)
        self._folder_row(parent, "Output", self.output_folder, self.choose_output_folder)

    def _folder_row(self, parent, label, variable, command):
        ttk.Label(parent, text=label, style="CardMuted.TLabel").pack(anchor="w", pady=(8, 3))
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x")
        ttk.Entry(row, textvariable=variable, width=42).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=command).pack(side="left", padx=(8, 0))

    def _build_preprocessing_panel(self, parent):
        ttk.Label(parent, text="Tahap preprocessing", style="Section.TLabel").pack(anchor="w", pady=(22, 10))
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
        ttk.Label(parent, text="Dataset", style="Section.TLabel").pack(anchor="w", pady=(22, 10))

        form = ttk.Frame(parent, style="Card.TFrame")
        form.pack(fill="x")
        ttk.Label(form, text="Label", style="CardMuted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Nama file", style="CardMuted.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Entry(form, textvariable=self.label_value, width=15).grid(row=1, column=0, sticky="ew", pady=(3, 10))
        ttk.Entry(form, textvariable=self.dataset_name, width=22).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(3, 10))

        self._stage_button(parent, "04", "Creating Dataset + Label", "Susun fitur piksel dan label ke file dataset.", self.run_create_dataset)
        self._stage_button(parent, "05", "Randomize Dataset", "Acak urutan data sebelum training ANN.", self.run_randomize_dataset)

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
        ttk.Label(parent, text="Product surface", style="DarkTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(parent, text="Preview file, output folder, dan status pipeline", style="Dark.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 14))

        top_row = ttk.Frame(parent, style="Dark.TFrame")
        top_row.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        top_row.columnconfigure(0, weight=1)

        self.image_combo = ttk.Combobox(top_row, textvariable=self.selected_image, state="readonly")
        self.image_combo.grid(row=0, column=0, sticky="ew")
        self.image_combo.bind("<<ComboboxSelected>>", lambda _event: self.show_selected_image())
        ttk.Button(top_row, text="Refresh", style="Dark.TButton", command=self.refresh_image_list).grid(row=0, column=1, padx=(8, 0))

        preview_wrap = tk.Frame(parent, bg=COLORS["surface_dark_soft"], highlightbackground=COLORS["surface_dark_elevated"], highlightthickness=1)
        preview_wrap.grid(row=3, column=0, sticky="nsew")
        preview_wrap.rowconfigure(0, weight=1)
        preview_wrap.columnconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(preview_wrap, bg=COLORS["surface_dark_soft"], highlightthickness=0)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.preview_canvas.bind("<Configure>", lambda _event: self.show_selected_image())

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
        folders = [self.input_folder.get(), self.output_folder.get()]
        image_paths = []
        for folder in folders:
            if not folder or not os.path.isdir(folder):
                continue
            for filename in sorted(os.listdir(folder)):
                if filename.lower().endswith(IMAGE_EXTENSIONS):
                    image_paths.append(os.path.join(folder, filename))

        unique_paths = sorted(dict.fromkeys(image_paths))
        self.image_combo["values"] = unique_paths
        if unique_paths and self.selected_image.get() not in unique_paths:
            self.selected_image.set(unique_paths[0])
            self.show_selected_image()
        elif not unique_paths:
            self.selected_image.set("")
            self.clear_preview("Belum ada gambar .jpg yang ditemukan.")

    def show_selected_image(self):
        path = self.selected_image.get()
        if not path:
            self.clear_preview("Pilih gambar untuk preview.")
            return
        try:
            image = Image.open(path)
        except OSError as error:
            self.clear_preview(f"Gagal membuka gambar:\n{error}")
            return

        canvas_width = max(self.preview_canvas.winfo_width() - 24, 1)
        canvas_height = max(self.preview_canvas.winfo_height() - 24, 1)
        image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(image)

        self.preview_canvas.delete("all")
        image_width = self.preview_image.width()
        image_height = self.preview_image.height()
        x = max((self.preview_canvas.winfo_width() - image_width) // 2, 0)
        y = max((self.preview_canvas.winfo_height() - image_height) // 2, 0)
        self.preview_canvas.create_image(x, y, anchor="nw", image=self.preview_image)

    def clear_preview(self, text):
        self.preview_image = None
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(22, 22, anchor="nw", fill=COLORS["on_dark"], text=text, font=CODE_FONT)

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

    def execute_stage(self, stage, **kwargs):
        try:
            result = run_stage(stage, **kwargs)
        except NotImplementedError as error:
            messagebox.showinfo("Backend belum diisi", str(error))
            result = f"Tahap '{stage}' sudah terhubung ke modul backend, tetapi implementasinya belum diisi."
        except Exception as error:
            messagebox.showerror("Proses gagal", str(error))
            self.set_status(f"Tahap '{stage}' gagal.")
            return

        self.refresh_image_list()
        self.select_latest_output_image(kwargs.get("output_folder"))
        self.set_status(result)
        self.show_stage_success(stage, result)

    def show_stage_success(self, stage, result):
        if stage == "grayscale":
            messagebox.showinfo("Grayscale Berhasil", result)

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
        label = self.label_value.get().strip()
        dataset_name = self.dataset_name.get().strip()
        if not label:
            messagebox.showerror("Label Kosong", "Isi label dataset terlebih dahulu.")
            return
        if not dataset_name:
            messagebox.showerror("Nama File Kosong", "Isi nama file dataset terlebih dahulu.")
            return
        input_folder, output_folder = folders
        self.set_status("Membuat dataset dan label...")
        self.execute_stage("create_dataset", input_folder=input_folder, output_folder=output_folder, label=label, dataset_name=dataset_name)

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


if __name__ == "__main__":
    app = PreprocessingApp()
    app.mainloop()
