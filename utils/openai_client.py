from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_query_embedding(query: str) -> list[float]:
    """
    Genera un embedding para la consulta del usuario usando OpenAI.
    
    :param query: La consulta de búsqueda del usuario.
    :return: Lista de floats que representan el embedding.
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        logger.info(f"Successfully generated embedding for query: {query[:30]}...")
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        # Return a zero vector of appropriate length as fallback
        return [0.0] * 1536  # Default dimension for text-embedding-ada-002