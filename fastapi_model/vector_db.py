from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name = "intfloat/multilingual-e5-large-instruct",model_kwargs={"device": "cuda"})


def Embedder(dir_path, store_name = "FAISS_INDEX")