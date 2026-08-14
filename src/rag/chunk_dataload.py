from logging import log
from typing import Any
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config.settings import settings
from src.rag.ingestion import validate_and_load_pdf

def create_policy_store(documents: Any):
    """Create vector store with underwriting policies (loaded from PDF).

    Returns:
        ChromaDB vector store for policy retrieval
    """
    try:
        # Split policies into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        policy_chunks = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings(
            base_url=settings.OPENAI_API_BASE,
            model=settings.OPENAI_LLM_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        vectorstore = Chroma.from_documents(
            policy_chunks, embedding=embeddings, persist_directory="./chroma_db" 
        )
    except Exception as e:
        log.error(f"Error creating policy store: {e}")
        raise ValueError(f"Failed to create policy store: {e}") from e
    return vectorstore

def load_policy_store(url: str):
    """Load existing vector store with underwriting policies (from PDF).

    Returns:
        ChromaDB vector store for policy retrieval
    """
    try:
        documents = validate_and_load_pdf(url)
        vectorstore = create_policy_store(documents)
        log.info(f"Vector store created with {len(vectorstore)} policy chunks.")
    except Exception as e:
        log.error(f"Error loading policy store: {e}")
        raise ValueError(f"Failed to load policy store: {e}") from e
    return len(vectorstore)