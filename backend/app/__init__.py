from flask import Flask, jsonify, request
from .schemas.schema import schema
from .config import Config
from .db import db, migrate
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads') 
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models here to ensure they are registered
        from .models import user, recipe, food_item
        db.create_all()

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    @app.route('/api/data')
    def get_data():
        data = {
            'message': 'Hello from Flask!',
            'items': ['Item 1', 'Item 2', 'Item 3']
        }
        return jsonify(data)

    @app.route('/recognize', methods=['POST'])
    def recognize():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"File saved at: {filepath}")
            if os.path.exists(filepath):
                print(f"File exists at {filepath}")
            else:
                print(f"File not found at {filepath}")

        try:
            # Preprocess the image using Pillow
            img = Image.open(filepath).resize((224, 224))  # Resize to match model input size
            img_array = np.array(img) / 255.0
            print(f"Input array shape 1: {img_array.shape}")
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
            print(f"Input array shape 2: {img_array.shape}")
            print(f"Input array sample values: {img_array[0][:5, :5, 0]}")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            txt_file_path = os.path.join(current_dir, "..", "airflow/dag/Indian Food Images", "List of Indian Foods.txt")
            absolute_path = os.path.abspath(txt_file_path)
            print(f"Resolved Path to .txt File: {absolute_path}")
            meta_file = os.path.abspath(txt_file_path)
            #txt_file_path = "/opt/airflow/dags/dag/Indian Food Images/List of Indian Foods.txt"
            if os.path.exists(meta_file):
                labels = pd.read_csv(meta_file, header=None, names=["label"])
                print(labels.head())
            else:
               print("Metadata file not found.")
            # Make prediction
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "..", "airflow", "efficientnet.h5")
            model_path = os.path.abspath(model_path)
            #model_path = "/opt/airflow/storage/efficientnet.h5"
            model = tf.keras.models.load_model(model_path)
            print("HERE",model.summary())
            predictions = model.predict(img_array)
            print(f"Raw predictions: {predictions}")
            print(f"Sum of probabilities: {np.sum(predictions)}")
            print(f"Number of output classes: {predictions.shape[1]}")
            print(f"Number of labels: {len(labels)}")
            top_indices = np.argsort(predictions[0])[-3:][::-1]  # Top-3 indices
            print(f"Top indices: {top_indices}")

            # Ensure labels are correctly matched to the indices
            top_predictions = []
            for i in top_indices:
                label = labels.iloc[i]["label"] if i < len(labels) else f"Unknown ({i})"
                confidence = float(predictions[0][i])
                top_predictions.append({"label": label, "confidence": confidence})

            print(f"Top Predictions: {top_predictions}")
            return jsonify({'top_predictions': top_predictions}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/graphql', methods=['POST'])
    def graphql():
        data = request.get_json()
        success, result = schema.execute(
            data.get("query"),
            variables=data.get("variables"),
            context_value=request,
        )
        status_code = 200 if success else 400
        return jsonify(result), status_code

    return app
