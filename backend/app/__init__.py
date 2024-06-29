from flask import Flask, jsonify
from flask_graphql import GraphQLView
from .schemas.schema import schema
from .config import Config
from .db import db, migrate
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

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
        
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    )

    return app
