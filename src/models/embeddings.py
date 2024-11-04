from typing import List, Dict
import numpy as np
from langchain_openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings
import logging

class EmbeddingsManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.logger = logging.getLogger(__name__)
        self.embeddings = OpenAIEmbeddings()
        self.chroma_client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
        )
        self.collection = self._initialize_collection()
        
    def _initialize_collection(self):
        """Initialize or get existing Chroma collection"""
        try:
            collection = self.chroma_client.create_collection(
                name="powerapps_docs",
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info("Chroma collection initialized")
            return collection
        except Exception as e:
            self.logger.error(f"Error initializing collection: {str(e)}")
            raise
            
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to the vector store"""
        try:
            # Process in batches of 100
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                texts = [doc['content'] for doc in batch]
                ids = [f"doc_{i + idx}" for idx in range(len(batch))]
                metadatas = [doc['metadata'] for doc in batch]
                
                embeddings = self.embeddings.embed_documents(texts)
                
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    ids=ids,
                    metadatas=metadatas
                )
                
            self.logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise
            
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        try:
            query_embedding = self.embeddings.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for idx in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][idx],
                    'metadata': results['metadatas'][0][idx],
                    'similarity': 1 - results['distances'][0][idx]  # Convert distance to similarity
                })
                
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            raise 