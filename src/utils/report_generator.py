from typing import List, Dict
from dataclasses import dataclass
import logging
from datetime import datetime
import os

@dataclass
class ReportSection:
    title: str
    prompt_template: str
    summary_template: str

class ReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sections = [
            ReportSection(
                title="Technical Architecture",
                prompt_template="""Analyze the technical architecture from these documents:
                {documents}
                Focus on:
                - System components
                - Technical stack
                - Architecture patterns
                - Integration points
                
                Provide a detailed analysis:""",
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
        """Generate comparative analysis report from document chunks"""
        try:
            self.logger.info("Generating comparative report")
            report = {}
            
            # Convert chunks to dictionary format
            documents = [chunk.to_dict()['content'] for chunk in chunks]
            
            # Generate report for each section
            for section in self.sections:
                self.logger.info(f"Generating section: {section.title}")
                report[section.title] = self._analyze_section(
                    section,
                    "\n".join(documents)
                )
                
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
            
    def _analyze_section(self, section: ReportSection, documents: str) -> Dict:
        """Analyze documents for a specific report section"""
        return {
            'title': section.title,
            'content': section.prompt_template.format(documents=documents),
            'metadata': {
                'generated_at': datetime.now().isoformat()
            }
        }
        
    def save_report(self, report_data: Dict) -> Dict[str, str]:
        """Save report to files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join('notebooks', 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # Save main report
            main_path = os.path.join(output_dir, f'analysis_report_{timestamp}.txt')
            with open(main_path, 'w', encoding='utf-8') as f:
                for section_title, data in report_data.items():
                    f.write(f"\n=== {section_title} ===\n")
                    f.write(data['content'])
                    f.write("\n\n")
                    
            return {
                'main_report': main_path
            }
            
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            raise