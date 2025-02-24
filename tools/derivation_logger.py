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
                 
                    For example, if the conversation is "I need help with my computer", you can log the reason as "Technical support required".
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