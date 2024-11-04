from typing import List, Dict
from dataclasses import dataclass
import logging
from datetime import datetime
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

@dataclass
class ReportSection:
    title: str
    prompt_template: str
    summary_template: str

class ReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # Drastically reduced from 8000
            chunk_overlap=100,  # Reduced overlap
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Secondary splitter for extra-large chunks
        self.safety_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            length_function=len
        )
        
        self.sections = [
            ReportSection(
                title="Technical Architecture",
                prompt_template="""Analyze this section of the technical architecture:
                {documents}
                
                Focus on:
                - System components
                - Technical stack
                - Architecture patterns
                - Integration points
                
                Provide a concise analysis of just this section:""",
                summary_template="Architecture overview: {key_points}"
            ),
            ReportSection(
                title="Data Flow Analysis",
                prompt_template="""Analyze the data flows from these documents:
                {documents}
                Focus on:
                - Data sources
                - Data transformations
                - Data storage
                - Data access patterns
                
                Provide a detailed analysis:""",
                summary_template="Data flows: {flow_points}"
            ),
            ReportSection(
                title="Control Structure",
                prompt_template="""Analyze the control structure from these documents:
                {documents}
                Focus on:
                - Control hierarchy
                - Event handling
                - State management
                - User interactions
                
                Provide a detailed analysis:""",
                summary_template="Control patterns: {control_points}"
            ),
            ReportSection(
                title="Integration Points",
                prompt_template="""Analyze the integration points from these documents:
                {documents}
                Focus on:
                - External systems
                - APIs and interfaces
                - Data exchange patterns
                - Integration methods
                
                Provide a detailed analysis:""",
                summary_template="Integration summary: {integration_points}"
            )
        ]
        
    async def generate_comparative_report(self, chunks: List[ProcessedChunk]) -> Dict:
        """Generate comparative analysis report with strict size management"""
        try:
            self.logger.info("Generating comparative report")
            report = {}
            
            # Extract and combine content with length limit
            all_text = "\n".join(
                chunk.content[:2000] for chunk in chunks  # Limit each chunk
            )
            
            # Initial split into very small chunks
            text_chunks = self.text_splitter.split_text(all_text)
            self.logger.info(f"Split into {len(text_chunks)} small chunks for processing")
            
            # Process each section with smaller batches
            for section in self.sections:
                self.logger.info(f"Generating section: {section.title}")
                section_analyses = []
                
                # Smaller batch size
                batch_size = 3  # Reduced from 5
                for i in range(0, len(text_chunks), batch_size):
                    batch = text_chunks[i:i + batch_size]
                    
                    for j, chunk in enumerate(batch):
                        chunk_num = i + j + 1
                        try:
                            analysis = await self._analyze_chunk(section, chunk, chunk_num, len(text_chunks))
                            if analysis:  # Only add non-empty analyses
                                section_analyses.append(analysis)
                        except Exception as e:
                            self.logger.error(f"Error analyzing chunk {chunk_num}: {str(e)}")
                            continue
                
                # Combine analyses with length check
                report[section.title] = self._combine_analyses(section_analyses[:10])  # Limit number of analyses
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
            
    async def _analyze_chunk(self, section: ReportSection, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """Analyze a single chunk of text using LLM with strict size limits"""
        try:
            # Further split if chunk is still too large
            if len(chunk) > 2000:  # Much lower threshold
                sub_chunks = self.safety_splitter.split_text(chunk)
                analyses = []
                
                for i, sub_chunk in enumerate(sub_chunks):
                    prompt = section.prompt_template.format(
                        documents=f"[Part {chunk_num}.{i+1}/{total_chunks}]\n{sub_chunk[:1500]}"  # Hard limit
                    )
                    
                    try:
                        # Try OpenAI with shorter timeout
                        response = await self.openai_llm.agenerate_text(
                            prompt,
                            timeout=30
                        )
                        analyses.append(response)
                    except Exception as e:
                        self.logger.warning(f"OpenAI analysis failed: {str(e)}, trying Anthropic...")
                        try:
                            # Fallback to Anthropic with shorter timeout
                            response = await self.anthropic_llm.agenerate_text(
                                prompt,
                                timeout=30
                            )
                            analyses.append(response)
                        except Exception as e2:
                            self.logger.error(f"Both LLMs failed for sub-chunk {i+1}: {str(e2)}")
                            continue  # Skip failed chunks instead of adding error message
                
                return "\n\n".join(analyses) if analyses else "Analysis failed for this section"
                
            else:
                # Process normal-sized chunk with hard limit
                prompt = section.prompt_template.format(
                    documents=f"[Part {chunk_num}/{total_chunks}]\n{chunk[:1500]}"
                )
                
                try:
                    return await self.openai_llm.agenerate_text(prompt, timeout=30)
                except Exception as e:
                    self.logger.warning(f"OpenAI analysis failed: {str(e)}, trying Anthropic...")
                    return await self.anthropic_llm.agenerate_text(prompt, timeout=30)
                    
        except Exception as e:
            self.logger.error(f"Error analyzing chunk {chunk_num}: {str(e)}")
            return ""  # Return empty string for failed chunks
        
    def _combine_analyses(self, analyses: List[str]) -> Dict:
        """Combine multiple chunk analyses into a single section report"""
        combined_content = "\n\n".join(analyses)
        return {
            'content': combined_content,
            'metadata': {
                'chunk_count': len(analyses),
                'generated_at': datetime.now().isoformat()
            }
        }
        
    def save_report(self, report_data: Dict) -> Dict[str, str]:
        """Save report to files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = 'reports'
            os.makedirs(output_dir, exist_ok=True)
            
            # Save as JSON
            json_path = os.path.join(output_dir, f'comparative_report_{timestamp}.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'chunk_count': sum(section.get('metadata', {}).get('chunk_count', 0) 
                                         for section in report_data.values()),
                        'models': ['openai', 'anthropic']
                    },
                    'sections': report_data
                }, f, indent=2)
            
            self.logger.info(f"Report saved to {json_path}")
            
            return {
                'json_path': json_path
            }
            
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            raise