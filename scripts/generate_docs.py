from pathlib import Path
import inspect
import importlib.util
import sys
from datetime import datetime
import json

class DocumentationGenerator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / 'docs'
        self.docs_dir.mkdir(exist_ok=True)

    def generate_project_structure(self) -> str:
        """Generate documentation of project structure"""
        structure = [
            "# Project Structure",
            "\nProject organization and key components:\n",
            "```",
            "project_root/",
            "+-- src/                    # Source code",
            "|   +-- document_analyzer.py # Main document analysis logic",
            "|   +-- utils/              # Utility functions",
            "|   +-- models/             # Model configurations",
            "+-- tests/                  # Test suite",
            "|   +-- data/              # Test data",
            "|   +-- reports/           # Test reports",
            "+-- scripts/               # Utility scripts",
            "+-- data/                  # Data directory",
            "|   +-- raw/              # Original documents",
            "|   +-- processed/        # Processed data",
            "+-- output/                # Output files",
            "|   +-- reports/          # Analysis reports",
            "|   +-- logs/             # Application logs",
            "+-- docs/                  # Documentation",
            "+-- notebooks/            # Jupyter notebooks",
            "```\n"
        ]
        return "\n".join(structure)

    def generate_setup_guide(self) -> str:
        """Generate setup and deployment documentation"""
        setup_guide = [
            "# Setup and Deployment Guide",
            "\n## Prerequisites",
            "- Python 3.9+",
            "- OpenAI API key",
            "- Anthropic API key",
            "\n## Installation",
            "1. Clone the repository",
            "2. Create and activate virtual environment:",
            "```bash",
            "python -m venv venv",
            "source venv/bin/activate  # Linux/Mac",
            "venv\\Scripts\\activate    # Windows",
            "```",
            "3. Install dependencies:",
            "```bash",
            "pip install -r requirements.txt",
            "```",
            "4. Create .env file with required API keys",
            "\n## Configuration",
            "Key environment variables:",
            "```ini",
            "OPENAI_API_KEY=your_key_here",
            "ANTHROPIC_API_KEY=your_key_here",
            "OPENAI_MODEL_NAME=gpt-4-1106-preview",
            "ANTHROPIC_MODEL_NAME=claude-2.1",
            "CHUNK_SIZE=1000",
            "CHUNK_OVERLAP=100",
            "MAX_CHUNKS=20",
            "```"
        ]
        return "\n".join(setup_guide)

    def generate_usage_guide(self) -> str:
        """Generate usage documentation"""
        usage_guide = [
            "# Usage Guide",
            "\n## Document Analysis",
            "### Basic Usage",
            "```bash",
            "python src/document_analyzer.py",
            "```",
            "\n### Key Scripts",
            "\n#### 1. Document Analysis",
            "- **Purpose**: Analyze PDF documents using AI models",
            "- **Usage**: Place PDF in data/raw/ and run document_analyzer.py",
            "- **Output**: Generates analysis reports in output/reports/",
            "\n#### 2. Environment Setup",
            "- **Script**: scripts/setup_environment.py",
            "- **Purpose**: Verify and setup required environment",
            "- **Usage**: Run before first use or after configuration changes",
            "\n#### 3. Testing",
            "- **Script**: scripts/run_tests.py",
            "- **Purpose**: Run test suite",
            "- **Usage**: Run regularly to verify system integrity",
            "\n### Common Use Cases",
            "1. **New Document Analysis**",
            "   - Place PDF in data/raw/",
            "   - Run document_analyzer.py",
            "   - Review reports in output/reports/",
            "\n2. **System Updates**",
            "   - Update dependencies",
            "   - Run setup_environment.py",
            "   - Run test suite",
            "\n3. **Troubleshooting**",
            "   - Check logs in output/logs/",
            "   - Verify API keys in .env",
            "   - Run setup_environment.py"
        ]
        return "\n".join(usage_guide)

    def generate_testing_guide(self) -> str:
        """Generate testing documentation"""
        testing_guide = [
            "# Testing Guide",
            "\n## Test Suite Organization",
            "```",
            "tests/",
            "├── test_document_analyzer.py  # Core functionality tests",
            "├── test_models.py            # Model integration tests",
            "├── test_utils.py             # Utility function tests",
            "└── data/                     # Test data",
            "```",
            "\n## Running Tests",
            "### Full Test Suite",
            "```bash",
            "python scripts/run_tests.py",
            "```",
            "\n### Individual Test Files",
            "```bash",
            "pytest tests/test_document_analyzer.py",
            "```",
            "\n## Test Categories",
            "1. **Unit Tests**",
            "   - Individual component testing",
            "   - Fast execution",
            "   - No external dependencies",
            "\n2. **Integration Tests**",
            "   - Model interaction testing",
            "   - API integration verification",
            "   - Requires API keys",
            "\n3. **System Tests**",
            "   - End-to-end workflow testing",
            "   - Full document processing",
            "   - Performance benchmarking",
            "\n## Adding New Tests",
            "1. Create test file in tests/",
            "2. Follow test naming convention: test_*.py",
            "3. Add test data if required",
            "4. Update test documentation"
        ]
        return "\n".join(testing_guide)

    def generate_all_documentation(self):
        """Generate all documentation files"""
        try:
            # Create documentation files
            docs = {
                'project_structure.md': self.generate_project_structure(),
                'setup_guide.md': self.generate_setup_guide(),
                'usage_guide.md': self.generate_usage_guide(),
                'testing_guide.md': self.generate_testing_guide()
            }

            # Write documentation files with UTF-8 encoding
            for filename, content in docs.items():
                with open(self.docs_dir / filename, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Generate index file
            index_content = [
                "# Documentation Index",
                "\n## Available Documentation",
                "1. [Project Structure](project_structure.md)",
                "2. [Setup Guide](setup_guide.md)",
                "3. [Usage Guide](usage_guide.md)",
                "4. [Testing Guide](testing_guide.md)",
                f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]

            with open(self.docs_dir / 'index.md', 'w', encoding='utf-8') as f:
                f.write('\n'.join(index_content))

            print("Documentation generated successfully!")
            print(f"Documentation available in: {self.docs_dir}")

        except Exception as e:
            print(f"Error generating documentation: {str(e)}")
            raise

def main():
    project_root = Path(__file__).parent.parent
    doc_gen = DocumentationGenerator(project_root)
    doc_gen.generate_all_documentation()

if __name__ == "__main__":
    main() 