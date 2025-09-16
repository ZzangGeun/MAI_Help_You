import os
import logging
from typing import List, Dict, Any, Optional
import sys

# services 폴더를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'services')
if services_dir not in sys.path:
    sys.path.append(services_dir)

# 통합 챗봇 서비스 import
try:
    from ai_models.chatbot_service import ChatbotAPIService
    logger = logging.getLogger(__name__)
    logger.info("통합 챗봇 서비스를 로드했습니다.")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"통합 챗봇 서비스 로드 실패: {e}")
    # 폴백: 기존 서비스 사용
    from .rag_engine import RagEngine
    import requests
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from huggingface_hub import login
    
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    FASTAPI_MODEL_URL = os.getenv("FASTAPI_MODEL_URL", "http://127.0.0.1:8001/api/chat")
    USE_REMOTE_LLM = os.getenv("USE_REMOTE_LLM", "auto").lower()
    if USE_REMOTE_LLM not in {"true", "false"}:
        REMOTE_MODE = bool(FASTAPI_MODEL_URL)
    else:
        REMOTE_MODE = USE_REMOTE_LLM == "true"
    
    if HUGGINGFACE_TOKEN:
        try:
            login(HUGGINGFACE_TOKEN)
        except Exception as _e:
            logger.warning("Hugging Face Hub 로그인 실패: %s", str(_e))

