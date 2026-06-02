import numpy as np
import matplotlib.pyplot as plt


def grayscale_image(input_path, output_path):
    img = plt.imread(input_path)

    if img.ndim == 2:
        gray = img
    else:
        rgb = img[:, :, :3]
        r = rgb[:, :, 0]
        g = rgb[:, :, 1]
        b = rgb[:, :, 2]
        gray = 0.299 * r + 0.587 * g + 0.114 * b

    if gray.dtype != np.uint8:
        gray = np.clip(gray * 255 if gray.max() <= 1.0 else gray, 0, 255).astype(
            np.uint8
        )

    plt.imsave(output_path, gray, cmap="gray")


def resize_images(input_folder, output_folder, method, rows, cols):
    raise NotImplementedError(
        "Isi resize_images() di preprocessing.py dengan average atau max pooling. "
        f"Input: {input_folder}. Output: {output_folder}. Method: {method}. Size: {rows}x{cols}."
    )


def binarize_images(input_folder, output_folder, threshold):
    raise NotImplementedError(
        "Isi binarize_images() di preprocessing.py dengan algoritma thresholding. "
        f"Input: {input_folder}. Output: {output_folder}. Threshold: {threshold}."
    )
