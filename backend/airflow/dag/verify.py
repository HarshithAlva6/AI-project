import h5py
import numpy as np
from collections import Counter

def verify_hdf5_data(hdf5_file, image_size=(224, 224)):
    # Open the HDF5 file for reading
    with h5py.File(hdf5_file, "r") as h5f:
        labels_dataset = h5f["labels"]
        label_map = eval(h5f.attrs["label_map"])  # Convert the string back to a dictionary
        reverse_label_map = {v: k for k, v in label_map.items()}  # Reverse label mapping

        # Count occurrences of each label
        label_counts = Counter(labels_dataset[:])

        # Display the distribution
        print("Label Distribution:")
        for label_id, count in label_counts.items():
            label_name = reverse_label_map[label_id]
            print(f"Label: {label_name} (ID: {label_id}), Count: {count}")

        # Visualize the distribution
        labels = [reverse_label_map[label_id] for label_id in label_counts.keys()]
        counts = list(label_counts.values())

        print("Label", labels, "counts", counts)
        
if __name__ == "__main__":
    hdf5_file_path = "/opt/airflow/storage/fin_data.h5"
    verify_hdf5_data(hdf5_file_path)
