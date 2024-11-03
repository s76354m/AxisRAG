from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferWindowMemory, EntityMemory
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
import logging
import json
from pathlib import Path
from tqdm import tqdm

class PowerAppsRAG:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.setup_logging()
        self.setup_components()
        
    def setup_logging(self):
        """Configure logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rag_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_components(self):
        """Initialize core RAG components"""
        try:
            self.embeddings = OpenAIEmbeddings()
            self.llm = ChatOpenAI(temperature=0)
            self.memory = self.setup_memory()
            self.vectorstore = None  # Will be populated after document processing
            self.compressor = LLMChainExtractor.from_llm(self.llm)
            
            self.logger.info("Core components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error setting up components: {str(e)}")
            raise

    def setup_memory(self):
        """Initialize combined memory system"""
        return {
            'window': ConversationBufferWindowMemory(k=10),
            'entity': EntityMemory(llm=self.llm)
        }

    def process_document(self):
        """Process PDF document with progress tracking"""
        try:
            self.logger.info(f"Processing document: {self.pdf_path}")
            
            # Load PDF
            loader = PyPDFLoader(self.pdf_path)
            documents = loader.load()
            
            # Split text
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
                length_function=len
            )
            
            # Process chunks with progress tracking
            chunks = []
            for doc in tqdm(documents, desc="Processing pages"):
                page_chunks = splitter.split_text(doc.page_content)
                for i, chunk in enumerate(page_chunks):
                    chunks.append({
                        'content': chunk,
                        'metadata': {
                            'page': doc.metadata.get('page', 0),
                            'chunk_id': i,
                            'source': self.pdf_path
                        }
                    })
            
            # Create vectorstore
            texts = [chunk['content'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            self.vectorstore = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            self.logger.info(f"Document processed: {len(chunks)} chunks created")
            return len(chunks)
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            raise

    def retrieve_context(self, query: str, k: int = 5):
        """Retrieve and rerank context using MMR"""
        try:
            # Create compression retriever
            base_retriever = self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": k}
            )
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor,
                base_retriever=base_retriever
            )
            
            # Get compressed results
            compressed_docs = compression_retriever.get_relevant_documents(query)
            
            # Log similarity scores
            results = []
            for doc in compressed_docs:
                score = self.vectorstore.similarity_search_with_score(
                    doc.page_content, k=1
                )[0][1]
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': score
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving context: {str(e)}")
            raise

    def generate_section_analysis(self, section_text: str, template: dict):
        """Generate structured analysis for a section"""
        try:
            chain = load_qa_with_sources_chain(
                self.llm,
                chain_type="stuff",
                prompt=template.get('prompt')
            )
            
            response = chain(
                {"input_documents": [section_text], "question": template.get('question')},
                return_only_outputs=True
            )
            
            return {
                'section': template.get('section'),
                'analysis': response['output_text'],
                'metadata': {
                    'template_used': template.get('name'),
                    'timestamp': str(datetime.now())
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating section analysis: {str(e)}")
            raise

def test_core_functionality():
    """Test core RAG functionality"""
    pdf_path = "notebooks/data/Axis Program Management_Unformatted detailed.pdf"
    
    try:
        # Initialize system
        rag = PowerAppsRAG(pdf_path)
        
        # Test document processing
        chunk_count = rag.process_document()
        print(f"Document processed into {chunk_count} chunks")
        
        # Test retrieval
        query = "What are the main features of the PowerApps system?"
        results = rag.retrieve_context(query)
        print("\nRetrieval Results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Score: {result['similarity_score']}")
            print(f"Content: {result['content'][:200]}...")
            
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_core_functionality() 