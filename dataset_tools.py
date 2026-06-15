import csv
import os
import re
import shutil

import matplotlib.pyplot as plt
import numpy as np


def load_labels(labels_path):
    if not os.path.isfile(labels_path):
        raise FileNotFoundError(f"File label tidak ditemukan: {labels_path}")

    labels = {}
    with open(labels_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "filename" not in reader.fieldnames or "label" not in reader.fieldnames:
            raise ValueError("CSV label harus punya kolom: filename,label")

        for row in reader:
            filename = row.get("filename", "").strip()
            label = row.get("label", "").strip()
            if filename and label:
                labels[filename] = label

    return labels


def label_from_filename(filename):
    name = os.path.splitext(os.path.basename(filename))[0]
    if name.endswith("_ready"):
        name = name[:-6]
    name = re.sub(r"\s*\(\d+\)$", "", name)
    parts = [part for part in re.split(r"[_\-\s]+", name) if part]

    if len(parts) >= 2 and parts[0].lower() == "hangul":
        return parts[1]
    if len(parts) >= 2 and parts[-1].isdigit():
        return parts[-2]
    if len(parts) >= 2:
        return parts[0]
    return name


def save_label(labels_path, filename, label):
    os.makedirs(os.path.dirname(labels_path), exist_ok=True)
    labels = {}
    if os.path.isfile(labels_path):
        labels = load_labels(labels_path)

    labels[filename] = label
    with open(labels_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["filename", "label"])
        writer.writeheader()
        for saved_filename in sorted(labels):
            writer.writerow({"filename": saved_filename, "label": labels[saved_filename]})

    return labels_path


def create_dataset(image_paths, dataset_path, labels_path):
    labels = load_labels(labels_path) if os.path.isfile(labels_path) else {}
    rows = []
    label_order = []
    missing_labels = []
    for input_path in image_paths:
        filename = os.path.basename(input_path)
        label = labels.get(filename) or label_from_filename(filename)
        if not label:
            missing_labels.append(filename)
            continue

        img = plt.imread(input_path)
        img = _to_uint8(img)
        features = _single_channel(img).reshape(-1)
        rows.append((input_path, features, label))
        if label not in label_order:
            label_order.append(label)

    if missing_labels:
        names = ", ".join(missing_labels[:5])
        extra = "" if len(missing_labels) <= 5 else f" dan {len(missing_labels) - 5} lainnya"
        raise ValueError(f"Ada gambar yang belum punya label di CSV: {names}{extra}")

    if not rows:
        raise ValueError("Tidak ada gambar .jpg, .jpeg, atau .png di folder input.")

    feature_count = len(rows[0][1])
    with open(dataset_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["sample", "label", "feature_count"])
        for sample_index, (_input_path, features, label) in enumerate(rows):
            _validate_feature_count(features, feature_count)
            writer.writerow([sample_index, label, feature_count])

    dataset_folder = os.path.join(os.path.dirname(dataset_path), "dataset_label")
    dataset_images_folder = os.path.join(dataset_folder, "images")
    os.makedirs(dataset_images_folder, exist_ok=True)

    inputs_path = os.path.join(dataset_folder, f"inputs_{len(rows)}_{feature_count + 1}.npy")
    labels_output_path = os.path.join(dataset_folder, f"labels_{len(rows)}_{len(label_order) + 1}.npy")
    class_map_path = os.path.join(dataset_folder, "class_map.csv")
    dataset_index_path = os.path.join(dataset_folder, "dataset_index.csv")

    inputs_dataset = np.zeros(shape=(len(rows), feature_count + 1), dtype=np.uint16)
    labels_dataset = np.zeros(shape=(len(rows), len(label_order) + 1), dtype=float)
    label_to_index = {label: index for index, label in enumerate(label_order)}

    with open(dataset_index_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["sample_index", "filename", "label", "image_copy"])

        for sample_index, (input_path, features, label) in enumerate(rows):
            _validate_feature_count(features, feature_count)
            inputs_dataset[sample_index, 0] = sample_index
            inputs_dataset[sample_index, 1:] = features
            labels_dataset[sample_index, 0] = sample_index
            labels_dataset[sample_index, label_to_index[label] + 1] = 1

            copied_name = f"{sample_index:03d}_{os.path.basename(input_path)}"
            copied_path = os.path.join(dataset_images_folder, copied_name)
            shutil.copy2(input_path, copied_path)
            writer.writerow([sample_index, os.path.basename(input_path), label, os.path.join("images", copied_name)])

    np.save(inputs_path, inputs_dataset)
    np.save(labels_output_path, labels_dataset)

    with open(class_map_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["class_index", "label"])
        for label, index in label_to_index.items():
            writer.writerow([index, label])

    return len(rows), dataset_path, inputs_path, labels_output_path, class_map_path, dataset_index_path


def randomize_dataset(dataset_path):
    folder = os.path.dirname(dataset_path)
    npy_result = randomize_ann_datasets(folder)
    if npy_result:
        return npy_result

    with open(dataset_path, newline="", encoding="utf-8") as file:
        reader = list(csv.reader(file))

    if not reader:
        raise ValueError("Dataset CSV kosong.")

    header = reader[0]
    rows = reader[1:]
    randomized = np.random.permutation(rows).tolist() if rows else []

    with open(dataset_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(randomized)

    return len(randomized), dataset_path


def randomize_ann_datasets(folder):
    dataset_folder = os.path.join(folder, "dataset_label")
    search_folder = dataset_folder if os.path.isdir(dataset_folder) else folder
    inputs_files = sorted(
        filename
        for filename in os.listdir(search_folder)
        if filename.startswith("inputs_") and filename.endswith(".npy")
    )
    labels_files = sorted(
        filename
        for filename in os.listdir(search_folder)
        if filename.startswith("labels_") and filename.endswith(".npy")
    )
    if not inputs_files or not labels_files:
        return None

    inputs_path = os.path.join(search_folder, inputs_files[-1])
    labels_path = os.path.join(search_folder, labels_files[-1])
    inputs = np.load(inputs_path)
    labels = np.load(labels_path)
    if inputs.shape[0] != labels.shape[0]:
        raise ValueError("Jumlah baris inputs dan labels tidak sama.")

    m, n = np.shape(inputs)
    r, s = np.shape(labels)

    a = []
    for i in range(0, m):
        a.append(i)
    np.random.shuffle(a)

    inputs_random = np.zeros(shape=(m, n), dtype=float)
    labels_random = np.zeros(shape=(r, s), dtype=float)

    for i in range(0, m):
        inputs_random[i, :] = inputs[a[i], :]
        labels_random[i, :] = labels[a[i], :]

    random_folder = os.path.join(folder, "randomize_dataset")
    random_images_folder = os.path.join(random_folder, "images")
    os.makedirs(random_images_folder, exist_ok=True)

    random_inputs_path = os.path.join(random_folder, "random_" + os.path.basename(inputs_path))
    random_labels_path = os.path.join(random_folder, "random_" + os.path.basename(labels_path))
    np.save(random_inputs_path, inputs_random)
    np.save(random_labels_path, labels_random)

    dataset_index_path = os.path.join(search_folder, "dataset_index.csv")
    if os.path.isfile(dataset_index_path):
        index_rows = {}
        with open(dataset_index_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                index_rows[int(row["sample_index"])] = row

        random_index_path = os.path.join(random_folder, "random_index.csv")
        with open(random_index_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["random_index", "original_sample_index", "filename", "label", "image_copy"])
            for random_index, original_index in enumerate(a):
                row = index_rows.get(original_index)
                if not row:
                    continue
                source_image = os.path.join(search_folder, row["image_copy"])
                copied_name = f"{random_index:03d}_from_{original_index:03d}_{row['filename']}"
                copied_path = os.path.join(random_images_folder, copied_name)
                if os.path.isfile(source_image):
                    shutil.copy2(source_image, copied_path)
                writer.writerow([random_index, original_index, row["filename"], row["label"], os.path.join("images", copied_name)])

    return inputs.shape[0], f"{random_inputs_path} dan {random_labels_path}"


def _to_uint8(img):
    if img.dtype == np.uint8:
        return img
    return np.clip(img * 255 if img.max() <= 1.0 else img, 0, 255).astype(np.uint8)


def _single_channel(img):
    if img.ndim == 2:
        return img
    return img[:, :, 0]


def _validate_feature_count(features, feature_count):
    if len(features) != feature_count:
        raise ValueError("Ukuran fitur gambar berbeda. Pastikan semua gambar sudah di-resize ke ukuran yang sama.")
