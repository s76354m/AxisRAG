# Testing Guide

## Test Suite Organization
```
tests/
├── test_document_analyzer.py  # Core functionality tests
├── test_models.py            # Model integration tests
├── test_utils.py             # Utility function tests
└── data/                     # Test data
```

## Running Tests
### Full Test Suite
```bash
python scripts/run_tests.py
```

### Individual Test Files
```bash
pytest tests/test_document_analyzer.py
```

## Test Categories
1. **Unit Tests**
   - Individual component testing
   - Fast execution
   - No external dependencies

2. **Integration Tests**
   - Model interaction testing
   - API integration verification
   - Requires API keys

3. **System Tests**
   - End-to-end workflow testing
   - Full document processing
   - Performance benchmarking

## Adding New Tests
1. Create test file in tests/
2. Follow test naming convention: test_*.py
3. Add test data if required
4. Update test documentation