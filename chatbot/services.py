import os
import logging
from typing import List, Dict, Any, Optional
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
# from peft import PeftModel  # Not used here
from huggingface_hub import login


logger = logging.getLogger(__name__)
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
# 로그인 토큰이 있을 때만 허브 로그인 시도
if HUGGINGFACE_TOKEN:
    try:
        login(HUGGINGFACE_TOKEN)
    except Exception as _e:
        logger.warning("Hugging Face Hub 로그인 실패: %s", str(_e))

class CustomLLM(LLM):
    """커스텀 파인튜닝된 모델을 LangChain과 연동하는 클래스"""
    
    model: Any = None
    tokenizer: Any = None
    model_path: str = os.getenv("LOCAL_MODEL_PATH", "fine_tuned_model/merged_qwen")
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        if model_path:
            self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        """모델과 토크나이저를 로드합니다."""
        try:
            # 먼저 로컬 파인튜닝된 모델을 시도
            if os.path.exists(self.model_path):
                logger.info("로컬 파인튜닝된 모델을 로드합니다...")
                try:
                    # 로컬 모델에서 토크나이저 로드
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, auth_token=HUGGINGFACE_TOKEN)
                    if getattr(self.tokenizer, "pad_token", None) is None:
                        self.tokenizer.pad_token = getattr(self.tokenizer, "eos_token", None)
                    
                    # 로컬 모델 로드
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        torch_dtype=dtype,
                        trust_remote_code=True,
                        auth_token=HUGGINGFACE_TOKEN
                    )
                    self.model.to(device)
                    logger.info("로컬 파인튜닝된 모델이 성공적으로 로드되었습니다.")
                    return
                except Exception as e:
                    logger.warning(f"로컬 모델 로딩 실패: {str(e)}")
            

            logger.info("공개 모델을 로드합니다...")
            base_model_name = os.getenv("HF_BASE_MODEL", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B") 
            
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
            if getattr(self.tokenizer, "pad_token", None) is None:
                self.tokenizer.pad_token = getattr(self.tokenizer, "eos_token", None)
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            # 베이스 모델 로드
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=dtype,
                trust_remote_code=True
            )
            self.model.to(device)
            
            logger.info("공개 모델이 성공적으로 로드되었습니다.")
                
        except Exception as e:
            logger.error(f"모델 로딩 중 오류 발생: {str(e)}")
            # 모델 로딩 실패 시 더미 모델 생성
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """모델 로딩 실패 시 더미 모델을 생성합니다."""
        logger.warning("더미 모델을 생성합니다. 실제 AI 기능은 작동하지 않습니다.")
        self.model = None
        self.tokenizer = None
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        """모델을 사용하여 텍스트를 생성합니다."""
        if self.model is None or self.tokenizer is None:
            return "죄송합니다. AI 모델을 로드할 수 없습니다. 관리자에게 문의하세요."
        
        try:
            # 입력 텍스트를 토큰화
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # GPU로 이동 (가능한 경우)
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            
            # 모델로 텍스트 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=512,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 생성된 텍스트 디코딩
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 입력 프롬프트 제거하고 답변만 반환
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response if response else "죄송합니다. 답변을 생성할 수 없습니다."
            
        except Exception as e:
            logger.error(f"텍스트 생성 중 오류 발생: {str(e)}")
            return f"오류가 발생했습니다: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "custom_maplestory_llm"

