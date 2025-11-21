import streamlit as st
from openai import OpenAI

st.title("2. Chat 페이지 (Responses API)")

# --- API Key ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input(
    "OpenAI API Key를 입력하세요 (필요시 다시 입력)",
    type="password",
    value=st.session_state.api_key,
)

if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input

if not st.session_state.api_key:
    st.warning("먼저 API Key를 입력하세요.")
    st.stop()


def get_client() -> OpenAI:
    return OpenAI(api_key=st.session_state.api_key)


# --- 대화 히스토리 ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # [{"role": "user"/"assistant", "content": "..."}, ...]


# 지금까지 대화 출력
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 입력창 + Clear 버튼
user_input = st.chat_input("메시지를 입력하세요")

col1, _ = st.columns([1, 1])
with col1:
    clear = st.button("🧹 Clear (대화 초기화)")

if clear:
    st.session_state.chat_history = []
    st.rerun()

if user_input:
    # 1) 유저 메시지 저장/표시
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    client = get_client()

    # 대화를 하나의 문자열로 합치기 (간단 버전)
    full_dialog = ""
    for m in st.session_state.chat_history:
        who = "사용자" if m["role"] == "user" else "챗봇"
        full_dialog += f"{who}: {m['content']}\n"

    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = client.responses.create(
                model="gpt-5-mini",
                input=[
                    {
                        "role": "user",
                        "content": (
                            "아래는 지금까지의 대화입니다.\n"
                            f"{full_dialog}\n\n"
                            "위 대화를 참고하여 마지막 사용자 메시지에 자연스럽게 한국어로 이어서 답변해 주세요."
                        ),
                    }
                ],
            )
            answer = response.output_text
            st.write(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
