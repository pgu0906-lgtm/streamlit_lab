# pages/2_LibraryChatbot.py
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Library Chatbot", page_icon="📚")
st.title("3. 국립부경대학교 도서관 챗봇")

# --- API Key 확인 ---
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("먼저 메인 페이지에서 OpenAI API Key를 입력하세요.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# 🔽 여기 넣을 규정 텍스트는 네가 직접 복사해서 넣어야 함!
LIB_RULES_TEXT = """
여기에 국립부경대학교 도서관 규정 원문을 복사해서 넣으세요.
예: 휴관일, 개관시간, 대출 가능 도서 권수, 연체 규정 등.
"""

if not LIB_RULES_TEXT.strip():
    st.error("도서관 규정 텍스트를 넣어야 합니다!")
    st.stop()

# --- 대화 메모리 ---
if "lib_messages" not in st.session_state:
    st.session_state.lib_messages = []

# Clear 버튼
if st.button("대화 초기화"):
    st.session_state.lib_messages = []
    st.success("대화 기록이 초기화되었습니다.")

# 기존 메시지 표시
for msg in st.session_state.lib_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
if question := st.chat_input("도서관 규정에 대해 질문해보세요."):
    st.chat_message("user").markdown(question)
    st.session_state.lib_messages.append({"role": "user", "content": question})

    instructions = (
        "너는 국립부경대학교 도서관 규정 안내 챗봇이다. "
        "아래 규정 텍스트에 포함된 내용만 사용해서 답변해라. "
        "규정에 없는 내용은 모른다고 답해라.\n\n"
        "---[규정 시작]---\n"
        f"{LIB_RULES_TEXT}\n"
        "---[규정 끝]---"
    )

    with st.chat_message("assistant"):
        with st.spinner("규정을 분석하는 중..."):
            response = client.responses.create(
                model="gpt-5-mini",
                input=question,
                instructions=instructions
            )
            answer = response.output_text
            st.markdown(answer)

    st.session_state.lib_messages.append({"role": "assistant", "content": answer})
`
