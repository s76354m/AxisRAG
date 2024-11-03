from pathlib import Path
import json
import shutil
import sys
from datetime import datetime
import os

def get_unique_backup_dir(project_root: Path) -> Path:
    """Create a unique backup directory name"""
    base_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir = project_root / base_name
    
    # If directory exists, append a number
    counter = 1
    while backup_dir.exists():
        backup_dir = project_root / f"{base_name}_{counter}"
        counter += 1
    
    return backup_dir

def backup_project(project_root: Path) -> Path:
    """Create a backup of the project"""
    backup_dir = project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree(project_root, backup_dir, ignore=shutil.ignore_patterns(
        '.git', '__pycache__', '.pytest_cache', 'backup_*'
    ))
    return backup_dir

def execute_reorganization(project_root: Path):
    """Execute project reorganization based on current structure"""
    try:
        # Create backup
        backup_dir = backup_project(project_root)
        print(f"Backup created at: {backup_dir}")
        
        # Define new structure
        new_structure = {
            'directories': [
                'src',
                'src/utils',
                'src/models',
                'tests',
                'tests/data',
                'tests/reports',
                'app',
                'app/components',
                'scripts',
                'data',
                'data/raw',
                'data/processed',
                'notebooks/examples',
                'output',
                'output/reports',
                'output/logs',
                'db'
            ]
        }
        
        # Create new directories
        for dir_path in new_structure['directories']:
            (project_root / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Move files based on type and location
        file_moves = {
            # Move Python files
            'notebooks/*.py': 'src/',
            'notebooks/tests/*.py': 'tests/',
            
            # Move data files
            'notebooks/data/*.pdf': 'data/raw/',
            'notebooks/data/*.txt': 'data/raw/',
            
            # Move output files
            'notebooks/output/*.txt': 'output/reports/',
            'notebooks/tests/reports/*': 'tests/reports/',
            
            # Move database files
            'chroma_db/*': 'db/chroma_db/',
            
            # Move notebooks
            'notebooks/*.ipynb': 'notebooks/examples/',
            
            # Move batch files to scripts
            '*.bat': 'scripts/',
            
            # Move logs
            '*.log': 'output/logs/'
        }
        
        # Process file moves
        for pattern, dest in file_moves.items():
            source_pattern = project_root / Path(pattern)
            for source_file in project_root.glob(pattern):
                if source_file.is_file():
                    dest_path = project_root / dest / source_file.name
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_path)
                    print(f"Moved: {source_file.relative_to(project_root)} -> {dest_path.relative_to(project_root)}")
        
        # Create necessary __init__.py files
        init_locations = ['src', 'src/utils', 'src/models', 'tests', 'app', 'app/components']
        for loc in init_locations:
            (project_root / loc / '__init__.py').touch()
        
        # Update requirements.txt
        requirements_path = project_root / 'requirements.txt'
        with open(requirements_path, 'w') as f:
            f.write("""streamlit==1.29.0
pandas==2.1.3
openai==1.3.0
anthropic==0.7.0
chromadb==0.4.17
langchain==0.0.335
pytest==7.4.3
tqdm==4.66.1
python-dotenv==1.0.0
""")
        
        # Create .env template
        env_template_path = project_root / '.env.template'
        with open(env_template_path, 'w') as f:
            f.write("""# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database Configuration
CHROMA_DB_PATH=db/chroma_db

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
""")
        
        print("\nReorganization completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during reorganization: {str(e)}")
        return False

def cleanup_old_files(project_root: Path, backup_dir: Path) -> bool:
    """Clean up old files and directories after successful reorganization"""
    try:
        # Directories to clean up
        cleanup_dirs = [
            'notebooks/output',
            'notebooks/tests',
            'notebooks/data',
            'chroma_db',
            'notebooks/Archive'
        ]
        
        # Files to clean up (only if they exist in new location)
        cleanup_files = [
            '*.bat',
            '*.log',
            'notebooks/*.py'
        ]
        
        # Clean up directories
        for dir_path in cleanup_dirs:
            dir_to_remove = project_root / dir_path
            if dir_to_remove.exists():
                try:
                    shutil.rmtree(dir_to_remove)
                    print(f"Removed directory: {dir_path}")
                except Exception as e:
                    print(f"Warning: Could not remove directory {dir_path}: {str(e)}")
        
        # Clean up files
        for pattern in cleanup_files:
            for file_path in project_root.glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        print(f"Removed file: {file_path.relative_to(project_root)}")
                    except Exception as e:
                        print(f"Warning: Could not remove file {file_path}: {str(e)}")
        
        # Remove empty directories in notebooks
        notebooks_dir = project_root / 'notebooks'
        if notebooks_dir.exists():
            for dir_path in notebooks_dir.glob('**/*'):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    try:
                        dir_path.rmdir()
                        print(f"Removed empty directory: {dir_path.relative_to(project_root)}")
                    except Exception as e:
                        print(f"Warning: Could not remove empty directory {dir_path}: {str(e)}")
        
        print("\nCleanup completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        return False

def main():
    project_root = Path(__file__).parent.parent
    
    print("Starting project reorganization...")
    
    try:
        print("\nStep 1: Creating backup...")
        backup_dir = backup_project(project_root)
        
        print("\nStep 2: Reorganizing project structure...")
        if execute_reorganization(project_root):
            print("\nStep 3: Cleaning up old files...")
            if cleanup_old_files(project_root, backup_dir):
                print("\nReorganization completed successfully!")
                print("\nNext steps:")
                print("1. Review the new structure")
                print("2. Update import statements in moved files")
                print("3. Run tests to verify functionality")
                print("4. Delete backup if everything works correctly")
                print("\nBackup location:", backup_dir)
            else:
                print("\nCleanup failed! Old files remain but new structure is in place.")
        else:
            print("\nReorganization failed! Restore from backup at:", backup_dir)
            
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        print("Please check the backup directory and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 