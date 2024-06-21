import secrets
from pathlib import Path

def generate_secret_key():
    return secrets.token_hex(32)

def update_env_file(secret_key, env_file='.env'):
    env_path = Path(env_file)
    
    # Read the existing .env file
    if env_path.exists():
        with env_path.open('r') as file:
            lines = file.readlines()
    else:
        lines = []

    # Check if SECRET_KEY is already present
    for i, line in enumerate(lines):
        if line.startswith('SECRET_KEY='):
            lines[i] = f'SECRET_KEY={secret_key}\n'
            break
    else:
        # If SECRET_KEY is not present, add it
        lines.append(f'SECRET_KEY={secret_key}\n')
    
    # Write the updated lines back to the .env file
    with env_path.open('w') as file:
        file.writelines(lines)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    update_env_file(secret_key)
    print(f"SECRET_KEY has been updated in the .env file: {secret_key}")
