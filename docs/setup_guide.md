# Setup and Deployment Guide

## Prerequisites
- Python 3.9+
- OpenAI API key
- Anthropic API key

## Installation
1. Clone the repository
2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Create .env file with required API keys

## Configuration
Key environment variables:
```ini
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENAI_MODEL_NAME=gpt-4-1106-preview
ANTHROPIC_MODEL_NAME=claude-2.1
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
MAX_CHUNKS=20
```