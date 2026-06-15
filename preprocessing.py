import numpy as np
import matplotlib.pyplot as plt


ROW_CROP = 0.05
COL_CROP = 0.05
READY_ROWS = 20
READY_COLS = 20
READY_CHANNELS = 3


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


def ready_image(input_path, output_path, threshold):
    pic_ori = plt.imread(input_path)
    pic_ori = _to_uint8(pic_ori)
    row, col = np.shape(pic_ori)[0], np.shape(pic_ori)[1]

    row_margin = round(ROW_CROP * row)
    col_margin = round(COL_CROP * col)
    pic_crop = pic_ori[row_margin:row - row_margin, col_margin:col - col_margin, :]

    pic_asal = pic_crop.astype(np.float16)
    row_asal, col_asal, _ch_asal = pic_asal.shape
    row_hasil, col_hasil, ch_hasil = READY_ROWS, READY_COLS, READY_CHANNELS

    delta_row = round(row_asal / READY_ROWS)
    delta_col = round(col_asal / READY_COLS)
    pooled_rows = min(row_hasil, (row_asal - delta_row + delta_row - 1) // delta_row)
    pooled_cols = min(col_hasil, (col_asal - delta_col + delta_col - 1) // delta_col)
    usable_rows = pooled_rows * delta_row
    usable_cols = pooled_cols * delta_col

    pooled = pic_asal[:usable_rows, :usable_cols, :].reshape(
        pooled_rows,
        delta_row,
        pooled_cols,
        delta_col,
        ch_hasil,
    )
    pic_res = np.zeros(shape=(row_hasil, col_hasil, ch_hasil), dtype=np.float16)
    pic_res[:pooled_rows, :pooled_cols, :] = pooled.mean(axis=(1, 3))

    average = (pic_res[:, :, 0] + pic_res[:, :, 1] + pic_res[:, :, 2]) / 3
    pic_gs = np.zeros_like(pic_res)
    pic_gs[:, :, 0] = average
    pic_gs[:, :, 1] = average
    pic_gs[:, :, 2] = average

    pic_gs_hitam = 255 - pic_gs

    pic_gs_hitam_kontras = 1 * pic_gs_hitam
    binary = pic_gs_hitam_kontras[:, :, 0] >= threshold
    pic_gs_hitam_kontras[:, :, :] = 0
    pic_gs_hitam_kontras[binary, :] = 255

    plt.imsave(output_path, pic_gs_hitam_kontras.astype(np.uint8))


def _to_uint8(img):
    if img.dtype == np.uint8:
        return img
    return np.clip(img * 255 if img.max() <= 1.0 else img, 0, 255).astype(np.uint8)
