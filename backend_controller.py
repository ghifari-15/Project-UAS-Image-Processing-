import os

from dataset_tools import create_dataset, randomize_dataset
from preprocessing import binarize_image, grayscale_image, resize_image


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def list_image_files(input_folder):
    return [
        name
        for name in os.listdir(input_folder)
        if name.lower().endswith(IMAGE_EXTENSIONS)
    ]


def grayscale_images(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    image_files = list_image_files(input_folder)

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_gray{ext}")
        grayscale_image(input_path, output_path)

    return len(image_files)


def resize_images(input_folder, output_folder, method, rows, cols):
    os.makedirs(output_folder, exist_ok=True)
    image_files = list_image_files(input_folder)

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_{method}_{rows}x{cols}{ext}")
        resize_image(input_path, output_path, method, rows, cols)

    return len(image_files)


def binarize_images(input_folder, output_folder, threshold):
    os.makedirs(output_folder, exist_ok=True)
    image_files = list_image_files(input_folder)

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_bin{threshold}{ext}")
        binarize_image(input_path, output_path, threshold)

    return len(image_files)


def run_stage(stage, **kwargs):
    if stage == "grayscale":
        total_images = grayscale_images(kwargs["input_folder"], kwargs["output_folder"])
        return f"Color-to-Grayscale Conversion selesai. {total_images} gambar diproses."

    if stage == "resize":
        total_images = resize_images(
            kwargs["input_folder"],
            kwargs["output_folder"],
            kwargs["method"],
            kwargs["rows"],
            kwargs["cols"],
        )
        return f"Resizing selesai. {total_images} gambar diproses."

    if stage == "binarization":
        total_images = binarize_images(kwargs["input_folder"], kwargs["output_folder"], kwargs["threshold"])
        return f"Binarization selesai. {total_images} gambar diproses."

    if stage == "create_dataset":
        total_rows, dataset_path = create_dataset(
            kwargs["input_folder"],
            kwargs["output_folder"],
            kwargs["label"],
            kwargs["dataset_name"],
        )
        return f"Dataset .npy selesai dibuat. {total_rows} data disimpan ke {dataset_path}."

    if stage == "randomize_dataset":
        total_rows, dataset_path = randomize_dataset(kwargs["output_folder"], kwargs["dataset_name"])
        return f"Randomize dataset selesai. {total_rows} data diacak di {dataset_path}."

    raise ValueError(f"Tahap tidak dikenal: {stage}")
