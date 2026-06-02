def create_dataset(input_folder, output_folder, label, dataset_name):
    raise NotImplementedError(
        "Isi create_dataset() di dataset_tools.py untuk membuat dataset beserta label. "
        f"Input: {input_folder}. Output: {output_folder}. Label: {label}. File: {dataset_name}."
    )


def randomize_dataset(output_folder, dataset_name):
    raise NotImplementedError(
        "Isi randomize_dataset() di dataset_tools.py untuk mengacak baris dataset. "
        f"Folder: {output_folder}. File: {dataset_name}."
    )
