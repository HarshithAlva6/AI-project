from dotenv import load_dotenv
from app import create_app, db
import os
import sys

load_dotenv('.env')
app = create_app()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os

def delete_pycache(base_dir="."):
    for root, dirs, _ in os.walk(base_dir):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                full_path = os.path.join(root, dir_name)
                print(f"Deleting: {full_path}")
                os.system(f"rm -rf {full_path}" if os.name != "nt" else f"rmdir /s /q {full_path}")

delete_pycache()

if __name__ == '__main__':
    app.run(debug=True)
