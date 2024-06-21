from flask import Flask
from flask_graphql import GraphQLView
from .schemas.schema import schema
from .config import Config
from .db import db, migrate


def create_app():
    app = Flask(__name__)
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

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    )

    return app
