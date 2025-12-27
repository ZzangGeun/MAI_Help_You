# -*- coding: utf-8 -*-
"""AI 서비스 모듈

이 모듈은 사전 학습된 Qwen 모델을 로드하고, 비동기 함수 `get_ai_response_async` 를 제공하여
FastAPI 엔드포인트에서 호출될 수 있도록 설계되었습니다.
모델과 토크나이저는 모듈 레벨에서 싱글톤으로 초기화되어 첫 호출 시에만 로드됩니다.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Any

# 전역 싱글톤 객체 (첫 호출 시 로드)
_model: Any | None = None
_tokenizer: Any | None = None

def _load_model() -> None:
    """모델과 토크나이저를 한 번만 로드합니다.
    메모리 사용량을 최소화하고, 여러 요청에서 재사용하도록 합니다.
    """
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        model_path = r"C:\\Users\\ccg70\\OneDrive\\desktop\\programming\\MAI_Help_You\\fine_tuned_model\\merged_qwen"
        _model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16)
        _tokenizer = AutoTokenizer.from_pretrained(model_path)
        if torch.cuda.is_available():
            _model.to('cuda')

async def get_ai_response_async(prompt: str) -> str:
    """주어진 프롬프트에 대해 AI 응답을 비동기로 반환합니다.

    Args:
        prompt: 사용자 입력 문자열
    Returns:
        모델이 생성한 응답 문자열
    """
    _load_model()
    inputs = _tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.to('cuda') for k, v in inputs.items()}
    with torch.no_grad():
        output = _model.generate(
            **inputs,
            max_new_tokens=1024,  # 입력 길이와 무관하게 생성할 토큰 수만 제한
            do_sample=True,
            top_p=0.9,
            top_k=50,
            temperature=0.7
            )
    response = _tokenizer.decode(output[0], skip_special_tokens=True)
    return response
