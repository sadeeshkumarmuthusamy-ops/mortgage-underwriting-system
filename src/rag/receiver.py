import logging as log
import re
from langchain_community.vectorstores import Chroma
from src.config.settings import settings

log.basicConfig(level=log.INFO)

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
    try:
        if not settings.OPENAI_API_KEY:
            embedding_function = DummyEmbeddings()
            log.info("OPENAI_API_KEY is not configured. Using DummyEmbeddings for policy retrieval.")
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
        if not docs:
            log.warning("No policy documents were found for query: %s", query)
            return "No policy documents were found for this underwriting query."

        section_map = {}

        for doc in docs:
            text = doc.page_content.strip()
            if not text:
                continue

            match = re.match(r"^\d+\.\d+\s+[A-Za-z ].+", text)
            section = match.group(0) if match else "OTHER"

            if section not in section_map:
                section_map[section] = text
            elif text not in section_map[section]:
                section_map[section] += "\n" + text

        if not section_map:
            return "No policy sections were extracted from the retrieved documents."

        return "\n\n".join(section_map.values())
    except Exception as exc:
        log.exception("Policy retrieval failed for query: %s", query)
        return (
            "Policy retrieval is temporarily unavailable. "
            f"Manual underwriting review is recommended. Error: {exc}"
        )