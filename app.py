import time
import streamlit as st
from backend.core import run_llm

# 初始化參數

# Sessions to be stored in Streamlit session state
# session_list: a list of tuples, each tuple contains a key and a value
session_list = [
    ("llm_model", "gpt-3.5-turbo"),
    # chat_history: a list of dictionaries, each dictionary contains the role and content of a message
    ("chat_history", []),
    ("chat_input_disabled", False),
]
# Initialize session state
for session in session_list:
    # session[0]: key, session[1]: value
    if session[0] not in st.session_state:
        st.session_state[session[0]] = session[1]

# 介面渲染

st.set_page_config(page_title="記帳助理", layout="wide")
# Render the title
st.markdown(f"# 記帳助理")

# Create a container.
# A container is a layout element that can hold other Streamlit elements, such as text, charts, and widgets.
chatbot_container = st.container()
with chatbot_container:

    def chat_input_disabled():
        """Disable the chat"""
        st.session_state["chat_input_disabled"] = True

    chatbot = st.container(height=500)

    # 重新渲染所有訊息
    # chat_history: a list of dictionaries, each dictionary contains the role and content of a message
    for message in st.session_state["chat_history"]:
        with chatbot.chat_message(message["role"]):
            st.write(message["content"])

    # Render the chat input and get the user input
    if prompt := st.chat_input(
        placeholder="傳送訊息給記帳助理",
        # chat_input_disabled: a boolean value indicating whether the chat input is disabled
        disabled=st.session_state["chat_input_disabled"],
        # on_submit: a callback function that is called when the user submits the chat input
        # Disable the chat input after the user submits the chat input
        on_submit=chat_input_disabled,
    ):
        # 印出使用者輸入的訊息
        with chatbot.chat_message("user"):
            st.write(prompt)

        # with chatbot.chat_message("ai"), st.empty():
        # 印出 AI 回應的訊息
        with chatbot.chat_message("ai"):
            # Show a loading spinner while the AI is generating a response
            with st.spinner(""):
                # Generate a response using the AI model
                response = st.write_stream(
                    # run: a function that generates a response using the AI model
                    run_llm(
                        user_prompt=prompt,
                        chat_history=st.session_state["chat_history"],
                    )
                )
        # 將對話紀錄加入 chat_history
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        st.session_state["chat_history"].append({"role": "ai", "content": response})
        # 允許使用者再次輸入
        st.session_state["chat_input_disabled"] = False
        # When st.rerun() is called, Streamlit effectively restarts the script, re-executing all the code from the beginning, which ensures that any changes in the data or state are reflected immediately in the app's interface.
        st.rerun()
