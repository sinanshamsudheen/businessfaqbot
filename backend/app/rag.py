import os
from .embeddings_provider import generate_text

def query_rag(question: str, faiss_store, top_k: int = 5):
    """Perform RAG query using FAISS and OpenAI with enhanced prompting"""
    # Retrieve relevant chunks from FAISS
    results = faiss_store.query(question, k=top_k)
    
    # Check if we have any relevant results
    if not results or len(results) == 0 or results[0]['score'] < 0.5:
        fallback_message = """Hey! 😊 That's a great question, and I want to make sure you get the most accurate and up-to-date information. 

While I don't have the specific details about that in my current knowledge base, I'd love to help you get the answers you need! Here's what I recommend:

• **Contact our amazing customer service team** - they're super knowledgeable and always ready to help
• **Visit our official website** for the latest information
• **Feel free to ask me about anything else** regarding Mi Lifestyle - I might have just the info you're looking for!

I'm here and excited to help with any other questions about our products, business opportunities, or company! What else would you like to know? 🌟"""
        return fallback_message, [], fallback_message
    
    # Build context from retrieved chunks
    context_parts = []
    for i, result in enumerate(results, 1):
        source = result['meta']['source']
        content = result['meta']['text'].strip()
        context_parts.append(f"[Document {i}: {source}]\n{content}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Enhanced system prompt for Mi Lifestyle FAQ assistant
    system_prompt = """You are a friendly and knowledgeable Mi Lifestyle representative who genuinely cares about helping people. You have a warm, approachable personality while maintaining professionalism that reflects the premium nature of Mi Lifestyle.

YOUR PERSONALITY:
• Warm, genuine, and enthusiastic about Mi Lifestyle
• Speak like a trusted friend who happens to be an expert
• Use casual yet professional language (you can use "you" instead of formal terms)
• Show genuine excitement about the opportunities and products
• Be encouraging and supportive, especially about business opportunities
• Make people feel valued and important

YOUR COMMUNICATION STYLE:
• Start responses warmly when appropriate
• Use friendly transitions like "Great question!", "I'm excited to share...", "You'll love this..."
• Be conversational but informative
• Share benefits with genuine enthusiasm
• Use "we" and "our" when talking about Mi Lifestyle to create inclusion
• End with encouraging notes or invitations for more questions

RESPONSE GUIDELINES:
• Always be helpful, accurate, and genuinely caring
• Make complex information easy to understand
• Highlight benefits and value propositions with authentic enthusiasm
• If you're unsure, be honest but still helpful and encouraging
• Focus on how Mi Lifestyle can positively impact their life
• Make every interaction feel premium and personalized

FORMATTING:
• Use **bold** for key benefits and important points
• Use bullet points (•) for easy-to-read lists
• Keep paragraphs conversational and well-spaced
• Structure information logically but naturally"""

    # Enhanced user prompt with Mi Lifestyle focus
    user_prompt = f"""Here's some valuable information about Mi Lifestyle that I can share with you:

{context}

Someone just asked: {question}

Please respond in a warm, friendly, and enthusiastic way that makes them feel valued and excited about Mi Lifestyle. Share the information naturally, like you're talking to a friend who you genuinely want to help succeed. Make sure to highlight the benefits and opportunities in an authentic, caring manner."""

    # Generate response using OpenAI with system prompt
    answer = generate_text(
        prompt=user_prompt, 
        system_prompt=system_prompt,
        max_tokens=800, 
        temperature=0.3
    )
    
    # Prepare sources information with better metadata
    sources = [
        {
            "source": result["meta"]["source"],
            "score": round(result["score"], 3),
            "chunk_id": result["meta"].get("chunk_id", 0)
        } 
        for result in results
    ]
    
    return answer, sources, answer