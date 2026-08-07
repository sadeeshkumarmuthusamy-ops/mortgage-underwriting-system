
from langchain_community.vectorstores import Chroma

from src.config.settings import settings
import re


class DummyEmbeddings:
    """Fallback embeddings used when no OpenAI credentials are configured."""

    def embed_documents(self, texts):
        return [[0.0] * 3 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 3


def retrieve_relevant_policies(query):
    """
    Retrieve relevant policies from the policy store based on the query.

    Args:
        query: The query string to search for relevant policies.
    """
    # Implementation for retrieving relevant policies
    if not settings.OPENAI_API_KEY:
        embedding_function = DummyEmbeddings()
        print("⚠️ OPENAI_API_KEY is not configured. Using DummyEmbeddings for policy retrieval.")
    else:
        from langchain_openai import OpenAIEmbeddings

        embedding_function = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
        )

    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding_function,
    )

    docs = vectorstore.similarity_search(query, k=6)

    section_map = {}

    for doc in docs:
        text = doc.page_content.strip()

        # Extract section heading like "2.3 Self-Employment Income"
        match = re.match(r"^\d+\.\d+\s+[A-Za-z ].+", text)
        section = match.group(0) if match else "OTHER"

        if section not in section_map:
            section_map[section] = text
        else:
            # append only new content
            if text not in section_map[section]:
                section_map[section] += "\n" + text

    return "\n\n".join(section_map.values())