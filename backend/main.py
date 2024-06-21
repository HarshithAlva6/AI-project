from dotenv import load_dotenv
from app import create_app, db
import os
import sys

load_dotenv()
app = create_app()

# Add the parent directory of 'app' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    app.run(debug=True)
