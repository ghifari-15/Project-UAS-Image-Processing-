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


def resize_image(input_path, output_path, method, rows, cols):
    img = plt.imread(input_path)
    img = _to_uint8(img)

    if img.ndim == 2:
        img = img[:, :, np.newaxis]
    else:
        img = img[:, :, :3]

    row_asal, col_asal, channels = img.shape
    row_hasil = int(rows)
    col_hasil = int(cols)
    resized = np.zeros((row_hasil, col_hasil, channels), dtype=np.float32)

    for i in range(row_hasil):
        row_start = round(i * row_asal / row_hasil)
        row_end = round((i + 1) * row_asal / row_hasil)
        for j in range(col_hasil):
            col_start = round(j * col_asal / col_hasil)
            col_end = round((j + 1) * col_asal / col_hasil)
            region = img[
                row_start:max(row_end, row_start + 1),
                col_start:max(col_end, col_start + 1),
                :,
            ]

            if method == "average":
                resized[i, j, :] = np.mean(region, axis=(0, 1))
            elif method == "max":
                resized[i, j, :] = np.max(region, axis=(0, 1))
            else:
                raise ValueError("Method harus 'average' atau 'max'.")

    resized = np.clip(resized, 0, 255).astype(np.uint8)
    if channels == 1:
        plt.imsave(output_path, resized[:, :, 0], cmap="gray")
    else:
        plt.imsave(output_path, resized)


def binarize_image(input_path, output_path, threshold):
    img = plt.imread(input_path)
    img = _to_uint8(img)

    if img.ndim == 2:
        gray = img
    else:
        rgb = img[:, :, :3]
        gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

    binary = np.zeros(gray.shape, dtype=np.uint8)
    binary[gray >= threshold] = 255
    plt.imsave(output_path, binary, cmap="gray")


def _to_uint8(img):
    if img.dtype == np.uint8:
        return img
    return np.clip(img * 255 if img.max() <= 1.0 else img, 0, 255).astype(np.uint8)
