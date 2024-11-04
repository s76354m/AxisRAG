from typing import Dict, List, Optional
from pathlib import Path
import asyncio
import logging
from datetime import datetime

from .models.llm_wrapper import LLMWrapper
from .models.embeddings import EmbeddingsManager
from .models.report_generator import ReportGenerator
from .utils.document_processor import DocumentProcessor
from .utils.evaluation_metrics import EvaluationMetrics

class AxisRAG:
    """Main orchestrator for the RAG system"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or self._default_config()
        self._initialize_components()
        
    def _default_config(self) -> Dict:
        """Default configuration settings"""
        return {
            'output_dir': Path('reports'),
            'persist_dir': Path('data/processed/vectorstore'),
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'max_tokens': 4000,
            'temperature': 0
        }
        
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            self.llm_wrapper = LLMWrapper()
            self.embeddings_manager = EmbeddingsManager(
                persist_directory=str(self.config['persist_dir'])
            )
            self.document_processor = DocumentProcessor()
            self.report_generator = ReportGenerator(self.llm_wrapper)
            self.evaluation_metrics = EvaluationMetrics()
            
            self.logger.info("All components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing components: {str(e)}")
            raise
            
    async def process_document(self, pdf_path: str) -> Dict:
        """Process document and generate comparative analysis"""
        try:
            self.logger.info(f"Starting document processing: {pdf_path}")
            
            # Process PDF into chunks
            chunks = self.document_processor.process_pdf(pdf_path)
            self.logger.info(f"Document processed into {len(chunks)} chunks")
            
            # Add chunks to vector store
            self.embeddings_manager.add_documents([{
                'content': chunk.content,
                'metadata': chunk.metadata
            } for chunk in chunks])
            
            # Generate comparative report
            report_data = await self.report_generator.generate_comparative_report(chunks)
            
            # Save report
            report_paths = self.report_generator.save_report(report_data)
            
            return {
                'status': 'success',
                'chunks_processed': len(chunks),
                'report_paths': report_paths,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in document processing pipeline: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    async def query_system(self, query: str) -> Dict:
        """Query the system with a specific question"""
        try:
            # Search for relevant chunks
            relevant_docs = self.embeddings_manager.search(query)
            
            # Generate responses from both models
            responses = await self.llm_wrapper.generate_comparison(
                self._create_query_prompt(query, relevant_docs)
            )
            
            # Evaluate responses
            evaluation = self.llm_wrapper.evaluate_responses(responses)
            
            return {
                'status': 'success',
                'responses': responses,
                'evaluation': evaluation,
                'relevant_docs': relevant_docs[:3],  # Top 3 most relevant docs
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def _create_query_prompt(self, query: str, relevant_docs: List[Dict]) -> str:
        """Create prompt for query using relevant documents"""
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']}"
            for i, doc in enumerate(relevant_docs[:3])
        ])
        
        return f"""Please answer the following question using the provided context.
        If the answer cannot be derived from the context, please state that explicitly.

        Question: {query}

        Context:
        {context}

        Please provide a detailed technical response, including:
        1. Direct references to relevant information from the context
        2. Technical implementation considerations
        3. Any potential limitations or assumptions
        4. Code examples or patterns where applicable
        """
        
    async def run_batch_analysis(self, queries: List[str]) -> Dict:
        """Run batch analysis on multiple queries"""
        try:
            results = []
            for query in queries:
                result = await self.query_system(query)
                results.append({
                    'query': query,
                    'result': result
                })
                
            return {
                'status': 'success',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in batch analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def get_system_status(self) -> Dict:
        """Get current system status and statistics"""
        try:
            return {
                'status': 'operational',
                'components': {
                    'llm_wrapper': 'operational',
                    'embeddings_manager': 'operational',
                    'document_processor': 'operational',
                    'report_generator': 'operational'
                },
                'vectorstore_stats': {
                    'total_documents': len(self.embeddings_manager.collection),
                    'last_updated': datetime.now().isoformat()
                },
                'config': self.config,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

