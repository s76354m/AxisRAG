from typing import List, Dict
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import fitz  # PyMuPDF
from tqdm import tqdm

@dataclass
class ProcessedChunk:
    content: str
    metadata: Dict
    
    def __getitem__(self, key):
        """Make the class subscriptable"""
        if key == 'content':
            return self.content
        elif key == 'metadata':
            return self.metadata
        raise KeyError(f"Key {key} not found")
        
    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            'content': self.content,
            'metadata': self.metadata
        }

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
                    
                chunk = ProcessedChunk(
                    content=text,
                    metadata={
                        'page': page_num + 1,
                        'source': pdf_path,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                chunks.append(chunk)
                
            doc.close()
            self.logger.info(f"Processed {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise