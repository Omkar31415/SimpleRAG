import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG News Chatbot", page_icon="📰", layout="wide")

st.title("📰 RAG News Chatbot")
st.markdown("Ask questions about the ingested news articles using the RAG backend.")

# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for actions
with st.sidebar:
    st.header("🗄️ Database Actions")
    
    st.subheader("Ingest Single News Item")
    title = st.text_input("Title")
    content = st.text_area("Content")
    if st.button("Ingest"):
        if title and content:
            with st.spinner("Ingesting..."):
                # Save to Relational DB
                db_resp = requests.post(f"{API_URL}/db/news", json={"title": title, "content": content})
                # Save to Vector DB
                vec_resp = requests.post(f"{API_URL}/vector/ingest", json={"title": title, "content": content})
                
                if db_resp.status_code == 200 and vec_resp.status_code == 200:
                    st.success("Successfully ingested into both databases!")
                else:
                    st.error("Failed to ingest.")
        else:
            st.warning("Please provide both title and content.")
            
    st.subheader("Clear Chat History")
    if st.button("Clear History"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.success("Chat history cleared!")

# Chat Interface
st.header("💬 Chat with News")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the news..."):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API for response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/rag/chat",
                    json={"session_id": st.session_state.session_id, "query": prompt}
                )
                if response.status_code == 200:
                    ans = response.json().get("response", "No response returned.")
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")
