import streamlit as st
from openai import OpenAI
import hashlib

st.set_page_config(page_title="Lab - Q&A", page_icon="🤖")

st.title("1. 단일 질문 → gpt-5-mini 응답")

# --- API Key를 session_state에 저장 ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",
    value=st.session_state.api_key,
)

if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input

if not st.session_state.api_key:
    st.warning("먼저 OpenAI API Key를 입력하세요.")
    st.stop()


def _hash_args(api_key: str, question: str) -> str:
    m = hashlib.sha256()
    m.update(api_key.encode("utf-8"))
    m.update(question.encode("utf-8"))
    return m.hexdigest()


@st.cache_data(show_spinner=True)
def ask_gpt_cached(key_hash: str, api_key: str, question: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-5-mini",
        input=question,
        instructions="당신은 친절한 한국어 튜터입니다. 가능한 한 쉽게 설명하세요.",
    )
    return response.output_text


question = st.text_input("질문을 입력하세요")

if st.button("질문 보내기"):
    if not question:
        st.warning("질문을 먼저 입력하세요.")
    else:
        with st.spinner("gpt-5-mini에게 물어보는 중..."):
            key_hash = _hash_args(st.session_state.api_key, question)
            answer = ask_gpt_cached(key_hash, st.session_state.api_key, question)

        st.subheader("모델 응답")
        st.write(answer)
