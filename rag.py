import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from schema import ChatRequest
from vector_store import search_vector_store
from dotenv import load_dotenv

load_dotenv()

# We need GROQ API Key to run. We use a placeholder string to avoid crashes, 
# but it will fail on invocation without a real key.
api_key = os.getenv("GROQ_API_KEY", "dummy_key")
llm = ChatGroq(model_name="groq/compound", temperature=0.5, groq_api_key=api_key)

# Basic dictionary session cache memory
chat_sessions = {}

def get_chat_history(session_id: str) -> str:
    history = chat_sessions.get(session_id, [])
    formatted_history = ""
    for msg in history[-10:]: # Restrict context length to last 10 turns
        formatted_history += f"{msg['role'].capitalize()}: {msg['content']}\n"
    return formatted_history

def add_to_history(session_id: str, role: str, content: str):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append({"role": role, "content": content})

def generate_summary(query: str, k: int = 5) -> str:
    docs = search_vector_store(query, k=k)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = PromptTemplate(
        input_variables=["query", "context"],
        template="""You are an AI assistant. Use the retrieved context to answer the question.
If the answer is not in the context, say so.

Context:
{context}

Question: {query}
Answer:"""
    )
    
    chain = prompt | llm
    return chain.invoke({"query": query, "context": context}).content

def chat_with_history(request: ChatRequest) -> str:
    docs = search_vector_store(request.query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    history = get_chat_history(request.session_id)
    
    prompt = PromptTemplate(
        input_variables=["query", "context", "history"],
        template="""You are a helpful AI assistant. Answer the user based on History and Context.

Conversation History:
{history}

Retrieved Context:
{context}

User Question: {query}
Answer:"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"query": request.query, "context": context, "history": history}).content
    
    add_to_history(request.session_id, "user", request.query)
    add_to_history(request.session_id, "assistant", response)
    
    return response
