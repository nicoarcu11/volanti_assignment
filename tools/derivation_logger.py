import logging
from utils.openai_client import client
from models.schemas import DeriveToHumanExtraction
from typing import List

logger = logging.getLogger(__name__)

def log_derivation(chat_history: List[dict]) -> DeriveToHumanExtraction:
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                    You are the derivation logger. Your task is to log the reason for deriving the user's request to a human representative. 
                 
                    You should provide a reason for the derivation based on the conversation.
                 
                    For example, if the conversation is "Quiero comprar esto ahora", the reason could be "El usuario quiere realizar una compra".
                 
                    The reason should be concise and clear to help the human representative understand the context of the conversation. And it should be in Spanish.
                """}
            ] + chat_history,
            response_format=DeriveToHumanExtraction,
        )
        result = completion.choices[0].message.parsed
        logger.info(f"Derivation reason: {result.reason}")
        return result
    except Exception as e:
        logger.error(f"Error logging derivation: {str(e)}")
        # Return a default reason to prevent crashes
        return DeriveToHumanExtraction(reason="Error determining reason for derivation")