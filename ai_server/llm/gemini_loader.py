
import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger("LLM")
load_dotenv()

class GeminiLoader:
    _instance = None
    _llm = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeminiLoader, cls).__new__(cls, *args, **kwargs)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """
        Gemini API 모델 초기화
        """
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")

            self._llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=0.8,
            )
            logger.info("Gemini LLM loaded successfully")
        except Exception as e:
            logger.error(f"Gemini LLM Load Failed: {e}")
            raise

    def get_llm(self):
        return self._llm
