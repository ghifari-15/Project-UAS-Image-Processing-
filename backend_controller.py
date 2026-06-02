import os

from dataset_tools import create_dataset, randomize_dataset
from preprocessing import binarize_images, grayscale_image, resize_images


def grayscale_images(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    image_files = [
        name
        for name in os.listdir(input_folder)
        if name.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_gray{ext}")
        grayscale_image(input_path, output_path)

    return len(image_files)


def run_stage(stage, **kwargs):
    if stage == "grayscale":
        total_images = grayscale_images(kwargs["input_folder"], kwargs["output_folder"])
        return f"Color-to-Grayscale Conversion selesai. {total_images} gambar diproses."

    if stage == "resize":
        resize_images(
            kwargs["input_folder"],
            kwargs["output_folder"],
            kwargs["method"],
            kwargs["rows"],
            kwargs["cols"],
        )
        return "Resizing selesai dipanggil."

    if stage == "binarization":
        binarize_images(kwargs["input_folder"], kwargs["output_folder"], kwargs["threshold"])
        return "Binarization selesai dipanggil."

    if stage == "create_dataset":
        create_dataset(
            kwargs["input_folder"],
            kwargs["output_folder"],
            kwargs["label"],
            kwargs["dataset_name"],
        )
        return "Dataset dan label selesai dipanggil."

    if stage == "randomize_dataset":
        randomize_dataset(kwargs["output_folder"], kwargs["dataset_name"])
        return "Randomize dataset selesai dipanggil."

    raise ValueError(f"Tahap tidak dikenal: {stage}")
