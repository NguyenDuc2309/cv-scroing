import json
import re
import logging
from typing import Dict
from google import genai
from openai import OpenAI
from config import config
from services.prompt_builder import build_cv_analysis_prompt
from services.info_extractor import extract_info
from services.scoring import calculate_overall_score

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.provider = config.LLM_PROVIDER.lower()
        
        if config.GEMINI_API_KEY:
            self.gemini_client = genai.Client()
            self.gemini_model = "gemini-2.5-flash-lite"
        else:
            self.gemini_client = None
            self.gemini_model = None
        
        if config.OPENAI_API_KEY:
            self.openai_client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                timeout=60.0,
                max_retries=2,
                http_client=None
            )
            self.openai_model = "gpt-4o-mini"
        else:
            self.openai_client = None
            self.openai_model = None
        
        if self.provider == "gemini" and not self.gemini_client:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        elif self.provider == "openai" and not self.openai_client:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        elif self.provider not in ["gemini", "openai"]:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _extract_json_from_response(self, text: str) -> Dict:
        text = re.sub(r'```json\s*|```\s*', '', text).strip()
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse JSON from LLM response: {str(e)}")
    
    async def analyze_cv_with_gemini(self, cv_text: str) -> Dict:
        if not self.gemini_client:
            raise ValueError("Gemini API key is not configured")
        
        try:
            prompt = build_cv_analysis_prompt(cv_text)
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model,
                contents=prompt
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            result = self._extract_json_from_response(response.text)
            
            try:
                usage = getattr(response, 'usage_metadata', None) or getattr(response, 'usage', None)
                if usage:
                    token_usage = {
                        "prompt_tokens": getattr(usage, 'prompt_token_count', 0) or 0,
                        "completion_tokens": getattr(usage, 'candidates_token_count', 0) or getattr(usage, 'completion_tokens', 0) or 0,
                        "total_tokens": getattr(usage, 'total_token_count', 0) or getattr(usage, 'total_tokens', 0) or 0
                    }
                    if token_usage.get("total_tokens", 0) > 0:
                        result["_token_usage"] = token_usage
            except Exception:
                pass
            
            return result
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def analyze_cv_with_openai(self, cv_text: str) -> Dict:
        if not self.openai_client:
            raise ValueError("OpenAI API key is not configured")
        
        try:
            prompt = build_cv_analysis_prompt(cv_text)
            
            request_params = {
                "model": self.openai_model,
                "messages": [
                    {"role": "system", "content": "Chuyên gia phân tích CV. Trả về JSON hợp lệ bằng tiếng Việt."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
            }
            
            if any(x in self.openai_model.lower() for x in ["gpt-4", "gpt-3.5-turbo", "gpt-4o"]):
                request_params["response_format"] = {"type": "json_object"}
            
            response = self.openai_client.chat.completions.create(**request_params)
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")
            
            result = self._extract_json_from_response(content)
            
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
        extracted_info = extract_info(cv_text)
        
        if self.provider == "gemini":
            result = await self.analyze_cv_with_gemini(cv_text)
        elif self.provider == "openai":
            result = await self.analyze_cv_with_openai(cv_text)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        llm_level = result.get("level", "junior")
        if not llm_level or llm_level not in ["intern", "fresher", "junior", "mid", "senior"]:
            llm_level = "junior"

        result["level"] = llm_level

        if "info" in result and isinstance(result["info"], dict):
            extracted_info["location"] = result["info"].get("location", "")

        result["info"] = extracted_info

        credibility_issues = result.get("credibility_issues", [])
        if not isinstance(credibility_issues, list):
            credibility_issues = []
        result["credibility_issues"] = credibility_issues

        try:
            core_scores = result.get("core_scores", {})
            bonus_scores = result.get("bonus_scores", {})
            if isinstance(core_scores, dict) and isinstance(bonus_scores, dict):
                calculated_overall = calculate_overall_score(
                    llm_level, 
                    core_scores, 
                    bonus_scores,
                    credibility_issues=credibility_issues
                )
                result["overall_score"] = calculated_overall
            else:
                logger.warning(f"Missing core_scores or bonus_scores in LLM response. core_scores type: {type(core_scores)}, bonus_scores type: {type(bonus_scores)}")
        except Exception as e:
            logger.error(f"Error calculating overall_score: {e}. Keeping LLM's overall_score if available.")
            if "overall_score" not in result:
                result["overall_score"] = 0

        return result


_llm_service_instance = None


def get_llm_service() -> LLMService:
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance

