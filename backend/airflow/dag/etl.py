import os
from PIL import Image
import numpy as np
import h5py

def run_etl(output_file="/opt/airflow/storage/fin_data.h5", chunk_size=500):
    dataset_path = "/opt/airflow/dags/dag/Indian Food Images/Indian Food Images"
    total_images = 0
    skipped_images = 0

    with h5py.File(output_file, "w") as h5f:
        # Use uint8 for images and int32 for labels, with gzip compression
        images_dataset = h5f.create_dataset(
            "images", shape=(0, 224, 224, 3), maxshape=(None, 224, 224, 3),
            dtype=np.uint8, compression="gzip", compression_opts=9
        )
        labels_dataset = h5f.create_dataset(
            "labels", shape=(0,), maxshape=(None,), dtype="int32", compression="gzip", compression_opts=9
        )

        images_list = []
        labels_list = []

        unique_labels_map = {}
        current_label_id = 0

        for root, _, files in os.walk(dataset_path):
            for file in files:
                if file.endswith(('.jpg', '.png')):
                    try:
                        image_path = os.path.join(root, file)
                        img = Image.open(image_path).convert("RGB").resize((224, 224))
                        img_array = np.array(img, dtype=np.uint8)  # Store as uint8

                        label = os.path.basename(root)
                        if label not in unique_labels_map:
                            unique_labels_map[label] = current_label_id
                            current_label_id += 1

                        encoded_label = unique_labels_map[label]
                        images_list.append(img_array)
                        labels_list.append(encoded_label)
                        total_images += 1

                        if len(images_list) >= chunk_size:
                            append_to_hdf5(images_dataset, labels_dataset, images_list, labels_list)
                            images_list.clear()
                            labels_list.clear()
                            print(f"Saved {total_images} images so far...")
                    except Exception as e:
                        skipped_images += 1
                        print(f"Skipped {image_path}: {e}")

        if images_list:
            append_to_hdf5(images_dataset, labels_dataset, images_list, labels_list)

    print(f"ETL complete. Total images: {total_images}, Skipped: {skipped_images}")

def append_to_hdf5(images_dataset, labels_dataset, images_list, labels_list):
    new_size = images_dataset.shape[0] + len(images_list)
    images_dataset.resize(new_size, axis=0)
    labels_dataset.resize(new_size, axis=0)
    images_dataset[-len(images_list):] = np.array(images_list, dtype=np.uint8)
    labels_dataset[-len(labels_list):] = np.array(labels_list, dtype=np.int32)

if __name__ == "__main__":
    print("Starting etl process...")
    run_etl()