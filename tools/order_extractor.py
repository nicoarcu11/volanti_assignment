import logging
from utils.openai_client import client
from models.schemas import OrderExtraction
from typing import List

logger = logging.getLogger(__name__)

def extract_order_id(chat_history: List[dict]) -> OrderExtraction:
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                    You are the order id extractor. Your task is to extract the order ID based on the conversation. 
                 
                    If there is not an order ID in the conversation, you should set the 'has_order_id' field to False and leave the 'order_id' field as None.
                 
                    If there is an order ID in the conversation, you should set the 'has_order_id' field to True and assign the order ID to the 'order_id' field.
                """},
            ] + chat_history,
            response_format=OrderExtraction,
        )
        result = completion.choices[0].message.parsed
        logger.info(f"Order Extraction: has_order_id={result.has_order_id}, order_id={result.order_id}")
        return result
    except Exception as e:
        logger.error(f"Error extracting order ID: {str(e)}")
        # Return a default extraction to prevent crashes
        return OrderExtraction(has_order_id=False, order_id=None)