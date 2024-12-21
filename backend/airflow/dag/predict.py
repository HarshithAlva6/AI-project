import tensorflow as tf
import h5py
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

class HDF5Sequence(tf.keras.utils.Sequence):
    """Custom data loader for HDF5 files using Sequence API."""
    def __init__(self, file_path, indices, labels, batch_size):
        self.file_path = file_path
        self.indices = indices
        self.labels = labels
        self.batch_size = batch_size

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, idx):
        # Open the file within each batch for thread safety
        with h5py.File(self.file_path, "r") as h5f:
            images = h5f["images"]
            batch_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
            batch_images = np.array([images[i] for i in batch_indices], dtype=np.float32) / 255.0  # Normalize here
            batch_labels = np.array([self.labels[i] for i in batch_indices], dtype=np.int32)
        return batch_images, batch_labels

def run_predict():
    input_path = "/opt/airflow/storage/fin_data.h5"

    # Step 1: Load metadata and prepare label mapping
    with h5py.File(input_path, "r") as h5f:
        total_samples = h5f["images"].shape[0]
        print(f"Total Samples: {total_samples}")

        labels = np.array(h5f["labels"][:])  # Use directly as integers
        unique_labels, integer_labels = np.unique(labels, return_inverse=True)
        print(f"Unique labels: {unique_labels}")
        print(f"Sample mapped labels: {integer_labels[:5]}")

        # Train-validation split
        indices = np.arange(total_samples)
        train_indices = indices[:int(0.8 * total_samples)]
        val_indices = indices[int(0.8 * total_samples):]

    # Compute class weights for imbalance
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(integer_labels),
        y=integer_labels
    )
    class_weights = dict(enumerate(class_weights))

    # Step 2: Create Sequence-based datasets
    batch_size = 4
    train_seq = HDF5Sequence(input_path, train_indices, integer_labels, batch_size)
    val_seq = HDF5Sequence(input_path, val_indices, integer_labels, batch_size)

    base_model = tf.keras.applications.EfficientNetV2B0(
        include_top=False,  # Exclude the classification head
        weights="imagenet",  # Use pre-trained weights
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False 

    # Step 3: Define the CNN model
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(16, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(len(unique_labels), activation="softmax")
    ])

    # Step 4: Compile the model
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    # Callbacks
    callbacks = [
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
    ]

    # Step 5: Train the model
    print("Training the model...")
    model.fit(train_seq, validation_data=val_seq, epochs=10, class_weight=class_weights, callbacks=callbacks)

    # Step 6: Save the model
    model.save("/opt/airflow/storage/efficientnet.h5")
    print("Model saved successfully!")

if __name__ == "__main__":
    run_predict()
