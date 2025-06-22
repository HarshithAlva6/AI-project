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
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from PIL import Image
import io

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

    # Load pre-trained InceptionV3 model
    global inception_model
    inception_model = InceptionV3(weights='imagenet')
    
    # Optional: Load your custom trained model if you have one
    # You can still keep your custom model for Indian food specific recognition
    global custom_model, food_labels
    custom_model = None
    food_labels = None
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "airflow", "efficientnet.h5")
        model_path = os.path.abspath(model_path)
        
        txt_file_path = os.path.join(current_dir, "..", "airflow/dag/Indian Food Images", "List of Indian Foods.txt")
        txt_file_path = os.path.abspath(txt_file_path)
        
        if os.path.exists(model_path) and os.path.exists(txt_file_path):
            custom_model = tf.keras.models.load_model(model_path)
            food_labels = pd.read_csv(txt_file_path, header=None, names=["label"])
            print("Custom Indian food model loaded successfully")
        else:
            print("Custom model or labels not found, using only InceptionV3")
    except Exception as e:
        print(f"Error loading custom model: {e}")

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

    def preprocess_image_for_inception(img_path):
        """Preprocess image for InceptionV3"""
        img = image.load_img(img_path, target_size=(299, 299))  # InceptionV3 expects 299x299
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        return img_array

    def preprocess_image_for_custom(img_path):
        """Preprocess image for custom model"""
        img = Image.open(img_path).resize((224, 224))  # Your custom model expects 224x224
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    def get_food_predictions(predictions, model_type="inception"):
        """Extract food-related predictions"""
        if model_type == "inception":
            decoded_predictions = decode_predictions(predictions, top=10)[0]
            
            # Filter for food-related items (you can expand this list)
            food_keywords = [
                'pizza', 'burger', 'sandwich', 'salad', 'soup', 'pasta', 'noodles',
                'rice', 'bread', 'cake', 'cookie', 'pie', 'fruit', 'vegetable',
                'meat', 'chicken', 'fish', 'cheese', 'egg', 'milk', 'coffee',
                'tea', 'wine', 'beer', 'chocolate', 'ice_cream', 'pancake',
                'waffle', 'bagel', 'donut', 'pretzel', 'hot_dog', 'taco',
                'burrito', 'curry', 'stew', 'gravy', 'sauce', 'dip'
            ]
            
            food_predictions = []
            for _, label, confidence in decoded_predictions:
                label_lower = label.lower()
                if any(keyword in label_lower for keyword in food_keywords):
                    food_predictions.append({
                        "label": label.replace('_', ' ').title(),
                        "confidence": float(confidence)
                    })
            
            return food_predictions[:3]  # Return top 3 food predictions
        
        elif model_type == "custom":
            top_indices = np.argsort(predictions[0])[-3:][::-1]
            top_predictions = []
            for i in top_indices:
                if i < len(food_labels):
                    label = food_labels.iloc[i]["label"]
                    confidence = float(predictions[0][i])
                    top_predictions.append({
                        "label": label.replace('_', ' ').title(),
                        "confidence": confidence
                    })
            return top_predictions

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

        try:
            # Get predictions from InceptionV3 (general food recognition)
            inception_img = preprocess_image_for_inception(filepath)
            inception_predictions = inception_model.predict(inception_img)
            inception_food_predictions = get_food_predictions(inception_predictions, "inception")
            
            result = {
                "inception_v3_predictions": inception_food_predictions,
                "custom_model_predictions": []
            }
            
            # If custom model is available, also get predictions from it
            if custom_model is not None and food_labels is not None:
                custom_img = preprocess_image_for_custom(filepath)
                custom_predictions = custom_model.predict(custom_img)
                custom_food_predictions = get_food_predictions(custom_predictions, "custom")
                result["custom_model_predictions"] = custom_food_predictions
            
            # Combine and rank predictions
            all_predictions = inception_food_predictions + result["custom_model_predictions"]
            all_predictions.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'top_predictions': all_predictions[:3],
                'detailed_results': result
            }), 200

        except Exception as e:
            # Clean up uploaded file on error
            if os.path.exists(filepath):
                os.remove(filepath)
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