import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Chat", page_icon="💬")
st.title("2. Chat 페이지")

if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("먼저 메인 페이지에서 OpenAI API Key를 입력하세요.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# --- 메시지 메모리 초기화 ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# --- Clear 버튼 ---
if st.button("Clear 대화"):
    st.session_state.chat_messages = []
    st.success("대화를 초기화했습니다.")

# --- 기존 메시지 출력 ---
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 사용자 입력 ---
if prompt := st.chat_input("메시지를 입력하세요"):
    # 사용자 메시지 화면 + 메모리 저장
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_messages.append(
        {"role": "user", "content": prompt}
    )

    # OpenAI로 기존 대화 모두 보내기 (간단 버전)
    openai_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            response = client.responses.create(
                model="gpt-5-mini",
                input=openai_messages,
            )
            answer = response.output_text
            st.markdown(answer)

    # 응답도 메모리에 저장
    st.session_state.chat_messages.append(
        {"role": "assistant", "content": answer}
    )
