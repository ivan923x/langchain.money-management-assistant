import time
import streamlit as st
from backend.core import run

# 初始化參數

session_list = [
    ("llm_model", "gpt-3.5-turbo"),
    ("chat_history", []),
    ("chat_input_disabled", False),
]
for session in session_list:
    if session[0] not in st.session_state:
        st.session_state[session[0]] = session[1]

# 介面渲染

st.set_page_config(page_title="記帳助理", layout="wide")

st.markdown(f"# 記帳助理")

chatbot_container = st.container()
with chatbot_container:

    def chat_input_disabled():
        st.session_state['chat_input_disabled'] = True

    chatbot = st.container(height=500)

    # 重新渲染所有訊息
    for message in st.session_state['chat_history']:
        with chatbot.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input(placeholder="傳送訊息給記帳助理", disabled=st.session_state['chat_input_disabled'], on_submit=chat_input_disabled):

        with chatbot.chat_message("user"):
            st.write(prompt)

        # with chatbot.chat_message("ai"), st.empty():
        with chatbot.chat_message("ai"):
            with st.spinner(""):
                response = st.write_stream(run(user_prompt=prompt, chat_history=st.session_state["chat_history"]))

        st.session_state['chat_history'].append({"role": "user", "content": prompt})
        st.session_state['chat_history'].append({"role": "ai", "content": response})

        st.session_state['chat_input_disabled'] = False
        st.rerun()