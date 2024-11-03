import sys
import os
from pathlib import Path
import unittest
import json
from datetime import datetime
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag_core import PowerAppsRAG
from src.report_generator import ReportGenerator

class TestRAGSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.pdf_path = "tests/data/test_documents/Axis Program Management_Unformatted detailed.pdf"
        cls.output_dir = Path("tests/output")
        cls.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tests/test_run.log'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)

    def setUp(self):
        """Initialize RAG system for each test"""
        self.rag = PowerAppsRAG(self.pdf_path)

    def test_document_processing(self):
        """Test document processing and chunking"""
        try:
            chunk_count = self.rag.process_document()
            self.assertGreater(chunk_count, 0)
            self.logger.info(f"Document processed into {chunk_count} chunks")
        except Exception as e:
            self.logger.error(f"Document processing failed: {str(e)}")
            raise

    def test_context_retrieval(self):
        """Test context retrieval and similarity scoring"""
        try:
            # Process document first
            self.rag.process_document()
            
            # Test queries
            test_queries = [
                "What are the main features of the PowerApps system?",
                "How does the system handle data security?",
                "What are the reporting capabilities?"
            ]
            
            results = {}
            for query in test_queries:
                retrieved_context = self.rag.retrieve_context(query)
                results[query] = {
                    'count': len(retrieved_context),
                    'avg_similarity': sum(r['similarity_score'] for r in retrieved_context) / len(retrieved_context)
                }
                
            # Save retrieval results
            with open(self.output_dir / "retrieval_results.json", 'w') as f:
                json.dump(results, f, indent=2)
                
            self.logger.info("Context retrieval test completed")
        except Exception as e:
            self.logger.error(f"Context retrieval failed: {str(e)}")
            raise

    def test_report_quality(self):
        """Test report generation quality"""
        try:
            # Generate reports
            template = {
                'name': 'system_overview',
                'section': 'System Overview',
                'prompt': "Analyze the following text and provide a comprehensive overview of the system's capabilities.",
                'question': "What are the key features and capabilities described in this section?"
            }
            
            # Process document and generate analysis
            self.rag.process_document()
            analysis = self.rag.generate_section_analysis("sample_section", template)
            
            # Evaluate report quality
            quality_metrics = self.evaluate_report_quality(analysis)
            
            # Save quality metrics
            with open(self.output_dir / "quality_metrics.json", 'w') as f:
                json.dump(quality_metrics, f, indent=2)
                
            self.logger.info("Report quality test completed")
        except Exception as e:
            self.logger.error(f"Report quality test failed: {str(e)}")
            raise

    def evaluate_report_quality(self, analysis):
        """Evaluate the quality of generated reports"""
        metrics = {
            'completeness': self.check_completeness(analysis),
            'coherence': self.check_coherence(analysis),
            'relevance': self.check_relevance(analysis),
            'structure': self.check_structure(analysis),
            'timestamp': str(datetime.now())
        }
        return metrics

    def check_completeness(self, analysis):
        """Check if the analysis covers all required aspects"""
        # Implementation for completeness checking
        pass

    def check_coherence(self, analysis):
        """Check if the analysis is coherent and well-organized"""
        # Implementation for coherence checking
        pass

    def check_relevance(self, analysis):
        """Check if the analysis is relevant to the query"""
        # Implementation for relevance checking
        pass

    def check_structure(self, analysis):
        """Check if the analysis follows the required structure"""
        # Implementation for structure checking
        pass

def run_all_tests():
    """Run all tests and generate report"""
    try:
        # Run tests
        suite = unittest.TestLoader().loadTestsFromTestCase(TestRAGSystem)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        
        # Generate test report
        report = {
            'timestamp': str(datetime.now()),
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success': result.wasSuccessful()
        }
        
        # Save test report
        output_dir = Path("tests/output")
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / "test_report.json", 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        return None

if __name__ == "__main__":
    run_all_tests() 