import unittest
from src.utils.evaluation_metrics import EvaluationMetrics
import textwrap

class TestEvaluationMetrics(unittest.TestCase):
    def setUp(self):
        self.metrics = EvaluationMetrics()
        self.sample_code = textwrap.dedent("""
            // This is a sample PowerApps component
            public class GalleryComponent {
                /* Properties section */
                @Input() items: any[];
                
                // Error handling
                try {
                    this.processItems();
                } catch (error) {
                    console.error("Error processing items:", error);
                }
                
                // Async data loading
                async loadData() {
                    await this.dataService.getItems();
                }
            }
        """)
        
    def test_technical_depth(self):
        """Test technical depth evaluation"""
        sample_text = """
        The PowerApps application uses a Gallery control connected to SharePoint.
        It implements CRUD operations through Patch and Collect functions.
        The data model uses Dataverse with proper error handling.
        """
        score = self.metrics.evaluate_technical_depth(sample_text)
        self.assertGreater(score, 0.5)
        self.assertLessEqual(score, 1.0)
        
    def test_code_snippets(self):
        """Test code snippet detection and evaluation"""
        text_with_code = """
        Here's an example:
        ```
        // Handle button click
        Button.OnSelect = function() {
            Collect(Items, {Title: input.Text});
        }
        ```
        """
        score = self.metrics._count_code_snippets(text_with_code)
        self.assertGreater(score, 0)
        
    def test_implementation_details(self):
        """Test implementation details analysis"""
        detailed_text = """
        The system implements a three-tier architecture:
        1. Data layer using SharePoint lists
        2. Business logic in Power Automate flows
        3. UI components with galleries and forms
        
        Error handling is implemented using try-catch blocks.
        Performance optimization includes caching and indexing.
        """
        score = self.metrics._analyze_implementation_details(detailed_text)
        self.assertGreater(score, 0.6)
        
    def test_aspect_coverage(self):
        """Test aspect coverage checking"""
        security_text = """
        The application implements role-based authentication.
        User permissions are managed through Azure AD.
        Security protocols include OAuth and JWT tokens.
        """
        self.assertTrue(self.metrics._check_aspect_coverage(security_text, 'security'))
        
    def test_pattern_adherence(self):
        """Test pattern adherence evaluation"""
        score = self.metrics._evaluate_pattern_adherence(self.sample_code)
        self.assertGreater(score, 0)
        
    def test_best_practices(self):
        """Test best practices evaluation"""
        score = self.metrics._evaluate_best_practices(self.sample_code)
        self.assertGreater(score, 0.5)
        
    def test_documentation_quality(self):
        """Test documentation quality evaluation"""
        score = self.metrics._evaluate_documentation(self.sample_code)
        self.assertGreater(score, 0.4)
        
    def test_comment_ratio(self):
        """Test comment ratio calculation"""
        ratio = self.metrics._calculate_comment_ratio(self.sample_code)
        self.assertGreater(ratio, 0)
        self.assertLessEqual(ratio, 1.0)
        
    def test_explanation_quality(self):
        """Test explanation quality evaluation"""
        text = """
        This means the component is reusable.
        For example, you can use it in multiple screens.
        Specifically, it handles data loading and error states.
        Note that proper error handling is crucial.
        """
        score = self.metrics._evaluate_explanation_quality(text)
        self.assertGreater(score, 0.6)
        
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Empty text
        self.assertEqual(self.metrics.evaluate_technical_depth(""), 0.0)
        
        # Invalid aspect
        self.assertFalse(self.metrics._check_aspect_coverage("text", "invalid_aspect"))
        
        # Malformed code
        malformed_code = "```\nunclosed code block"
        score = self.metrics._count_code_snippets(malformed_code)
        self.assertGreaterEqual(score, 0.0)

if __name__ == '__main__':
    unittest.main() 