class CustomLLM:
    """간단한 로컬 HF 모델 래퍼 (LangChain 의존 제거).

    _call(prompt: str) -> str 만 제공.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model: Any = None
        self.tokenizer: Any = None
        self.model_path: str = model_path or os.getenv("LOCAL_MODEL_PATH", "fine_tuned_model/merged_qwen")
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                logger.info("로컬 파인튜닝된 모델을 로드합니다...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, auth_token=HUGGINGFACE_TOKEN)
                if getattr(self.tokenizer, "pad_token", None) is None:
                    self.tokenizer.pad_token = getattr(self.tokenizer, "eos_token", None)
                device = "cuda" if torch.cuda.is_available() else "cpu"
                dtype = torch.float16 if torch.cuda.is_available() else torch.float32
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=dtype,
                    trust_remote_code=True,
                    auth_token=HUGGINGFACE_TOKEN,
                )
                self.model.to(device)
                logger.info("로컬 파인튜닝된 모델 로드 완료")
                return

            logger.info("공개 모델을 로드합니다...")
            base_model_name = os.getenv("HF_BASE_MODEL", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B")
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
            if getattr(self.tokenizer, "pad_token", None) is None:
                self.tokenizer.pad_token = getattr(self.tokenizer, "eos_token", None)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_name, torch_dtype=dtype, trust_remote_code=True
            )
            self.model.to(device)
            logger.info("공개 모델 로드 완료")
        except Exception as e:
            logger.error("모델 로딩 중 오류: %s", e)
            self.model = None
            self.tokenizer = None

    def _call(self, prompt: str) -> str:
        if self.model is None or self.tokenizer is None:
            return "죄송합니다. AI 모델을 로드할 수 없습니다. 관리자에게 문의하세요."
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=512,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if prompt in response:
                response = response.replace(prompt, "").strip()
            return response or "죄송합니다. 답변을 생성할 수 없습니다."
        except Exception as e:
            logger.error("텍스트 생성 오류: %s", e)
            return f"오류가 발생했습니다: {str(e)}"

class ChatbotService:
    """LangChain(pgvector) 기반 챗봇 서비스 (로컬/원격 LLM 모드)

    - 로컬 모드: CustomLLM + LangChain RagEngine 검색결과를 컨텍스트에 주입
    - 원격 모드: FastAPI 모델 엔드포인트 호출 (간단 컨텍스트 주입)
    - 사용자별 히스토리는 메모리에 저장
    - LangChain PGVector를 사용한 의미 검색 기능
    """

    def __init__(self):
        self.remote_mode = REMOTE_MODE
        try:
            # 사용자별 히스토리만 보관 (간단 dict: uid -> List[{'user','assistant'}])
            self.user_histories: Dict[str, List[Dict[str, str]]] = {}

            if not self.remote_mode:
                self.llm = CustomLLM()
                self.rag = RagEngine()
            else:
                self.llm = None
                self.rag = None
                logger.info("ChatbotService: 원격 LLM 모드 활성화 (모델 로딩 생략)")
        except Exception as e:
            logger.error(f"ChatbotService 초기화 중 오류: {str(e)}")
            self.llm = None
            self.rag = None
            self.user_histories = {}
    
    def get_response(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """질문에 대한 답변을 생성합니다.

        user_id 가 없을 경우 'anonymous' 키로 히스토리를 분리한다.
        (뷰 레벨에서 세션 키를 전달하므로 실제로는 세션 기반 식별자 사용 기대)
        """
        try:
            uid = user_id or "anonymous"
            if self.remote_mode:
                # 최근 히스토리 몇 개(최대 5쌍) 프롬프트에 포함
                prior = self.get_chat_history(uid)
                condensed = "".join([f"사용자: {p['user']}\nAI: {p['assistant']}\n" for p in prior[-5:]])
                final_question = question if not condensed else (
                    "다음은 지금까지의 대화입니다:\n" + condensed + "\n사용자 질문: " + question + "\nAI 답변:"
                )
                try:
                    resp = requests.post(
                        FASTAPI_MODEL_URL,
                        json={"question": final_question, "user_id": uid},
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        j = resp.json()
                        response = j.get("response") or j.get("answer") or "응답을 가져오지 못했습니다."
                    else:
                        response = f"원격 모델 오류: HTTP {resp.status_code}"
                except Exception as e:
                    response = f"원격 모델 호출 실패: {e}"
                sources = []
                has_rag = False
            else:
                # 로컬: RAG 검색 → 컨텍스트 주입 → LLM 호출
                context_blocks = []
                if self.rag:
                    hits = self.rag.retrieve_texts(question, top_k=3)
                    for text, meta in hits:
                        context_blocks.append(text[:800])
                context_text = "\n\n".join(context_blocks)

                prior = self.get_chat_history(uid)
                history_text = "\n".join([f"사용자: {p['user']}\nAI: {p['assistant']}" for p in prior[-5:]])
                prompt = (
                    ("다음은 참고할 수 있는 문서 발췌입니다:\n" + context_text + "\n\n" if context_text else "")
                    + ("이전 대화:\n" + history_text + "\n\n" if history_text else "")
                    + f"사용자 질문: {question}\nAI 답변:"
                )

                if self.llm:
                    response = self.llm._call(prompt)
                else:
                    response = "죄송합니다. 로컬 LLM이 준비되지 않았습니다."

                sources = [s[:200] + "..." for s in context_blocks] if context_blocks else []
                has_rag = bool(context_blocks)

            # 최신 히스토리 저장
            hist = self.user_histories.get(uid, [])
            hist.append({"user": question, "assistant": response})
            self.user_histories[uid] = hist

            return {
                "response": response,
                "sources": sources,
                "has_rag": has_rag,
            }
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {str(e)}")
            return {
                "response": f"오류가 발생했습니다: {str(e)}",
                "sources": [],
                "has_rag": False
            }
    
    def get_chat_history(self, user_id: Optional[str] = None) -> List[Dict[str, str]]:
        """채팅 히스토리를 반환합니다 (사용자/세션 구분)."""
        try:
            uid = user_id or "anonymous"
            return self.user_histories.get(uid, [])
        except Exception as e:
            logger.error(f"채팅 히스토리 조회 중 오류 발생: {str(e)}")
            return []
    
    def clear_history(self, user_id: Optional[str] = None):
        """채팅 히스토리를 초기화합니다 (해당 사용자/세션만)."""
        try:
            uid = user_id or "anonymous"
            if uid in self.user_histories:
                del self.user_histories[uid]
            return True
        except Exception as e:
            logger.error(f"히스토리 초기화 중 오류 발생: {str(e)}")
            return False

# 전역 서비스 인스턴스 - 통합 서비스 우선 사용
try:
    chatbot_service = ChatbotAPIService()
    logger.info("통합 챗봇 서비스가 초기화되었습니다.")
except Exception as e:
    logger.error(f"통합 챗봇 서비스 초기화 실패, 기존 서비스 사용: {e}")
    chatbot_service = ChatbotService() 