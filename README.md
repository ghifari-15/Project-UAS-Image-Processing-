# Dataset Preprocessing Studio

Dataset Preprocessing Studio adalah aplikasi desktop berbasis Tkinter untuk membantu proses preprocessing dataset gambar sebelum digunakan pada tahap training model, khususnya alur pengolahan citra seperti grayscale, resizing, binarization, pembuatan dataset, dan randomisasi dataset.

Tool ini dibuat untuk memproses banyak gambar dalam satu folder sekaligus. User cukup memilih folder input awal dan folder output induk, lalu menjalankan tahap preprocessing dari interface aplikasi. Setelah satu tahap selesai, folder hasil tahap tersebut otomatis menjadi input untuk tahap berikutnya.

## Fitur

- Preview gambar before/after menggunakan Tkinter, NumPy, dan Matplotlib.
- Konversi color-to-grayscale untuk semua gambar dalam folder.
- Resize gambar menggunakan average pooling atau max pooling.
- Binarization dengan nilai threshold 0 sampai 255.
- Label otomatis dari nama file, dengan opsi koreksi manual ke `labels.csv`.
- Pembuatan dataset berformat `.csv` dari kumpulan gambar dan label.
- Randomize dataset ANN `.npy` atau dataset inspeksi `.csv`.
- Panel menu kiri scrollable agar tetap usable pada viewport kecil.
- Input folder otomatis mengikuti hasil tahap preprocessing terakhir.
- Preview hasil preprocessing dari subfolder output seperti `grayscale`, `resize`, dan `binarization`.
- Alert sukses setelah setiap proses selesai.

## Struktur File Utama

```text
.
├── main.py
├── tool_app.py
├── backend_controller.py
├── preprocessing.py
├── dataset_tools.py
└── README.md
```

Keterangan:

- `main.py`: entry point aplikasi.
- `tool_app.py`: interface Tkinter, preview gambar, validasi input user, dan pemanggilan stage preprocessing.
- `backend_controller.py`: penghubung antara UI dan modul processing. File ini menangani proses folder, nama output, dan routing stage.
- `preprocessing.py`: algoritma image processing per gambar menggunakan `numpy` dan `matplotlib`.
- `dataset_tools.py`: pembuatan dataset `.csv`, penyimpanan label CSV, dan randomisasi dataset.

## Kebutuhan Library

Pastikan Python sudah terinstall. Library yang digunakan:

```text
numpy
matplotlib
```

Install dependency dengan:

```bash
pip install numpy matplotlib
```

Tkinter biasanya sudah termasuk dalam instalasi Python standar di Windows.

## Cara Menjalankan Aplikasi

Jalankan command berikut dari root project:

```bash
python main.py
```

Setelah aplikasi terbuka:

1. Pilih folder input berisi gambar.
2. Pilih folder output untuk menyimpan hasil proses.
3. Jalankan tahap preprocessing yang dibutuhkan.
4. Setelah tahap selesai, aplikasi otomatis mengganti `Input` ke folder hasil tahap tersebut.
5. Jalankan tahap berikutnya tanpa perlu browse input folder ulang.
6. Lihat hasil terbaru di area preview.

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

Output disimpan ke subfolder `grayscale` di dalam folder output induk.

Contoh output:

```text
grayscale/gambar_gray.jpg
grayscale/huruf_gray.png
```

Setelah proses selesai, aplikasi menampilkan alert sukses, jumlah gambar yang diproses, dan otomatis mengubah `Input` menjadi folder `grayscale`.

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

Output disimpan ke subfolder `resize` di dalam folder output induk.

Contoh output average pooling:

```text
resize/gambar_gray_average_20x30.jpg
```

Contoh output max pooling:

