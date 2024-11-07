from typing import Dict, Optional
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import logging

class LLMWrapper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {
            'openai': ChatOpenAI(
                model_name="gpt-4-1106-preview",
                temperature=0.7,
                max_tokens=4096
            ),
            'anthropic': ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=0.7,
                max_tokens=8192
            )
        }
        self.logger.info("Models initialized successfully")

    async def generate_text(self, prompt: str, timeout: int = 30) -> str:
        """Generate text using OpenAI first, fallback to Anthropic"""
        try:
            response = await self.models['openai'].ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"Error with openai: {str(e)}")
            try:
                response = await self.models['anthropic'].ainvoke(prompt)
                return response.content
            except Exception as e:
                self.logger.error(f"Error with anthropic: {str(e)}")
                raise
        
    async def generate_comparison(self, prompt: str) -> Dict[str, str]:
        """Generate responses from both models for comparison"""
        results = {}
        
        for model_name, model in self.models.items():
            try:
                self.logger.info(f"Generating response with {model_name}")
                response = await model.ainvoke([HumanMessage(content=prompt)])
                results[model_name] = response.content
                self.logger.info(f"{model_name} response generated successfully")
            except Exception as e:
                self.logger.error(f"Error with {model_name}: {str(e)}")
                results[model_name] = f"Error: {str(e)}"
                
        return results
        
    def evaluate_responses(self, responses: Dict[str, str]) -> Dict[str, float]:
        """Evaluate and compare responses from both models"""
        metrics = {
            'technical_depth': self._evaluate_technical_depth,
            'completeness': self._evaluate_completeness,
            'code_quality': self._evaluate_code_quality
        }
        
        evaluation = {}
        for model_name, response in responses.items():
            evaluation[model_name] = {
                metric: evaluator(response)
                for metric, evaluator in metrics.items()
            }
            
        return evaluation
        
    def _evaluate_technical_depth(self, response: str) -> float:
        """Evaluate technical depth of response"""
        # Implementation for technical depth scoring
        pass
        
    def _evaluate_completeness(self, response: str) -> float:
        """Evaluate completeness of response"""
        # Implementation for completeness scoring
        pass
        
    def _evaluate_code_quality(self, response: str) -> float:
        """Evaluate code quality in response"""
        # Implementation for code quality scoring
        pass 