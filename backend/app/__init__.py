from flask import Flask, jsonify, request
from flask_graphql import GraphQLView
from .schemas.schema import schema
from .config import Config
from .db import db, migrate
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')  # Use absolute path
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

    # Ensure the upload folder exists
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
            # Here you would add your recognition logic
            recognized_food = 'Example food item'  # This should be replaced with your recognition result
            return jsonify({'result': recognized_food})

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    )

    return app
