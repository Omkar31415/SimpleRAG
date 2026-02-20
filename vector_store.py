import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from database import SQLALCHEMY_DATABASE_URL
from dotenv import load_dotenv

load_dotenv()

# Replace psycopg2 with psycopg for langchain-postgres standard compatibility if needed, 
# but usually SQLalchemy URLs work directly.
vector_db_url = SQLALCHEMY_DATABASE_URL.replace("postgresql+psycopg2", "postgresql+psycopg")

# Initialize HuggingFace embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

collection_name = "news_vectors"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=vector_db_url,
    use_jsonb=True,
)

def add_to_vector_store(texts: list[str], metadatas: list[dict] = None) -> list[str]:
    """Adds texts to the vector store and returns their IDs."""
    return vector_store.add_texts(texts=texts, metadatas=metadatas)

def search_vector_store(query: str, k: int = 5):
    """Searches the vector store for similar texts."""
    return vector_store.similarity_search(query, k=k)
