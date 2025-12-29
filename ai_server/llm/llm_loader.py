import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger("LLM")

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH")
BASE_MODEL = os.getenv("BASE_MODEL")


class LocalLLMLoader:
    _instance = None
    _llm = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LocalLLMLoader, cls).__new__(cls, *args, **kwargs)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """
        메모리에 로드
        """
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                torch_dtype=torch.float16,
                device_map="cuda"
                )
            
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=1024,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.1, # 반복 방지
                return_full_text=False  # 질문 포함하지 않고 답변만 반환
            )

            self._llm = HuggingFacePipeline(pipeline=pipe)
        except Exception as e:
            logger.error(f"LLM 로드 실패: {e}")
            raise

    def get_llm(self):
        return self._llm
