import logging
from utils.openai_client import client
from models.schemas import ProductSearchExtraction
from typing import List

logger = logging.getLogger(__name__)

def extract_product_query(chat_history: List[dict]) -> ProductSearchExtraction:
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                    You are the search query generator. Your task is to generate a product search query based on the conversation. 
                 
                    If the conversation does not need a search query, you should set the 'needs_search' field to False and leave the 'query' field as None.
                 
                    If the conversation requires a search query (which it most likely does), you should set the 'needs_query' field to True and assign the search query to the 'query' field.
                 
                    For example, if the user says "Quiero comprar una lampara", the search query should be "lampara".
                 
                    If the user says "Quiero iluminar mi sala", the search query should be "iluminar sala".
                 
                    Your query will be used in a similarity search to find the most relevant products so only include the essential keywords.
                """},
            ] + chat_history,
            response_format=ProductSearchExtraction,
        )
        result = completion.choices[0].message.parsed
        logger.info(f"Product Search Extraction: needs_query={result.needs_query}, query={result.query}")
        return result
    except Exception as e:
        logger.error(f"Error extracting product query: {str(e)}")
        # Return a default extraction to prevent crashes
        return ProductSearchExtraction(needs_query=False, query=None)