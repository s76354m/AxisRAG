from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List
import json
import os
import sys
from dotenv import load_dotenv
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Updated imports for LangChain
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate

class DocumentAnalyzer:
    def __init__(self, pdf_path: str):
        # Load environment variables
        load_dotenv()
        
        # Verify API keys
        self.verify_api_keys()
        
        self.pdf_path = Path(pdf_path)
        self.setup_logging()
        self.setup_models()
    
    def verify_api_keys(self):
        """Verify required API keys are present"""
        required_keys = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
        }
        
        missing_keys = [key for key, value in required_keys.items() if not value]
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")

    def setup_logging(self):
        """Configure logging"""
        log_file = f"output/logs/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_models(self):
        """Initialize language models"""
        try:
            # Get model configurations from environment
            openai_model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4-1106-preview')
            anthropic_model_name = os.getenv('ANTHROPIC_MODEL_NAME', 'claude-2.1')
            temperature = float(os.getenv('TEMPERATURE', '0'))
            
            self.openai_model = ChatOpenAI(
                temperature=temperature,
                model_name=openai_model_name
            )
            
            self.anthropic_model = ChatAnthropic(
                temperature=temperature,
                model_name=anthropic_model_name
            )
            
            self.embeddings = OpenAIEmbeddings()
            
            self.logger.info(f"Models initialized successfully:")
            self.logger.info(f"OpenAI Model: {openai_model_name}")
            self.logger.info(f"Anthropic Model: {anthropic_model_name}")
            
        except Exception as e:
            self.logger.error(f"Error setting up models: {str(e)}")
            raise

    def load_and_split_document(self) -> List[str]:
        """Load PDF and split into chunks with optimized size"""
        self.logger.info(f"Loading document: {self.pdf_path}")
        
        # Adjusted chunk configurations for better performance
        chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))  # Smaller chunks
        chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '100'))
        
        loader = PyPDFLoader(str(self.pdf_path))
        documents = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        chunks = splitter.split_documents(documents)
        total_chunks = len(chunks)
        self.logger.info(f"Document split into {total_chunks} chunks")
        
        # If too many chunks, combine some
        max_chunks = 20  # Adjust based on your needs
        if total_chunks > max_chunks:
            self.logger.info(f"Consolidating chunks from {total_chunks} to {max_chunks}")
            consolidated_chunks = []
            chunk_size = len(chunks) // max_chunks
            for i in range(0, len(chunks), chunk_size):
                combined_chunk = chunks[i:i + chunk_size]
                consolidated_chunks.append(combined_chunk[0].page_content + "\n".join(c.page_content for c in combined_chunk[1:]))
            chunks = consolidated_chunks
        
        return chunks

    def create_vectorstore(self, chunks: List[str]):
        """Create vector store from document chunks"""
        return Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="db/chroma_db"
        )

    def generate_summary(self, chunks: List[str], model, system_name: str) -> Dict:
        """Generate summary with progress monitoring"""
        try:
            self.logger.info(f"Generating {system_name} summary...")
            start_time = time.time()
            
            # Modified summary template for more focused analysis
            summary_template = """
            Analyze this document section concisely, focusing on:
            1. Key technical features
            2. Integration requirements
            3. Critical implementation details
            
            Section:
            {text}
            
            Provide a brief, focused technical summary.
            """

            prompt = PromptTemplate(template=summary_template, input_variables=["text"])
            
            # Process chunks with progress bar
            summaries = []
            with tqdm(total=len(chunks), desc=f"{system_name} Analysis") as pbar:
                for chunk in chunks:
                    summary = model.predict(prompt.format(text=chunk))
                    summaries.append(summary)
                    pbar.update(1)
            
            # Combine summaries
            combined_summary = "\n\n".join(summaries)
            
            # Final consolidation pass
            final_prompt = """
            Consolidate these section summaries into a cohesive technical analysis:

            {text}

            Provide a structured final summary focusing on implementation details.
            """
            final_summary = model.predict(final_prompt.format(text=combined_summary))
            
            # Save summary
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"output/reports/analysis_report_{system_name}_{timestamp}.txt"
            
            with open(output_file, 'w') as f:
                f.write(f"Analysis Report ({system_name})\n")
                f.write("=" * 50 + "\n\n")
                f.write(final_summary)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Generated {system_name} summary in {elapsed_time:.2f} seconds")
            
            return {
                "system": system_name,
                "summary": final_summary,
                "file": output_file,
                "timestamp": timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error generating {system_name} summary: {str(e)}")
            raise

    def analyze_document(self) -> Dict:
        """Complete document analysis with parallel processing"""
        try:
            self.logger.info("Starting document analysis...")
            start_time = time.time()
            
            # Load and process document
            chunks = self.load_and_split_document()
            
            # Generate summaries in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_openai = executor.submit(self.generate_summary, chunks, self.openai_model, "openai")
                future_anthropic = executor.submit(self.generate_summary, chunks, self.anthropic_model, "anthropic")
                
                openai_summary = future_openai.result()
                anthropic_summary = future_anthropic.result()
            
            # Compare summaries
            comparison = self.compare_summaries(openai_summary, anthropic_summary)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Complete analysis finished in {elapsed_time:.2f} seconds")
            
            return {
                "openai": openai_summary,
                "anthropic": anthropic_summary,
                "comparison": comparison
            }
            
        except Exception as e:
            self.logger.error(f"Error during document analysis: {str(e)}")
            raise

    def compare_summaries(self, openai_summary: Dict, anthropic_summary: Dict) -> Dict:
        """Compare summaries from different models"""
        try:
            # Use OpenAI to analyze differences
            comparison_prompt = f"""
            Compare the following two technical summaries and identify:
            1. Key differences in identified features
            2. Unique insights from each analysis
            3. Areas of agreement
            4. Overall recommendation for which analysis provides more actionable insights

            Summary 1 (OpenAI):
            {openai_summary['summary']}

            Summary 2 (Anthropic):
            {anthropic_summary['summary']}
            """

            comparison = self.openai_model.predict(comparison_prompt)
            
            # Save comparison
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comparison_file = f"output/reports/summary_comparison_{timestamp}.txt"
            
            with open(comparison_file, 'w') as f:
                f.write("Summary Comparison Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(comparison)
            
            return {
                "comparison": comparison,
                "file": comparison_file,
                "timestamp": timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing summaries: {str(e)}")
            raise

def main():
    pdf_path = "data/raw/Axis Program Management_Unformatted detailed.pdf"
    analyzer = DocumentAnalyzer(pdf_path)
    
    try:
        results = analyzer.analyze_document()
        print("\nAnalysis completed successfully!")
        print("\nGenerated files:")
        print(f"OpenAI Summary: {results['openai']['file']}")
        print(f"Anthropic Summary: {results['anthropic']['file']}")
        print(f"Comparison Report: {results['comparison']['file']}")
        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 