```text
resize/gambar_gray_max_20x30.jpg

Setelah proses selesai, aplikasi otomatis mengubah `Input` menjadi folder `resize`.
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

Output disimpan ke subfolder `binarization` di dalam folder output induk.

Contoh output:

```text
binarization/gambar_gray_average_20x30_bin128.jpg
```

Setelah proses selesai, aplikasi otomatis mengubah `Input` menjadi folder `binarization`.

### 4. Labeling Per Gambar (Opsional)

Jika class sudah ada di nama file, tahap labeling manual tidak wajib. Aplikasi bisa mengambil label otomatis dari nama file saat tombol `Dataset & Label` dijalankan.

Contoh:

```text
hangul_a_01.jpg  -> a
hangul_eo_01.jpg -> eo
hangul_ho_01.jpg -> ho
```

Label manual tetap tersedia untuk koreksi jika ada nama file yang tidak sesuai.

Default file label:

```text
labels.csv
```

Format CSV:

```csv
filename,label
hangul_a_01.jpg,a
hangul_eo_01.jpg,eo
```

Kolom `filename` berisi nama file gambar, sedangkan kolom `label` berisi target kelas untuk training ANN.

### 5. Dataset & Label

Tahap ini membuat dataset dari semua gambar dalam folder input. Label diambil dari `labels.csv` jika tersedia. Jika tidak ada, label otomatis diambil dari nama file.

Default nama file inspeksi:

```text
dataset.csv
```

Setiap gambar akan dicocokkan dengan label berdasarkan nama file. Pixel satu channel gambar di-flatten menjadi fitur dengan pendekatan low-level seperti script referensi ANN.

Output utama untuk ANN:

```text
inputs_<jumlah_sampel>_<jumlah_pixel+1>.npy
labels_<jumlah_sampel>_<jumlah_kelas+1>.npy
class_map.csv
```

Kolom ke-0 pada `inputs_*.npy` dan `labels_*.npy` berisi nomor sampel. Kolom input berikutnya berisi pixel. Kolom label berikutnya berisi one-hot class.

Selain itu aplikasi tetap membuat `dataset.csv` untuk inspeksi manual.

Format data konseptual:

```csv
pixel_1,pixel_2,pixel_3,...,label
0,255,255,...,a
255,0,0,...,eo
```

Jika nama file diisi tanpa ekstensi, aplikasi tetap menyimpan sebagai `.csv`.

Contoh:

```text
Input nama file: dataset
Output file: dataset.csv
```

Jika `labels.csv` tidak ada, aplikasi tetap membuat dataset dengan label hasil parsing nama file.

### 6. Randomize Dataset

Tahap ini mengacak dataset ANN jika file `inputs_*.npy` dan `labels_*.npy` tersedia. Outputnya:

```text
random_inputs_<jumlah_sampel>_<jumlah_pixel+1>.npy
random_labels_<jumlah_sampel>_<jumlah_kelas+1>.npy
```

Jika file ANN belum ada, aplikasi mengacak `dataset.csv` sebagai fallback.

Randomize berguna agar urutan data tidak bias sebelum training model.

## Catatan Penggunaan Folder

Gunakan satu folder input awal dan satu folder output induk. Aplikasi akan membuat subfolder hasil secara otomatis. Contoh:

```text
dataset_mentah/
hasil_preprocessing/
├── grayscale/
├── resize/
├── binarization/
└── dataset_label/
```

Contoh alur:

1. Pilih input `dataset_mentah`.
2. Pilih output `hasil_preprocessing`.
3. Jalankan `Color-to-Grayscale Conversion`. Input otomatis menjadi `hasil_preprocessing/grayscale`.
4. Jalankan `Resizing`. Input otomatis menjadi `hasil_preprocessing/resize`.
5. Jalankan `Binarization`. Input otomatis menjadi `hasil_preprocessing/binarization`.
6. Jika nama file sudah memuat class, langsung jalankan `Dataset & Label`.
7. Jika perlu koreksi label, pilih gambar di preview, isi label, lalu klik `Save Label` atau `Save & Next`.
8. Jalankan `Randomize Dataset` setelah dataset ANN dibuat.

Jika ingin mengulang dari data mentah atau menjalankan tahap tertentu dari folder lain, user tetap bisa memilih folder input manual melalui tombol `Browse`.

## Output File

Ringkasan nama output:

```text
Grayscale:      grayscale/nama_gray.ext
Average Pool:   resize/nama_average_<row>x<col>.ext
Max Pool:       resize/nama_max_<row>x<col>.ext
Binarization:   binarization/nama_bin<threshold>.ext
Label CSV:      labels.csv
Dataset CSV:    dataset.csv
Input ANN:      dataset_label/inputs_*.npy
Label ANN:      dataset_label/labels_*.npy
Random ANN:     dataset_label/random_inputs_*.npy, dataset_label/random_labels_*.npy
```

Contoh:

```text
grayscale/huruf_gray.jpg
resize/huruf_gray_average_20x30.jpg
binarization/huruf_gray_average_20x30_bin128.jpg
labels.csv
dataset.csv
dataset_label/inputs_200_601.npy
dataset_label/labels_200_11.npy
dataset_label/random_inputs_200_601.npy
dataset_label/random_labels_200_11.npy
```

## Validasi Input

Aplikasi melakukan validasi untuk:

- Folder input harus ada.
- Folder output harus ada.
- Row dan column resize harus bilangan bulat positif.
- Threshold harus berada pada rentang 0 sampai 255.
- Label gambar tidak boleh kosong saat menyimpan label manual.
- CSV label manual harus memiliki kolom `filename,label`.
- Nama file dataset tidak boleh kosong.

## Testing Cepat

Untuk memastikan file Python tidak memiliki error sintaks, jalankan:

```bash
python -m py_compile main.py tool_app.py backend_controller.py preprocessing.py dataset_tools.py
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
git add main.py tool_app.py backend_controller.py preprocessing.py dataset_tools.py README.md
```

Commit:

```bash
git commit -m "Document preprocessing studio workflow"
```

Push:

```bash
git push
```

Hindari commit file output sementara seperti hasil grayscale, resize, binarization, `labels.csv`, `dataset.csv`, atau dataset ANN `.npy` jika file tersebut tidak diminta masuk repository.

## Troubleshooting

Jika preview gambar tidak muncul, pastikan file gambar dapat dibaca oleh Matplotlib dan formatnya `.jpg`, `.jpeg`, atau `.png`.

Jika proses dataset gagal karena ukuran fitur berbeda, pastikan semua gambar yang dibuat dataset sudah melewati tahap resize ke ukuran yang sama.

Jika menu kiri terlihat terpotong, gunakan scrollbar pada panel kiri.

Jika output tidak terlihat langsung, klik tombol Refresh pada area preview atau cek subfolder di dalam folder output secara langsung.

Jika tahap berikutnya memproses folder yang salah, cek field `Input`. Setelah preprocessing berhasil, field tersebut seharusnya otomatis mengarah ke subfolder hasil tahap terakhir.
