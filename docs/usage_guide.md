# Usage Guide

## Document Analysis
### Basic Usage
```bash
python src/document_analyzer.py
```

### Key Scripts

#### 1. Document Analysis
- **Purpose**: Analyze PDF documents using AI models
- **Usage**: Place PDF in data/raw/ and run document_analyzer.py
- **Output**: Generates analysis reports in output/reports/

#### 2. Environment Setup
- **Script**: scripts/setup_environment.py
- **Purpose**: Verify and setup required environment
- **Usage**: Run before first use or after configuration changes

#### 3. Testing
- **Script**: scripts/run_tests.py
- **Purpose**: Run test suite
- **Usage**: Run regularly to verify system integrity

### Common Use Cases
1. **New Document Analysis**
   - Place PDF in data/raw/
   - Run document_analyzer.py
   - Review reports in output/reports/

2. **System Updates**
   - Update dependencies
   - Run setup_environment.py
   - Run test suite

3. **Troubleshooting**
   - Check logs in output/logs/
   - Verify API keys in .env
   - Run setup_environment.py