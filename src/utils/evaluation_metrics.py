from typing import Dict, List, Tuple
import re
from collections import Counter
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

class EvaluationMetrics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize evaluation patterns and criteria"""
        self.technical_patterns = {
            'powerapps_components': [
                'gallery', 'form', 'button', 'label', 'textinput', 'dropdown',
                'datatable', 'image', 'camera', 'barcodescanner'
            ],
            'powerapps_functions': [
                'collect', 'patch', 'remove', 'updatecontext', 'navigate',
                'launch', 'filter', 'search', 'lookup', 'first', 'last'
            ],
            'data_sources': [
                'sharepoint', 'dataverse', 'sql', 'excel', 'onedrive',
                'common data service', 'azure'
            ],
            'net_concepts': [
                'class', 'interface', 'method', 'property', 'async',
                'await', 'task', 'list', 'dictionary', 'linq'
            ]
        }
        
        self.best_practices = {
            'naming_conventions': r'[A-Z][a-zA-Z0-9]+',
            'error_handling': r'(try|catch|finally|error|exception)',
            'comments': r'(\/\/|\/\*|\*).*',
            'async_patterns': r'(async|await|\.then|promise)',
            'dependency_injection': r'(interface|service|provider|inject)'
        }
        
    def evaluate_technical_depth(self, response: str) -> float:
        """Evaluate technical depth of response"""
        try:
            metrics = {
                'technical_terms': self._count_technical_terms(response),
                'code_snippets': self._count_code_snippets(response),
                'implementation_details': self._analyze_implementation_details(response)
            }
            
            # Weighted average of metrics
            weights = {'technical_terms': 0.3, 'code_snippets': 0.4, 'implementation_details': 0.3}
            score = sum(metrics[k] * weights[k] for k in metrics)
            
            return min(1.0, score)  # Normalize to [0,1]
            
        except Exception as e:
            self.logger.error(f"Error evaluating technical depth: {str(e)}")
            return 0.0
            
    def evaluate_completeness(self, response: str) -> float:
        """Evaluate completeness of response"""
        try:
            required_aspects = [
                'architecture',
                'data_model',
                'integration',
                'security',
                'performance'
            ]
            
            covered_aspects = sum(1 for aspect in required_aspects 
                                if self._check_aspect_coverage(response, aspect))
            
            return covered_aspects / len(required_aspects)
            
        except Exception as e:
            self.logger.error(f"Error evaluating completeness: {str(e)}")
            return 0.0
            
    def evaluate_code_quality(self, response: str) -> float:
        """Evaluate code quality in response"""
        try:
            metrics = {
                'pattern_adherence': self._evaluate_pattern_adherence(response),
                'best_practices': self._evaluate_best_practices(response),
                'documentation': self._evaluate_documentation(response)
            }
            
            return sum(metrics.values()) / len(metrics)
            
        except Exception as e:
            self.logger.error(f"Error evaluating code quality: {str(e)}")
            return 0.0
            
    def _count_technical_terms(self, text: str) -> float:
        """Count technical terms in text"""
        technical_terms = [
            'PowerApps', 'Canvas App', 'Model-driven App',
            'Dataverse', 'Flow', 'Power Automate',
            'SharePoint', 'SQL', 'API', 'OAuth',
            '.NET', 'C#', 'Azure', 'Web API'
        ]
        count = sum(text.lower().count(term.lower()) for term in technical_terms)
        return min(1.0, count / 10)  # Normalize to [0,1]
        
    def _count_code_snippets(self, text: str) -> float:
        """Count and evaluate code snippets"""
        try:
            # Look for code blocks with various indicators
            code_block_patterns = [
                r'```[\s\S]*?```',  # Markdown code blocks
                r'(?m)^    .*$',    # Indented code blocks
                r'(?s)<code>.*?</code>'  # HTML code tags
            ]
            
            total_snippets = 0
            quality_score = 0
            
            for pattern in code_block_patterns:
                snippets = re.finditer(pattern, text)
                for snippet in snippets:
                    total_snippets += 1
                    snippet_text = snippet.group()
                    
                    # Evaluate snippet quality
                    quality_score += self._evaluate_snippet_quality(snippet_text)
            
            if total_snippets == 0:
                return 0.0
                
            return min(1.0, (quality_score / total_snippets))
            
        except Exception as e:
            self.logger.error(f"Error in code snippet evaluation: {str(e)}")
            return 0.0
            
    def _evaluate_snippet_quality(self, snippet: str) -> float:
        """Evaluate the quality of a code snippet"""
        quality_metrics = {
            'has_comments': bool(re.search(self.best_practices['comments'], snippet)),
            'follows_naming': bool(re.search(self.best_practices['naming_conventions'], snippet)),
            'has_error_handling': bool(re.search(self.best_practices['error_handling'], snippet)),
            'uses_async': bool(re.search(self.best_practices['async_patterns'], snippet))
        }
        
        return sum(quality_metrics.values()) / len(quality_metrics)
        
    def _analyze_implementation_details(self, text: str) -> float:
        """Analyze implementation details comprehensiveness"""
        try:
            detail_scores = []
            
            # Check for architectural components
            arch_patterns = {
                'data_layer': r'(database|schema|table|entity|model)',
                'business_logic': r'(service|manager|provider|controller)',
                'ui_components': r'(view|screen|form|gallery|component)',
                'integration': r'(api|endpoint|connection|integration)',
                'security': r'(authentication|authorization|permission|role)'
            }
            
            for category, pattern in arch_patterns.items():
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                detail_scores.append(min(1.0, matches / 3))  # Normalize to max of 1.0
                
            # Check for specific implementation patterns
            impl_patterns = self._check_implementation_patterns(text)
            detail_scores.extend(impl_patterns)
            
            return sum(detail_scores) / len(detail_scores)
            
        except Exception as e:
            self.logger.error(f"Error analyzing implementation details: {str(e)}")
            return 0.0
            
    def _check_implementation_patterns(self, text: str) -> List[float]:
        """Check for specific implementation patterns"""
        patterns = {
            'data_operations': r'(crud|create|read|update|delete|query)',
            'error_handling': r'(try|catch|error|exception|validation)',
            'async_operations': r'(async|await|promise|callback)',
            'optimization': r'(cache|index|performance|optimize)',
            'testing': r'(test|mock|assert|verify)'
        }
        
        scores = []
        for pattern in patterns.values():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            scores.append(min(1.0, matches / 3))
            
        return scores
        
    def _check_aspect_coverage(self, text: str, aspect: str) -> bool:
        """Check if an aspect is adequately covered in the text"""
        aspect_patterns = {
            'architecture': [
                r'(system|component|module|service|architecture)',
                r'(layer|tier|structure|pattern|design)'
            ],
            'data_model': [
                r'(entity|table|schema|relationship|model)',
                r'(database|dataverse|sharepoint|sql)'
            ],
            'integration': [
                r'(api|endpoint|connection|interface)',
                r'(integration|webhook|callback|event)'
            ],
            'security': [
                r'(authentication|authorization|permission)',
                r'(role|access|security|identity)'
            ],
            'performance': [
                r'(optimization|cache|index|performance)',
                r'(scale|load|response|latency)'
            ]
        }
        
        if aspect not in aspect_patterns:
            return False
            
        # Check for minimum coverage threshold
        matches = 0
        for pattern in aspect_patterns[aspect]:
            matches += len(re.findall(pattern, text, re.IGNORECASE))
            
        return matches >= 2  # Require at least 2 matches for adequate coverage
        
    def _evaluate_pattern_adherence(self, text: str) -> float:
        """Evaluate adherence to coding patterns and conventions"""
        try:
            pattern_scores = []
            
            # Check PowerApps patterns
            for category, terms in self.technical_patterns.items():
                matches = sum(text.lower().count(term.lower()) for term in terms)
                pattern_scores.append(min(1.0, matches / 5))
                
            # Check coding conventions
            convention_scores = []
            for convention, pattern in self.best_practices.items():
                matches = len(re.findall(pattern, text))
                convention_scores.append(min(1.0, matches / 3))
                
            return (sum(pattern_scores) + sum(convention_scores)) / (len(pattern_scores) + len(convention_scores))
            
        except Exception as e:
            self.logger.error(f"Error evaluating pattern adherence: {str(e)}")
            return 0.0
            
    def _evaluate_best_practices(self, text: str) -> float:
        """Evaluate adherence to best practices"""
        try:
            practice_scores = []
            
            # Best practices categories
            practices = {
                'error_handling': r'(try|catch|error|exception)',
                'logging': r'(log|trace|debug|info|error)',
                'configuration': r'(config|setting|environment|variable)',
                'validation': r'(validate|check|verify|assert)',
                'documentation': r'(\/\/|\/\*|\*|#)',
                'testing': r'(test|mock|assert|verify)',
                'dependency_management': r'(import|require|using|reference)'
            }
            
            for practice, pattern in practices.items():
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                practice_scores.append(min(1.0, matches / 3))
                
            return sum(practice_scores) / len(practice_scores)
            
        except Exception as e:
            self.logger.error(f"Error evaluating best practices: {str(e)}")
            return 0.0
            
    def _evaluate_documentation(self, text: str) -> float:
        """Evaluate documentation quality"""
        try:
            doc_metrics = {
                'comment_ratio': self._calculate_comment_ratio(text),
                'explanation_quality': self._evaluate_explanation_quality(text),
                'example_coverage': self._evaluate_example_coverage(text)
            }
            
            weights = {
                'comment_ratio': 0.3,
                'explanation_quality': 0.4,
                'example_coverage': 0.3
            }
            
            return sum(score * weights[metric] for metric, score in doc_metrics.items())
            
        except Exception as e:
            self.logger.error(f"Error evaluating documentation: {str(e)}")
            return 0.0
            
    def _calculate_comment_ratio(self, text: str) -> float:
        """Calculate the ratio of comments to code"""
        comment_lines = len(re.findall(r'(\/\/|\/\*|\*).*', text))
        total_lines = len(text.split('\n'))
        return min(1.0, comment_lines / (total_lines + 1))
        
    def _evaluate_explanation_quality(self, text: str) -> float:
        """Evaluate the quality of explanations"""
        explanation_patterns = [
            r'(?i)this (means|indicates|shows|represents)',
            r'(?i)for example',
            r'(?i)in other words',
            r'(?i)specifically',
            r'(?i)note that'
        ]
        
        matches = sum(len(re.findall(pattern, text)) for pattern in explanation_patterns)
        return min(1.0, matches / 5)
        
    def _evaluate_example_coverage(self, text: str) -> float:
        """Evaluate the coverage and quality of examples"""
        example_indicators = [
            r'(?i)example:',
            r'(?i)for instance',
            r'(?i)such as',
            r'```',
            r'(?m)^    '
        ]
        
        matches = sum(len(re.findall(pattern, text)) for pattern in example_indicators)
        return min(1.0, matches / 3) 