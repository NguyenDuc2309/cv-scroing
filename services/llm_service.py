import json
import re
from typing import Dict
import google.generativeai as genai
from openai import OpenAI
from config import config
from services.prompt_builder import build_cv_analysis_prompt


class LLMService:
    """Service for interacting with LLM providers (Gemini/OpenAI)"""
    
    def __init__(self):
        self.provider = config.LLM_PROVIDER.lower()
        
        # Initialize Gemini if API key is available
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
        
        # Initialize OpenAI if API key is available
        if config.OPENAI_API_KEY:
            # Create OpenAI client with explicit parameters
            # Note: Newer versions of OpenAI client are compatible with httpx 0.28+
            self.openai_client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                timeout=60.0,
                max_retries=2,
                # Explicitly disable proxies to avoid httpx 0.28+ compatibility issues
                http_client=None  # Use default client, which handles httpx properly
            )
            self.openai_model = config.OPENAI_MODEL
        else:
            self.openai_client = None
            self.openai_model = None
        
        # Validate that the configured provider has API key
        if self.provider == "gemini" and not self.gemini_model:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        elif self.provider == "openai" and not self.openai_client:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        elif self.provider not in ["gemini", "openai"]:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _extract_json_from_response(self, text: str) -> Dict:
        """Extract JSON from LLM response, handling markdown code blocks and escape characters"""
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        # Remove any leading/trailing whitespace and newlines
        text = text.strip()
        
        # Try to find JSON object (match from first { to last })
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                # Parse JSON - this will handle escaped characters properly
                parsed = json.loads(json_str)
                # Clean up any strings that might have unwanted escape sequences
                return self._clean_json_response(parsed)
            except json.JSONDecodeError:
                pass
        
        # If no match, try parsing the whole text
        try:
            parsed = json.loads(text)
            return self._clean_json_response(parsed)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse JSON from LLM response: {str(e)}")
    
    def _clean_json_response(self, data: Dict) -> Dict:
        """Clean up JSON response by removing unwanted escape sequences from strings"""
        if isinstance(data, dict):
            return {k: self._clean_json_response(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_json_response(item) for item in data]
        elif isinstance(data, str):
            # Remove literal \n sequences that shouldn't be there
            # But keep actual newlines if they're properly escaped in JSON
            # This is tricky - we'll just return as-is since JSON parsing handles it
            return data
        else:
            return data
    
    async def analyze_cv_with_gemini(self, cv_text: str) -> Dict:
        """Analyze CV using Gemini API"""
        if not self.gemini_model:
            raise ValueError("Gemini API key is not configured")
        
        try:
            prompt = build_cv_analysis_prompt(cv_text)
            response = self.gemini_model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            result = self._extract_json_from_response(response.text)
            
            # Extract token usage from Gemini response
            token_usage = None
            try:
                # Gemini API returns usage_metadata in response
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    usage = response.usage_metadata
                    token_usage = {
                        "prompt_tokens": getattr(usage, 'prompt_token_count', 0) or 0,
                        "completion_tokens": getattr(usage, 'candidates_token_count', 0) or 0,
                        "total_tokens": getattr(usage, 'total_token_count', 0) or 0
                    }
                # Alternative: check response.usage (for some API versions)
                elif hasattr(response, 'usage') and response.usage:
                    usage = response.usage
                    token_usage = {
                        "prompt_tokens": getattr(usage, 'prompt_token_count', 0) or 0,
                        "completion_tokens": getattr(usage, 'candidates_token_count', 0) or 0,
                        "total_tokens": getattr(usage, 'total_token_count', 0) or 0
                    }
            except Exception:
                # If token usage is not available, continue without it
                token_usage = None
            
            if token_usage and token_usage.get("total_tokens", 0) > 0:
                result["_token_usage"] = token_usage
            
            return result
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def analyze_cv_with_openai(self, cv_text: str) -> Dict:
        """Analyze CV using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI API key is not configured")
        
        try:
            prompt = build_cv_analysis_prompt(cv_text)
            
            # Check if model supports json_object response format
            # Only gpt-4, gpt-4-turbo, gpt-3.5-turbo (newer versions) support it
            model_lower = self.openai_model.lower()
            supports_json_mode = any(x in model_lower for x in [
                "gpt-4", "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"
            ])
            
            # Build request parameters
            request_params = {
                "model": self.openai_model,
                "messages": [
                    {"role": "system", "content": "Bạn là chuyên gia phân tích CV. Luôn trả về kết quả dưới dạng JSON hợp lệ bằng tiếng Việt. Tất cả nội dung text phải bằng tiếng Việt."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
            }
            
            # Only add response_format if model supports it
            if supports_json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            response = self.openai_client.chat.completions.create(**request_params)
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")
            
            result = self._extract_json_from_response(content)
            
            # Extract token usage from OpenAI response
            if hasattr(response, 'usage') and response.usage:
                token_usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
                result["_token_usage"] = token_usage
            
            return result
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def analyze_cv(self, cv_text: str) -> Dict:
        """
        Analyze CV using the configured LLM provider from environment.
        
        Args:
            cv_text: Extracted text from CV
            
        Returns:
            Dictionary with analysis results
        """
        if self.provider == "gemini":
            return await self.analyze_cv_with_gemini(cv_text)
        elif self.provider == "openai":
            return await self.analyze_cv_with_openai(cv_text)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


# Global instance - will be initialized on first use
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance (lazy initialization)"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance

