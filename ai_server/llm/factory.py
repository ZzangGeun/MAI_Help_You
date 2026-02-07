
import os
import logging
from dotenv import load_dotenv

from .llm_loader import LocalLLMLoader
from .gemini_loader import GeminiLoader

load_dotenv()
logger = logging.getLogger("LLM_Factory")

class LLMFactory:
    @staticmethod
    def get_llm_loader():
        provider = os.getenv("LLM_PROVIDER", "local").lower()
        
        logger.info(f"Selected LLM Provider: {provider}")
        
        if provider == "gemini":
            return GeminiLoader()
        elif provider == "local":
            return LocalLLMLoader()
        else:
            logger.warning(f"Unknown provider '{provider}', falling back to Local")
            return LocalLLMLoader()

    @staticmethod
    def get_llm():
        """
        편의 메서드: 로더를 거쳐 바로 LLM 객체 반환
        """
        loader = LLMFactory.get_llm_loader()
        return loader.get_llm()
