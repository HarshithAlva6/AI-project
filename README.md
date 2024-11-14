WORK IN PROGRESS!!!

npm init -y

npm install express graphql graphql-http sequelize pg pg-hstore
npm install --save-dev nodemon

python -m venv envname
source envname/Scripts/activate
rm -rf envname

pip install Flask SQLAlchemy graphene graphene-sqlalchemy psycopg2 flask-graphql

python.exe -m pip install --upgrade pip

The main.py file serves as the entry point for your Flask application. It initializes the Flask app, sets up the database, and starts the application server. 
The config.py file is used to store configuration settings for your Flask application. This typically includes settings for the database connection, secret keys, and other configuration options.

pip install python-dotenv (for .env file)

generate_Secret_key.py file is used to generate the key and send it to .env file

You can use Flask-Migrate to handle database migrations.
pip install Flask-Migrate

flask db init
flask db migrate -m "Initial migration"
flask db upgrade


Opt -
 pip install --upgrade
 pip uninstall


 mutation {
  createRecipe(title: "Spaghetti Bolognese", description: "Salty", ingredients: "Spaghetti, Tomato Sauce, Ground Beef, Garlic, Onion, Olive Oil, Salt, Pepper", instructions: "1. Cook the spaghetti. 2. Prepare the sauce. 3. Mix and serve.") {
    recipe {
      id
      title
      description
      ingredients
      instructions
    }
  }
}


FRONTEND -
npx create-react-app frontend
pip install flask-cors
