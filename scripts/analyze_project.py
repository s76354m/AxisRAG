from pathlib import Path
import json
import shutil

def analyze_project_structure(root_dir: Path):
    """Analyze current project structure"""
    structure = {
        'directories': [],
        'files': [],
        'file_types': {}
    }
    
    # Ignore directories
    ignore_dirs = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv'}
    
    for item in root_dir.rglob('*'):
        if any(ignored in item.parts for ignored in ignore_dirs):
            continue
            
        rel_path = item.relative_to(root_dir)
        
        if item.is_dir():
            structure['directories'].append(str(rel_path))
        else:
            structure['files'].append(str(rel_path))
            ext = item.suffix
            if ext:
                structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1

    return structure

def reorganize_project(root_dir: Path, structure: dict):
    """Create new project structure and move files"""
    # Create new directory structure
    new_dirs = [
        'src',
        'src/utils',
        'tests',
        'tests/data/test_documents',
        'notebooks/examples',
        'app',
        'app/components',
        'scripts'
    ]
    
    # Create directories
    for dir_path in new_dirs:
        (root_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    init_locations = ['src', 'src/utils', 'tests', 'app', 'app/components']
    for loc in init_locations:
        (root_dir / loc / '__init__.py').touch()
    
    # Move/create core files
    file_moves = {
        # Source files
        'rag_core.py': ('src/rag_core.py', '.py'),
        'report_generator.py': ('src/report_generator.py', '.py'),
        'memory_manager.py': ('src/memory_manager.py', '.py'),
        
        # Utility files
        'logging_utils.py': ('src/utils/logging_utils.py', '.py'),
        'file_utils.py': ('src/utils/file_utils.py', '.py'),
        
        # App files
        'app.py': ('app/main.py', '.py'),
        'dashboard.py': ('app/components/dashboard.py', '.py'),
        
        # Test files
        'test_rag_core.py': ('tests/test_rag_core.py', '.py'),
        'test_report_quality.py': ('tests/test_report_quality.py', '.py'),
        'test_memory.py': ('tests/test_memory.py', '.py'),
        
        # Script files
        'run_tests.py': ('scripts/run_tests.py', '.py'),
        'setup_env.py': ('scripts/setup_env.py', '.py')
    }
    
    return {
        'current_structure': structure,
        'new_structure': {
            'directories': new_dirs,
            'file_moves': file_moves
        }
    }

def main():
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Analyze current structure
    current_structure = analyze_project_structure(project_root)
    
    # Save current structure analysis
    with open(project_root / 'project_analysis.json', 'w') as f:
        json.dump(current_structure, f, indent=2)
    
    print("Current Project Structure:")
    print("\nDirectories:")
    for dir_path in current_structure['directories']:
        print(f"  {dir_path}")
    
    print("\nFiles by Type:")
    for ext, count in current_structure['file_types'].items():
        print(f"  {ext}: {count} files")
    
    # Get reorganization plan
    reorg_plan = reorganize_project(project_root, current_structure)
    
    # Save reorganization plan
    with open(project_root / 'reorganization_plan.json', 'w') as f:
        json.dump(reorg_plan, f, indent=2)
    
    print("\nReorganization Plan Generated: reorganization_plan.json")

if __name__ == "__main__":
    main() 