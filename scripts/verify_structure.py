from pathlib import Path
import ast
import sys
from typing import Dict, List, Set
import logging

class ProjectVerifier:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('verification.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def verify_structure(self) -> bool:
        """Verify the project structure and create missing directories"""
        required_dirs = [
            'src',
            'src/utils',
            'src/models',
            'tests',
            'tests/data',
            'tests/reports',
            'app',
            'app/components',
            'scripts',
            'data/raw',
            'data/processed',
            'notebooks/examples',
            'output/reports',
            'output/logs',
            'db/chroma_db'
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            dir_full_path = self.project_root / dir_path
            if not dir_full_path.exists():
                try:
                    dir_full_path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created directory: {dir_path}")
                except Exception as e:
                    missing_dirs.append(dir_path)
                    self.logger.error(f"Failed to create directory {dir_path}: {str(e)}")
        
        if missing_dirs:
            self.logger.error(f"Could not create directories: {missing_dirs}")
            return False
            
        self.logger.info("Directory structure verification and creation completed")
        return True

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project, excluding backup and cache directories"""
        exclude_patterns = {
            'backup_',
            '__pycache__',
            '.pytest_cache',
            '.venv',
            'venv',
            '.git'
        }
        
        python_files = []
        for file_path in self.project_root.glob('**/*.py'):
            # Check if file path contains any excluded patterns
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                python_files.append(file_path)
        
        # Log found files by directory
        files_by_dir = {}
        for file_path in python_files:
            dir_name = file_path.parent.relative_to(self.project_root)
            if dir_name not in files_by_dir:
                files_by_dir[dir_name] = []
            files_by_dir[dir_name].append(file_path.name)
        
        # Log breakdown
        self.logger.info("\nPython files by directory:")
        for dir_name, files in files_by_dir.items():
            self.logger.info(f"{dir_name}: {len(files)} files")
            for file_name in files:
                self.logger.info(f"  - {file_name}")
        
        return python_files

    def analyze_imports(self, file_path: Path) -> Dict[str, Set[str]]:
        """Analyze imports in a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            imports = {
                'import': set(),
                'from': set()
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports['import'].add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports['from'].add(node.module)
            
            return imports
            
        except Exception as e:
            self.logger.error(f"Error analyzing imports in {file_path}: {str(e)}")
            return {'import': set(), 'from': set()}

    def update_imports(self, file_path: Path) -> bool:
        """Update imports in a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update relative imports
            updates = {
                'src.': 'src.',
                'from src import': 'from src import',
                'from src.': 'from src.',
                'import src.': 'import src.'
            }
            
            new_content = content
            for old, new in updates.items():
                new_content = new_content.replace(old, new)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.logger.info(f"Updated imports in {file_path}")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating imports in {file_path}: {str(e)}")
            return False

    def verify_contents(self) -> bool:
        """Verify contents of key directories"""
        try:
            # Check source files
            src_files = list((self.project_root / 'src').glob('*.py'))
            if not src_files:
                self.logger.warning("No Python files found in src directory")
            else:
                self.logger.info(f"Found {len(src_files)} Python files in src directory")

            # Check test files
            test_files = list((self.project_root / 'tests').glob('test_*.py'))
            if not test_files:
                self.logger.warning("No test files found in tests directory")
            else:
                self.logger.info(f"Found {len(test_files)} test files")

            # Check data files
            data_files = list((self.project_root / 'data/raw').glob('*.pdf'))
            if not data_files:
                self.logger.warning("No PDF files found in data/raw directory")
            else:
                self.logger.info(f"Found {len(data_files)} PDF files in data/raw")

            # Check reports
            report_files = list((self.project_root / 'output/reports').glob('*.txt'))
            if not report_files:
                self.logger.warning("No report files found in output/reports directory")
            else:
                self.logger.info(f"Found {len(report_files)} report files")

            return True

        except Exception as e:
            self.logger.error(f"Error verifying contents: {str(e)}")
            return False

    def verify_imports(self, file_path: Path) -> bool:
        """Verify imports in a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for problematic imports
            problematic_patterns = [
                'notebooks.',
                'from notebooks',
                'import notebooks',
                '../',
                '..'
            ]
            
            issues = []
            for line_num, line in enumerate(content.split('\n'), 1):
                if line.strip().startswith(('import', 'from')):
                    for pattern in problematic_patterns:
                        if pattern in line:
                            issues.append(f"Line {line_num}: {line.strip()}")
            
            if issues:
                self.logger.warning(f"\nPotential import issues in {file_path}:")
                for issue in issues:
                    self.logger.warning(f"  {issue}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying imports in {file_path}: {str(e)}")
            return False

    def verify_and_fix(self):
        """Verify project structure and fix imports"""
        try:
            print("\nVerifying project structure...")
            if not self.verify_structure():
                print("Project structure verification failed!")
                return False
            
            print("\nVerifying directory contents...")
            self.verify_contents()
            
            print("\nAnalyzing Python files...")
            python_files = self.find_python_files()
            print(f"Found {len(python_files)} Python files")
            
            print("\nVerifying imports...")
            files_with_issues = []
            for file_path in python_files:
                if not self.verify_imports(file_path):
                    files_with_issues.append(file_path)
            
            if files_with_issues:
                print("\nFiles with import issues:")
                for file_path in files_with_issues:
                    print(f"  - {file_path.relative_to(self.project_root)}")
            
            print("\nUpdating imports...")
            updated_files = []
            for file_path in python_files:
                if self.update_imports(file_path):
                    updated_files.append(file_path)
            
            if updated_files:
                print("\nUpdated imports in the following files:")
                for file_path in updated_files:
                    print(f"  - {file_path.relative_to(self.project_root)}")
            else:
                print("\nNo import updates needed")
            
            # Verify imports again after updates
            if files_with_issues:
                print("\nRe-checking files with import issues...")
                still_have_issues = []
                for file_path in files_with_issues:
                    if not self.verify_imports(file_path):
                        still_have_issues.append(file_path)
                
                if still_have_issues:
                    print("\nFiles still having import issues:")
                    for file_path in still_have_issues:
                        print(f"  - {file_path.relative_to(self.project_root)}")
            
            print("\nVerification and updates completed successfully!")
            return True
            
        except Exception as e:
            print(f"\nError during verification: {str(e)}")
            return False

def main():
    project_root = Path(__file__).parent.parent
    verifier = ProjectVerifier(project_root)
    
    if verifier.verify_and_fix():
        print("\nNext steps:")
        print("1. Run tests to verify functionality")
        print("2. Check updated import statements")
        print("3. Review verification.log for details")
    else:
        print("\nVerification failed! Please check verification.log for details")
        sys.exit(1)

if __name__ == "__main__":
    main() 