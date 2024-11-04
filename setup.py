from setuptools import setup, find_packages

setup(
    name="axis-rag",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'click',
        'rich',
        'python-dotenv',
        'PyMuPDF',
        'langchain',
        'langchain-openai',
        'langchain-anthropic',
        'chromadb',
    ],
) 