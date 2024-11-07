from typing import List, Dict
from dataclasses import dataclass
import logging
from datetime import datetime
import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.utils.document_processor import ProcessedChunk

@dataclass
class ReportSection:
    title: str
    prompt_template: str
    summary_template: str

class ReportGenerator:
    def __init__(self, llm_wrapper=None):
        self.logger = logging.getLogger(__name__)
        self.llm_wrapper = llm_wrapper
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.sections = [
            ReportSection(
                title="Technical Architecture",
                prompt_template="""Analyze this section of the technical architecture:
                {documents}
                Focus on system components, technical stack, and architecture patterns.
                Provide a concise analysis of this section.""",
                summary_template="Architecture overview: {key_points}"
            ),
            ReportSection(
                title="Data Flow Analysis",
                prompt_template="""Analyze the data flows in this section:
                {documents}
                Focus on data sources, transformations, and access patterns.
                Provide a concise analysis of this section.""",
                summary_template="Data flows: {flow_points}"
            ),
            ReportSection(
                title="Control Structure",
                prompt_template="""Analyze the control structure in this section:
                {documents}
                Focus on control hierarchy, event handling, and user interactions.
                Provide a concise analysis of this section.""",
                summary_template="Control patterns: {control_points}"
            ),
            ReportSection(
                title="Integration Points",
                prompt_template="""Analyze the integration points in this section:
                {documents}
                Focus on external systems, APIs, and data exchange patterns.
                Provide a concise analysis of this section.""",
                summary_template="Integration points: {integration_points}"
            )
        ]

    async def _analyze_chunk(self, section: ReportSection, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """Analyze a single chunk of text using LLM"""
        try:
            prompt = section.prompt_template.format(
                documents=f"[Part {chunk_num}/{total_chunks}]\n{chunk[:1500]}"
            )
            
            try:
                return await self.llm_wrapper.generate_text(prompt)
            except Exception as e:
                self.logger.error(f"Error analyzing chunk {chunk_num}: {str(e)}")
                return f"Analysis failed for part {chunk_num}"
                
        except Exception as e:
            self.logger.error(f"Error analyzing chunk {chunk_num}: {str(e)}")
            return f"Analysis failed for part {chunk_num}"

    async def generate_comparative_report(self, chunks: List[ProcessedChunk]) -> Dict:
        """Generate comparative analysis report with strict size management"""
        try:
            self.logger.info("Generating comparative report")
            report = {}
            
            # Process in very small batches
            batch_size = 2
            
            for section in self.sections:
                self.logger.info(f"Generating section: {section.title}")
                section_analyses = []
                
                # Combine content with stricter limits
                all_text = "\n".join(
                    chunk.content[:1000] for chunk in chunks
                )
                
                text_chunks = self.text_splitter.split_text(all_text)
                self.logger.info(f"Processing {len(text_chunks)} chunks for {section.title}")
                
                for i in range(0, len(text_chunks), batch_size):
                    batch = text_chunks[i:i + batch_size]
                    
                    for j, chunk in enumerate(batch):
                        chunk_num = i + j + 1
                        try:
                            # Add more context to the prompt
                            analysis = await self._analyze_chunk(
                                section, 
                                chunk[:500],
                                chunk_num, 
                                len(text_chunks)
                            )
                            if analysis and analysis != f"Analysis failed for part {chunk_num}":
                                section_analyses.append(analysis)
                        except Exception as e:
                            self.logger.error(f"Error analyzing chunk {chunk_num}: {str(e)}")
                            continue
                
                # Only include successful analyses
                if section_analyses:
                    report[section.title] = {
                        'content': "\n\n".join(section_analyses),
                        'metadata': {
                            'chunk_count': len(section_analyses),
                            'generated_at': datetime.now().isoformat()
                        }
                    }
                else:
                    report[section.title] = {
                        'content': "No successful analysis generated for this section",
                        'metadata': {
                            'chunk_count': 0,
                            'generated_at': datetime.now().isoformat()
                        }
                    }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise

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
                        'chunk_count': sum(
                            section.get('metadata', {}).get('chunk_count', 0) 
                            for section in report_data.values()
                        ),
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