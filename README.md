WORK IN PROGRESS!!!

npm init -y

npm install express graphql graphql-http sequelize pg pg-hstore
npm install --save-dev nodemon

python -m venv envname
source envname/Scripts/activate
rm -rf envname

pip install Flask SQLAlchemy graphene graphene-sqlalchemy psycopg2 //flask-graphql

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


Step-by-step Approach -
1. Extract raw data(Indian food Dataset) from Kaggle
2. pip install kaggle (using Kaggle CLI)
3. kaggle datasets download -d iamsouravbanerjee/indian-food-images-dataset
4. unzip indian-food-images-dataset.zip -d frontend
5. Do ETL on the images, where image folder and metadata(.txt) are under the unzipped folder.
 - pip install pillow, pip install pandas
6. TRANSFORM - Resize the image and bring it down to [0,1] by dividing np.array(img) / 255
7. In another file, do the prediction model using EfficientNet-Lite
 - pip install tensorflow tensorflow-hub scikit-learn
8. Once .h5 file is retrieved(Prediction model), we can run the test against the model in the API (__init__)
9. pip freeze > requirements.txt and pip install -r requirements.txt
10. pip install apache-airflow
11. docker ps
    docker exec -it docker-name bash
    docker exec -it docker-name-postgreSQL psql -U sql-name
12. pip install git-filter-repo


For etl.py, had to send data in chunks, and store it in uint8 under array to ensure minimal space taken in Airflow container.

-> Download and unzip Images dataset from https://www.kaggle.com/datasets/iamsouravbanerjee/indian-food-images-dataset
at AI-project/backend/airflow/dag directory