from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name = "intfloat/multilingual-e5-large-instruct",model_kwargs={"device": "cuda"})


def get_embedding(text):
    try:
        response = embeddings.embed_query(text)
        return response.data[0].embedding
    except Exception as e:
        print(f'임베딩 생성 중 오류 발생 : {e}')
        return None
    
