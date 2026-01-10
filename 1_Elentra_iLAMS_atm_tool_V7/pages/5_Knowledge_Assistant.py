# pages/5_Knowledge_Assistant.py
import sys, time
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
from chatbot.qa import KnowledgeAssistant

from core.theme import apply_ntu_purple_theme
from core.theme import apply_claude_theme
apply_ntu_purple_theme()
#apply_claude_theme()

st.set_page_config(page_title="Knowledge Assistant", page_icon="📚")
st.title("📚 Knowledge Assistant")
if st.button("🔄 Clear Knowledge Cache", type="secondary"):
    st.cache_resource.clear()
    st.success("Knowledge cache cleared. Reloading…")
    st.rerun()

# with st.sidebar:
#     # st.header("⚙️ Settings")

#     if st.button("🔄 Clear Knowledge Cache", type="primary"):
#         st.cache_resource.clear()
#         st.success("Knowledge cache cleared. Reloading…")
#         st.rerun()


@st.cache_resource
def init_assistant():
    return KnowledgeAssistant()

assistant = init_assistant()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Render chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            st.caption(msg["meta"])


user_input = st.text_input(
    "Ask a question about the knowledge base",
    placeholder="Type your question here..."
)
# with st.container():
#     st.header("Ask a question")
#     user_input = st.text_input("Question")


# # --- Chat input ---
# user_input = st.chat_input("Ask a question about the knowledge base")

if user_input:
    # 1️⃣ Show user message IMMEDIATELY
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # 2️⃣ Placeholder for assistant
    with st.chat_message("assistant"):
        thinking = st.empty()
        thinking.markdown("⏳ *Thinking…*")

        start = time.perf_counter()
        answer = assistant.answer(user_input)
        duration = time.perf_counter() - start

        thinking.empty()
        st.write(answer)

        # 3️⃣ Token estimation (simple + honest)
        approx_tokens = int(len(answer.split()) * 1.3)

        meta = f"⏱️ {duration:.2f}s · 🔢 ~{approx_tokens} tokens"

        st.caption(meta)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "meta": meta,
        }
    )
