from typing import List, Dict, Optional
from datetime import datetime
import json
import asyncio
from pathlib import Path
import logging
from .llm_wrapper import LLMWrapper

class ReportGenerator:
    def __init__(self, llm_wrapper: LLMWrapper):
        self.logger = logging.getLogger(__name__)
        self.llm_wrapper = llm_wrapper
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
        
    async def generate_comparative_report(self, chunks: List[Dict]) -> Dict:
        """Generate comparative analysis from both models"""
        try:
            sections = self._get_report_sections()
            report_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'chunk_count': len(chunks),
                    'models': ['openai', 'anthropic']
                },
                'sections': {}
            }
            
            for section in sections:
                self.logger.info(f"Generating section: {section['title']}")
                
                # Generate prompts for this section
                prompt = self._create_section_prompt(section, chunks)
                
                # Get responses from both models
                responses = await self.llm_wrapper.generate_comparison(prompt)
                
                # Evaluate responses
                evaluation = self.llm_wrapper.evaluate_responses(responses)
                
                report_data['sections'][section['title']] = {
                    'responses': responses,
                    'evaluation': evaluation
                }
                
            return report_data
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
            
    def save_report(self, report_data: Dict, report_type: str = "comparative"):
        """Save report to file system"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.output_dir / f"{report_type}_report_{timestamp}.json"
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
                
            self.logger.info(f"Report saved to {report_path}")
            
            # Generate HTML version
            html_path = self.output_dir / f"{report_type}_report_{timestamp}.html"
            self._generate_html_report(report_data, html_path)
            
            return {
                'json_path': str(report_path),
                'html_path': str(html_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            raise
            
    def _get_report_sections(self) -> List[Dict]:
        """Define report sections and their prompts"""
        return [
            {
                'title': 'Technical Architecture',
                'prompt_template': """Analyze the technical architecture of the PowerApps application:
                1. Identify key components and their relationships
                2. Analyze the data flow and integration points
                3. Evaluate the technical implementation patterns
                4. Identify potential .NET conversion considerations
                
                Context:
                {context}
                """
            },
            {
                'title': 'Data Model',
                'prompt_template': """Analyze the data model and storage patterns:
                1. Identify data sources and their relationships
                2. Analyze data access patterns
                3. Evaluate data integrity mechanisms
                4. Consider .NET data access equivalents
                
                Context:
                {context}
                """
            },
            # Add more sections as needed
        ]
        
    def _create_section_prompt(self, section: Dict, chunks: List[Dict]) -> str:
        """Create prompt for specific section using relevant chunks"""
        relevant_chunks = self._filter_relevant_chunks(section, chunks)
        context = "\n".join([chunk['content'] for chunk in relevant_chunks])
        return section['prompt_template'].format(context=context)
        
    def _filter_relevant_chunks(self, section: Dict, chunks: List[Dict]) -> List[Dict]:
        """Filter chunks relevant to specific section"""
        # Implement relevance filtering logic
        return chunks  # For now, return all chunks
        
    def _generate_html_report(self, report_data: Dict, output_path: Path):
        """Generate HTML version of the report"""
        # Implement HTML generation logic
        pass 