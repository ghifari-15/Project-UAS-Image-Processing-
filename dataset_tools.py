import os

import matplotlib.pyplot as plt
import numpy as np


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def create_dataset(input_folder, output_folder, label, dataset_name):
    os.makedirs(output_folder, exist_ok=True)
    dataset_path = _npy_path(output_folder, dataset_name)
    image_files = [
        name
        for name in os.listdir(input_folder)
        if name.lower().endswith(IMAGE_EXTENSIONS)
    ]

    rows = []
    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        img = plt.imread(input_path)
        img = _to_uint8(img)
        features = img.reshape(-1)
        rows.append(np.append(features, label))

    if not rows:
        raise ValueError("Tidak ada gambar .jpg, .jpeg, atau .png di folder input.")

    dataset = np.array(rows)
    np.save(dataset_path, dataset)
    return len(rows), dataset_path


def randomize_dataset(output_folder, dataset_name):
    dataset_path = _npy_path(output_folder, dataset_name)
    if not os.path.isfile(dataset_path):
        raise FileNotFoundError(f"Dataset tidak ditemukan: {dataset_path}")

    dataset = np.load(dataset_path, allow_pickle=True)
    randomized = np.random.permutation(dataset)
    np.save(dataset_path, randomized)
    return len(randomized), dataset_path


def _npy_path(output_folder, dataset_name):
    base, ext = os.path.splitext(dataset_name)
    filename = dataset_name if ext.lower() == ".npy" else f"{base or dataset_name}.npy"
    return os.path.join(output_folder, filename)


def _to_uint8(img):
    if img.dtype == np.uint8:
        return img
    return np.clip(img * 255 if img.max() <= 1.0 else img, 0, 255).astype(np.uint8)
