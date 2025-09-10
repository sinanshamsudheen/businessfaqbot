import streamlit as st
import requests
import os
import time

# Configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")

# Page configuration
st.set_page_config(
    page_title="Mi Lifestyle FAQ Assistant",
    page_icon="🏢",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("🏢 Mi Lifestyle FAQ Assistant")
st.markdown("Your questions about Mi Lifestyle, answered instantly")

# Clear chat button in the main area
if len(st.session_state.messages) > 0:
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()

st.markdown("---")

# Display chat messages
if len(st.session_state.messages) == 0:
    # Welcome message from assistant
    with st.chat_message("assistant"):
        st.markdown("""Hey there, welcome to Mi Lifestyle! 👋

I'm here to help u regarding all ur doubts related to our company.

Feel free to ask me about anything!

**For example:** "What are the benefits of being our distributor?" """)
else:
    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about Mi Lifestyle products, services, or policies..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Send request to backend
            response = requests.post(
                f"{API_URL}/query",
                json={"question": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                full_response = data["answer"]
                
                # Simulate typing effect
                words = full_response.split()
                for i, word in enumerate(words):
                    current_text = " ".join(words[:i+1])
                    message_placeholder.markdown(current_text + "▌")
                    time.sleep(0.05)
                
                # Display final response
                message_placeholder.markdown(full_response)
            else:
                full_response = f"Error: {response.status_code} - {response.text}"
                message_placeholder.markdown(full_response)
                
        except Exception as e:
            full_response = f"Error: {str(e)}"
            message_placeholder.markdown(full_response)
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})