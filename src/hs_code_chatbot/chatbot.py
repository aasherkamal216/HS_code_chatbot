import os
import anthropic
from dotenv import load_dotenv

from prompt import SYSTEM_PROMPT
from typing import Generator

# --- Configuration ---
load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("MODEL_ANTHROPIC_API_KEYNAME"),
)


# --- Constants ---
MODEL_NAME = os.getenv("MODEL_NAME")
MAX_TOKENS_RESPONSE = 200
TEMPERATURE = 0.5

# --- Main Chatbot ---
def get_chatbot_response(conversation_history: list) -> Generator[str, None, None]:
    """
    Sends conversation history to Anthropic API and streams the response.
    
    Args:
        conversation_history: List of message dicts with 'role' and 'content'
        (should only contain 'user' and 'assistant' roles)
        
    Yields:
        str: Text chunks from the streaming response
    """
    try:
        # Filter out system messages (Anthropic handles system prompt separately)
        filtered_messages = [
            msg for msg in conversation_history 
            if msg["role"] in ("user", "assistant")
        ]
        
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS_RESPONSE,
            temperature=TEMPERATURE,
            system=SYSTEM_PROMPT, 
            messages=filtered_messages,
            stream=True
        )

        for chunk in response:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text

    except Exception as e:
        yield f"Sorry, I encountered an error: {str(e)}"