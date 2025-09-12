import os
from .embeddings_provider import generate_text

def query_rag(question: str, faiss_store, top_k: int = 5):
    """Perform RAG query using FAISS and OpenAI with enhanced prompting"""
    # Retrieve relevant chunks from FAISS
    results = faiss_store.query(question, k=top_k)
    
    # Debug: Print search results info
    print(f"Query: '{question}'")
    print(f"Found {len(results)} results")
    if results:
        print(f"Best score: {results[0]['score']:.3f}")
    
    # Much more lenient threshold based on actual score distribution
    if not results or len(results) == 0 or results[0]['score'] < 0.015:
        fallback_message = "I don't have that info. Try asking something else!"
        return fallback_message, [], fallback_message
    
    # Build context from retrieved chunks (limit to prevent token overflow)
    context_parts = []
    total_length = 0
    max_context_length = 3000  # Limit context to prevent token issues
    
    for i, result in enumerate(results, 1):
        source = result['meta']['source']
        content = result['meta']['text'].strip()
        chunk_text = f"[Document {i}: {source}]\n{content}"
        
        # Check if adding this chunk would exceed limit
        if total_length + len(chunk_text) > max_context_length:
            break
            
        context_parts.append(chunk_text)
        total_length += len(chunk_text)
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Simplified system prompt for better performance
    system_prompt = """You are a helpful Mi Lifestyle representative. Be friendly, direct, and informative.

COMMUNICATION STYLE:
• Be conversational and natural
• Give clear, specific answers
• Use casual but professional language  
• Be enthusiastic about Mi Lifestyle benefits
• Keep responses concise and focused

RESPONSE GUIDELINES:
• Answer directly without lengthy introductions
• Highlight key benefits and opportunities
• Use "we" and "our" when talking about Mi Lifestyle
• Be encouraging about business opportunities
• Focus on practical information

FORMATTING:
• Use **bold** for important points
• Use bullet points (•) for lists
• Keep responses well-structured but concise"""

    # Enhanced user prompt with Mi Lifestyle focus
    user_prompt = f"""Based on this Mi Lifestyle information:

{context}

Question: {question}

Provide a helpful, direct answer about Mi Lifestyle. Be friendly and enthusiastic but keep it concise and focused on what they asked."""

    # Generate response using OpenAI with system prompt
    answer = generate_text(
        prompt=user_prompt, 
        system_prompt=system_prompt,
        max_tokens=600,  # Reduced to prevent long responses
        temperature=0.3
    )
    
    # Prepare sources information with better metadata
    sources = [
        {
            "source": result["meta"]["source"],
            "score": round(result["score"], 3),
            "chunk_id": result["meta"].get("chunk_id", 0)
        } 
        for result in results[:3]  # Limit sources returned
    ]
    
    return answer, sources, answer