class ChatbotService:
    """LangChain 기반 챗봇 서비스"""
    
    def __init__(self):
        try:
            self.llm = CustomLLM()
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            self.vectorstore = None
            self.qa_chain = None
            self._setup_rag()
        except Exception as e:
            logger.error(f"ChatbotService 초기화 중 오류: {str(e)}")
            # 기본 설정으로 초기화
            self.llm = None
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            self.vectorstore = None
            self.qa_chain = None
    
    def _setup_rag(self):
        """RAG 시스템을 설정합니다."""
        try:
            # 임베딩 모델 설정
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # 벡터 스토어 경로
            vectorstore_path = os.getenv("FAISS_INDEX_PATH", "MAI_db/indexex/faiss_index")
            
            if os.path.exists(vectorstore_path):
                # 기존 벡터 스토어 로드
                # allow_dangerous_deserialization=True는 신뢰된 로컬 파일만 대상으로 사용
                self.vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
                logger.info("기존 벡터 스토어를 로드했습니다.")
            else:
                # 새로운 벡터 스토어 생성
                self._create_vectorstore(embeddings)
            
            # RAG 체인 설정
            if self.vectorstore and self.llm:
                self.qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=True
                )
            
        except Exception as e:
            logger.error(f"RAG 설정 중 오류 발생: {str(e)}")
            # RAG 없이 기본 모델만 사용
            self.qa_chain = None
    
    def _create_vectorstore(self, embeddings):
        """벡터 스토어를 생성합니다."""
        try:
            # 데이터 로드 (MAI_db/json_data에서)
            data_path = os.getenv("RAG_DATA_PATH", "MAI_db/json_data")
            if os.path.exists(data_path):
                loader = DirectoryLoader(
                    data_path,
                    glob="**/*.json",
                    loader_cls=TextLoader
                )
                documents = loader.load()
                
                # 텍스트 분할
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                texts = text_splitter.split_documents(documents)
                
                # 벡터 스토어 생성
                self.vectorstore = FAISS.from_documents(texts, embeddings)
                
                # 벡터 스토어 저장
                # 인덱스 저장 경로 처리
                index_path = os.getenv("FAISS_INDEX_PATH", "MAI_db/indexex/faiss_index")
                os.makedirs(os.path.dirname(index_path), exist_ok=True)
                self.vectorstore.save_local(index_path)
                logger.info("새로운 벡터 스토어를 생성했습니다.")
            else:
                logger.warning("데이터 경로를 찾을 수 없습니다.")
                
        except Exception as e:
            logger.error(f"벡터 스토어 생성 중 오류 발생: {str(e)}")
    
    def get_response(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """질문에 대한 답변을 생성합니다."""
        try:
            if self.qa_chain:
                # RAG를 사용한 답변
                result = self.qa_chain({"question": question})
                response = result["answer"]
                source_documents = result.get("source_documents", [])
                
                return {
                    "response": response,
                    "sources": [doc.page_content[:200] + "..." for doc in source_documents],
                    "has_rag": True
                }
            elif self.llm:
                # 기본 모델만 사용
                response = self.llm._call(question)
                return {
                    "response": response,
                    "sources": [],
                    "has_rag": False
                }
            else:
                # 모델이 없는 경우 기본 응답
                return {
                    "response": "죄송합니다. AI 모델을 로드할 수 없습니다. 잠시 후 다시 시도해주세요.",
                    "sources": [],
                    "has_rag": False
                }
                
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {str(e)}")
            return {
                "response": f"오류가 발생했습니다: {str(e)}",
                "sources": [],
                "has_rag": False
            }
    
    def get_chat_history(self, user_id: Optional[str] = None) -> List[Dict[str, str]]:
        """채팅 히스토리를 반환합니다."""
        try:
            messages = self.memory.chat_memory.messages
            history = []
            
            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    history.append({
                        "user": messages[i].content,
                        "assistant": messages[i + 1].content
                    })
            
            return history
        except Exception as e:
            logger.error(f"채팅 히스토리 조회 중 오류 발생: {str(e)}")
            return []
    
    def clear_history(self, user_id: Optional[str] = None):
        """채팅 히스토리를 초기화합니다."""
        try:
            self.memory.clear()
            return True
        except Exception as e:
            logger.error(f"히스토리 초기화 중 오류 발생: {str(e)}")
            return False

# 전역 서비스 인스턴스
chatbot_service = ChatbotService() 