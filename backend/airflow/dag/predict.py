import tensorflow as tf
import h5py
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report

class HDF5Sequence(tf.keras.utils.Sequence):
    def __init__(self, file_path, indices, labels, batch_size, augment):
        self.h5f = h5py.File(file_path, "r")
        self.indices = indices
        self.labels = labels
        self.batch_size = batch_size
        self.augment = augment

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, idx):
        images = self.h5f["images"]
        batch_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_images = np.array([images[i] for i in batch_indices], dtype=np.float32)
        batch_images = tf.keras.applications.efficientnet.preprocess_input(batch_images)
        batch_labels = np.array([self.labels[i] for i in batch_indices], dtype=np.int32)

        if self.augment:
            batch_images = self.apply_augmentation(batch_images)

        return batch_images, batch_labels

    def apply_augmentation(self, images):
        return np.array([tf.image.random_flip_left_right(img) for img in images], dtype=np.float32)

    def on_epoch_end(self):
        np.random.shuffle(self.indices)

    def __del__(self):
        self.h5f.close()

def run_predict():
    input_path = "/opt/airflow/storage/fin_data.h5"
    with h5py.File(input_path, "r") as h5f:
        label_map = eval(h5f.attrs["label_map"])
        reverse_label_map = {v: k for k, v in label_map.items()}
        total_samples = h5f["images"].shape[0]
        labels = np.array(h5f["labels"][:])
        unique_labels, integer_labels = np.unique(labels, return_inverse=True)
        indices = np.arange(total_samples)
        np.random.shuffle(indices)
        train_indices = indices[:int(0.8 * total_samples)]
        val_indices = indices[int(0.8 * total_samples):]

    batch_size = 4
    train_seq = HDF5Sequence(input_path, train_indices, integer_labels, batch_size, augment=True)
    val_seq = HDF5Sequence(input_path, val_indices, integer_labels, batch_size, augment=False)

    base_model = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False  # Initially freeze all layers

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(len(unique_labels), activation="softmax"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    # Compute class weights
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(integer_labels),
        y=integer_labels
    )
    class_weights = {i: weight for i, weight in enumerate(class_weights)}

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6)
    ]

    # Initial Training
    history = model.fit(
        train_seq,
        validation_data=val_seq,
        epochs=10,
        callbacks=callbacks,
        class_weight=class_weights
    )

    # Fine-Tuning
    base_model.trainable = True
    for layer in base_model.layers[:-10]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    fine_tune_history = model.fit(
        train_seq,
        validation_data=val_seq,
        epochs=10,
        callbacks=callbacks,
        class_weight=class_weights
    )

    # Save the Model
    model.save("/opt/airflow/storage/efficientnet.h5")
    print("Model saved successfully!")

    # Evaluation
    true_labels = np.array([integer_labels[i] for i in val_indices])
    predictions = np.argmax(model.predict(val_seq), axis=-1)

    print(classification_report(true_labels, predictions, target_names=[reverse_label_map[l] for l in unique_labels]))

if __name__ == "__main__":
    run_predict()
