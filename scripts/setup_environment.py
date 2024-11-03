import os
from pathlib import Path
from dotenv import load_dotenv
import sys

def verify_environment():
    """Verify environment setup"""
    print("Verifying environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Default model configurations
    default_env = {
        'OPENAI_API_KEY': '',
        'ANTHROPIC_API_KEY': '',
        'OPENAI_MODEL_NAME': 'gpt-4-1106-preview',
        'ANTHROPIC_MODEL_NAME': 'claude-3-sonnet-20240229',
        'CHUNK_SIZE': '2000',
        'CHUNK_OVERLAP': '200',
        'TEMPERATURE': '0'
    }
    
    # Check for missing environment variables and create .env if needed
    env_file = Path('.env')
    if not env_file.exists():
        print("\nCreating .env file with template...")
        with open(env_file, 'w') as f:
            for key, value in default_env.items():
                f.write(f"{key}={value}\n")
        print("Please edit .env file with your API keys")
        return False
    
    # Check API keys
    missing_keys = []
    for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("\nError: Missing required API keys:")
        for key in missing_keys:
            print(f"- {key}")
        print("\nPlease add these keys to your .env file")
        return False
    
    # Verify directory structure
    required_dirs = [
        'output/logs',
        'output/reports',
        'data/raw',
        'db/chroma_db'
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            print(f"\nCreating directory: {dir_path}")
            path.mkdir(parents=True, exist_ok=True)
    
    print("\nEnvironment setup verified successfully!")
    return True

if __name__ == "__main__":
    if not verify_environment():
        sys.exit(1) 