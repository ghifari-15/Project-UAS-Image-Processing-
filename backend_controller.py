import os

from dataset_tools import create_dataset, randomize_dataset
from preprocessing import binarize_image, grayscale_image, ready_image, resize_image


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def list_image_files(input_folder):
    return [
        name
        for name in os.listdir(input_folder)
        if name.lower().endswith(IMAGE_EXTENSIONS)
    ]


def image_paths(input_folder):
    return [os.path.join(input_folder, filename) for filename in list_image_files(input_folder)]


def dataset_csv_path(output_folder, dataset_name):
    base, ext = os.path.splitext(dataset_name)
    filename = dataset_name if ext.lower() == ".csv" else f"{base or dataset_name}.csv"
    return os.path.join(output_folder, filename)


def csv_path(output_folder, csv_name):
    base, ext = os.path.splitext(csv_name)
    filename = csv_name if ext.lower() == ".csv" else f"{base or csv_name}.csv"
    return os.path.join(output_folder, filename)


def grayscale_images(input_folder, output_folder):
    output_folder = os.path.join(output_folder, "grayscale")
    os.makedirs(output_folder, exist_ok=True)
    image_files = list_image_files(input_folder)

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_gray{ext}")
        grayscale_image(input_path, output_path)

    return len(image_files), output_folder


def resize_images(input_folder, output_folder, method, rows, cols):
    output_folder = os.path.join(output_folder, "resize")
    os.makedirs(output_folder, exist_ok=True)
    image_files = list_image_files(input_folder)

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_{method}_{rows}x{cols}{ext}")
        resize_image(input_path, output_path, method, rows, cols)

    return len(image_files), output_folder


def binarize_images(input_folder, output_folder, threshold):
    output_folder = os.path.join(output_folder, "binarization")
    os.makedirs(output_folder, exist_ok=True)
    image_files = list_image_files(input_folder)

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_bin{threshold}{ext}")
        binarize_image(input_path, output_path, threshold)

    return len(image_files), output_folder


def ready_images(input_folder, output_folder, threshold):
    output_folder = os.path.join(output_folder, "binarization")
    os.makedirs(output_folder, exist_ok=True)
    image_files = list_image_files(input_folder)

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{base}_ready{ext}")
        ready_image(input_path, output_path, threshold)

    return len(image_files), output_folder


def run_stage(stage, **kwargs):
    if stage == "grayscale":
        total_images, stage_output_folder = grayscale_images(kwargs["input_folder"], kwargs["output_folder"])
        return f"Color-to-Grayscale Conversion selesai. {total_images} gambar diproses ke {stage_output_folder}."

    if stage == "resize":
        total_images, stage_output_folder = resize_images(
            kwargs["input_folder"],
            kwargs["output_folder"],
            kwargs["method"],
            kwargs["rows"],
            kwargs["cols"],
        )
        return f"Resizing selesai. {total_images} gambar diproses ke {stage_output_folder}."

    if stage == "binarization":
        total_images, stage_output_folder = binarize_images(kwargs["input_folder"], kwargs["output_folder"], kwargs["threshold"])
        return f"Binarization selesai. {total_images} gambar diproses ke {stage_output_folder}."

    if stage == "create_dataset":
        os.makedirs(kwargs["output_folder"], exist_ok=True)
        dataset_path = dataset_csv_path(kwargs["output_folder"], kwargs["dataset_name"])
        labels_path = csv_path(kwargs["labels_folder"], kwargs["labels_name"])
        total_rows, dataset_path, inputs_path, labels_output_path, class_map_path, dataset_index_path = create_dataset(
            image_paths(kwargs["input_folder"]),
            dataset_path,
            labels_path,
        )
        return " ".join([
            f"Dataset & Label selesai. {total_rows} data diproses.",
            f"CSV inspeksi: {dataset_path}.",
            f"Input ANN: {inputs_path}.",
            f"Label ANN: {labels_output_path}.",
            f"Class map: {class_map_path}.",
            f"Index map: {dataset_index_path}.",
        ])

    if stage == "randomize_dataset":
        dataset_path = dataset_csv_path(kwargs["output_folder"], kwargs["dataset_name"])
        if not os.path.isfile(dataset_path):
            raise FileNotFoundError(f"Dataset tidak ditemukan: {dataset_path}")
        total_rows, dataset_path = randomize_dataset(dataset_path)
        return f"Randomize dataset selesai. {total_rows} data diacak di {dataset_path}."

    raise ValueError(f"Tahap tidak dikenal: {stage}")
