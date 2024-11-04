from typing import List, Dict, Optional
from pathlib import Path
import fitz  # PyMuPDF
import re
from dataclasses import dataclass
from tqdm import tqdm
import logging

@dataclass
class ProcessedChunk:
    content: str
    page_num: int
    chunk_id: str
    metadata: Dict

class DocumentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
    def process_pdf(self, pdf_path: str) -> List[ProcessedChunk]:
        """Process PDF document into chunks with metadata"""
        try:
            self.logger.info(f"Processing PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            chunks = []
            
            for page_num in tqdm(range(len(doc)), desc="Processing pages"):
                page = doc[page_num]
                text = page.get_text()
                
                # Extract any PowerApps specific patterns
                patterns = self._extract_patterns(text)
                
                # Create chunks with overlap
                page_chunks = self._create_chunks(text)
                
                for idx, chunk in enumerate(page_chunks):
                    chunks.append(ProcessedChunk(
                        content=chunk,
                        page_num=page_num + 1,
                        chunk_id=f"chunk_{page_num}_{idx}",
                        metadata={
                            "page": page_num + 1,
                            "patterns": patterns,
                            "source": pdf_path,
                            "chunk_index": idx
                        }
                    ))
            
            self.logger.info(f"Processed {len(chunks)} chunks from PDF")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise
            
    def _extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract PowerApps specific patterns from text"""
        patterns = {
            'controls': re.findall(r'(?:Button|Label|TextInput|Gallery)\.[\w\d]+', text),
            'functions': re.findall(r'(?:Navigate|Collect|Patch|UpdateContext)', text),
            'data_sources': re.findall(r'(?:SharePoint|SQL|Dataverse)\.[\w\d]+', text)
        }
        return patterns
        
    def _create_chunks(self, text: str) -> List[str]:
        """Create overlapping chunks of text"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Adjust chunk to end at sentence boundary if possible
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period != -1:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk)
            start = end - self.chunk_overlap
            
        return chunks 