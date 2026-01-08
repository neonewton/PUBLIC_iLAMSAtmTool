# pages/5_Knowledge_Assistant.py
import sys
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
from core.chatbot.qa import KnowledgeAssistant

st.set_page_config(page_title="Knowledge Assistant", layout="wide")
st.title("📚 Knowledge Assistant")


@st.cache_resource
def init_assistant():
    return KnowledgeAssistant()


assistant = init_assistant()

if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


user_input = st.chat_input("Ask a question about the knowledge base")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("assistant"):
        answer = assistant.answer(user_input)
        st.write(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
