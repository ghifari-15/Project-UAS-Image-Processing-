# Dataset Preprocessing Studio

Dataset Preprocessing Studio adalah aplikasi desktop berbasis Tkinter untuk membantu proses preprocessing dataset gambar sebelum digunakan pada tahap training model, khususnya alur pengolahan citra seperti grayscale, resizing, binarization, pembuatan dataset, dan randomisasi dataset.

Tool ini dibuat untuk memproses banyak gambar dalam satu folder sekaligus. User cukup memilih folder input, folder output, lalu menjalankan tahap preprocessing dari interface aplikasi.

## Fitur

- Preview gambar di area Product Surface menggunakan Pillow.
- Konversi color-to-grayscale untuk semua gambar dalam folder.
- Resize gambar menggunakan average pooling atau max pooling.
- Binarization dengan nilai threshold 0 sampai 255.
- Pembuatan dataset berformat `.npy` dari kumpulan gambar.
- Randomize dataset `.npy`.
- Panel menu kiri scrollable agar tetap usable pada viewport kecil.
- Alert sukses setelah proses grayscale selesai.

## Struktur File Utama

```text
.
├── app.py
├── backend_controller.py
├── preprocessing.py
├── dataset_tools.py
└── README.md
```

Keterangan:

- `app.py`: interface Tkinter, preview gambar, validasi input user, dan pemanggilan stage preprocessing.
- `backend_controller.py`: penghubung antara UI dan modul processing. File ini menangani proses folder, nama output, dan routing stage.
- `preprocessing.py`: algoritma image processing per gambar menggunakan `numpy` dan `matplotlib`.
- `dataset_tools.py`: pembuatan dataset `.npy` dan randomisasi dataset.

## Kebutuhan Library

Pastikan Python sudah terinstall. Library yang digunakan:

```text
numpy
matplotlib
pillow
```

Install dependency dengan:

```bash
pip install numpy matplotlib pillow
```

Tkinter biasanya sudah termasuk dalam instalasi Python standar di Windows.

## Cara Menjalankan Aplikasi

Jalankan command berikut dari root project:

```bash
python app.py
```

Setelah aplikasi terbuka:

1. Pilih folder input berisi gambar.
2. Pilih folder output untuk menyimpan hasil proses.
3. Jalankan tahap preprocessing yang dibutuhkan.
4. Lihat hasil terbaru di area Product Surface.

Format gambar yang didukung:

```text
.jpg
.jpeg
.png
```

## Alur Preprocessing

### 1. Color-to-Grayscale Conversion

Tahap ini mengubah semua gambar berwarna dalam folder input menjadi grayscale.

Rumus grayscale yang digunakan:

```text
gray = 0.299R + 0.587G + 0.114B
```

Contoh output:

```text
gambar_gray.jpg
huruf_gray.png
```

Setelah proses selesai, aplikasi menampilkan alert sukses dan jumlah gambar yang berhasil diproses.

### 2. Resizing

Tahap resizing digunakan untuk mengubah ukuran gambar ke jumlah row dan column tertentu.

Metode yang tersedia:

- Average Pooling
- Max Pooling

Default ukuran target:

```text
Row: 20
Col: 30
```

Contoh output average pooling:

```text
gambar_average_20x30.jpg
```

Contoh output max pooling:

```text
gambar_max_20x30.jpg
```

### 3. Binarization

Tahap ini mengubah gambar menjadi hitam-putih berdasarkan nilai threshold.

Default threshold:

```text
128
```

Logika threshold:

```text
jika pixel >= threshold, pixel menjadi 255
jika pixel < threshold, pixel menjadi 0
```

Contoh output:

```text
gambar_bin128.jpg
```

### 4. Creating Dataset + Label

Tahap ini membuat dataset dari semua gambar dalam folder input dan menyimpannya dalam format `.npy`.

Default nama file:

```text
dataset.npy
```

Setiap gambar akan diubah menjadi satu baris dataset. Pixel gambar di-flatten menjadi fitur, lalu label ditambahkan di kolom terakhir.

Format data konseptual:

```text
[
  [pixel_1, pixel_2, pixel_3, ..., label],
  [pixel_1, pixel_2, pixel_3, ..., label],
  [pixel_1, pixel_2, pixel_3, ..., label]
]
```

Jika nama file diisi tanpa ekstensi, aplikasi tetap menyimpan sebagai `.npy`.

Contoh:

```text
Input nama file: dataset
Output file: dataset.npy
```

### 5. Randomize Dataset

Tahap ini membaca dataset `.npy`, mengacak urutan baris, lalu menyimpan ulang file tersebut.

Randomize berguna agar urutan data tidak bias sebelum training model.

## Catatan Penggunaan Folder

Untuk workflow yang rapi, gunakan folder berbeda untuk setiap tahap. Contoh:

```text
dataset_mentah/
dataset_gray/
dataset_resize/
dataset_binary/
dataset_final/
```

Contoh alur:

1. Input `dataset_mentah`, output `dataset_gray`, jalankan grayscale.
2. Input `dataset_gray`, output `dataset_resize`, jalankan resizing.
3. Input `dataset_resize`, output `dataset_binary`, jalankan binarization.
4. Input `dataset_binary`, output `dataset_final`, jalankan create dataset.
5. Output `dataset_final`, jalankan randomize dataset.

## Output File

Ringkasan nama output:

```text
Grayscale:      nama_gray.ext
Average Pool:   nama_average_ROWxCOL.ext
Max Pool:       nama_max_ROWxCOL.ext
Binarization:   nama_binTHRESHOLD.ext
Dataset:        dataset.npy
```

Contoh:

```text
huruf_gray.jpg
huruf_average_20x30.jpg
huruf_max_20x30.jpg
huruf_bin128.jpg
dataset.npy
```

## Validasi Input

Aplikasi melakukan validasi untuk:

- Folder input harus ada.
- Folder output harus ada.
- Row dan column resize harus bilangan bulat positif.
- Threshold harus berada pada rentang 0 sampai 255.
- Label dataset tidak boleh kosong.
- Nama file dataset tidak boleh kosong.

## Testing Cepat

Untuk memastikan file Python tidak memiliki error sintaks, jalankan:

```bash
python -m py_compile app.py backend_controller.py preprocessing.py dataset_tools.py
```

Jika tidak ada output error, file berhasil dikompilasi.

## Catatan untuk GitHub

Sebelum push project ke GitHub, cek perubahan dengan:

```bash
git status
git diff
```

Stage file yang relevan:

```bash
git add app.py backend_controller.py preprocessing.py dataset_tools.py README.md
```

Commit:

```bash
git commit -m "Document preprocessing studio workflow"
```

Push:

```bash
git push
```

Hindari commit file output sementara seperti hasil grayscale, resize, binarization, atau dataset `.npy` jika file tersebut tidak diminta masuk repository.

## Troubleshooting

Jika preview gambar tidak muncul, pastikan Pillow sudah terinstall:

```bash
pip install pillow
```

Jika proses dataset gagal karena ukuran fitur berbeda, pastikan semua gambar yang dibuat dataset sudah melewati tahap resize ke ukuran yang sama.

Jika menu kiri terlihat terpotong, gunakan scrollbar pada panel kiri.

Jika output tidak terlihat langsung, klik tombol Refresh pada area Product Surface atau cek folder output secara langsung.
