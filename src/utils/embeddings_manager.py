import logging
import time
from typing import List, Dict

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import chromadb.config

class EmbeddingsManager:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.logger = logging.getLogger(__name__)
        self.embeddings = OpenAIEmbeddings()
        
        # Create a new collection each time to avoid ID conflicts
        self.collection_name = f"collection_{int(time.time())}"
        
        client_settings = chromadb.config.Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True
        )
        
        self.vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
            client_settings=client_settings
        )
        
    def add_documents(self, documents: List[Dict]) -> None:
        """Add documents to vector store with unique IDs"""
        try:
            # Create texts and metadatas lists
            texts = [doc['content'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            
            # Generate unique IDs based on content hash
            ids = [f"doc_{hash(text)}" for text in texts]
            
            # Add to vectorstore
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise 