import os
import openai
from typing import List

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings for a list of texts using OpenAI's text-embedding-3-small model"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = openai.OpenAI(api_key=api_key)
    
    # Use the cost-effective text-embedding-3-small model
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            encoding_format="float"
        )
        embeddings.append(response.data[0].embedding)
    
    return embeddings

def generate_text(prompt: str, max_tokens: int = 1000, temperature: float = 0.7, system_prompt: str = None) -> str:
    """Generate text using OpenAI's GPT-4o-mini model (most cost-effective)"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = openai.OpenAI(api_key=api_key)
    
    # Prepare messages
    messages = []
    
    # If system_prompt is provided, use it; otherwise treat the prompt as both system and user
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
    else:
        # For backward compatibility, treat the entire prompt as user message
        messages.append({"role": "user", "content": prompt})
    
    # Use GPT-4o-mini which is the most cost-effective model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return response.choices[0].message.content