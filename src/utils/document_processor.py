from typing import List, Dict, Optional
from pathlib import Path
import fitz  # PyMuPDF
import logging
from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class ProcessedChunk:
    content: str
    metadata: Dict

class DocumentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def process_pdf(self, pdf_path: str) -> List[ProcessedChunk]:
        """Process PDF document into chunks with metadata"""
        try:
            self.logger.info(f"Processing PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            chunks = []
            
            # Process pages with progress bar
            for page_num in tqdm(range(len(doc)), desc="Processing pages"):
                page = doc[page_num]
                text = page.get_text()
                
                # Skip empty pages
                if not text.strip():
                    continue
                    
                chunks.append(ProcessedChunk(
                    content=text,
                    metadata={
                        "page": page_num + 1,
                        "source": pdf_path
                    }
                ))
                
            doc.close()
            self.logger.info(f"Processed {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise