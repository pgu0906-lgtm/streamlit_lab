import streamlit as st
from openai import OpenAI

st.title("3. 국립부경대학교 도서관 챗봇")

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


# 여기 문자열 안에 규정 텍스트를 그냥 복붙하면 됩니다.
LIB_RULES = """
여기에 '국립부경대학교 도서관 규정' 전문을 붙여넣으세요.
(규정 - 지원 및 부속시설 - 국립부경대학교 도서관 규정 부분)
예: 제1조(목적) ... 제2조(정의) ... 이런 식으로 전체 복사
"""

st.markdown("### 규정집 기반 도서관 챗봇")
st.write("이 챗봇은 **국립부경대학교 도서관 규정** 내용을 바탕으로만 답변합니다.")

if "lib_chat" not in st.session_state:
    st.session_state.lib_chat = []

for msg in st.session_state.lib_chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_q = st.chat_input("도서관에 대해 궁금한 점을 질문해 보세요. (예: 학부생 책 대여 권수?)")

col1, _ = st.columns([1, 1])
with col1:
    clear = st.button("🧹 Clear (대화 초기화)")

if clear:
    st.session_state.lib_chat = []
    st.rerun()

if user_q:
    st.session_state.lib_chat.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.write(user_q)

    client = get_client()

    system_prompt = (
        "당신은 국립부경대학교 도서관 규정을 잘 아는 도우미입니다.\n"
        "반드시 아래 규정(LIB_RULES) 내용에 근거해서만 대답해야 합니다.\n"
        "규정에서 찾을 수 없으면 '규정에 해당 내용이 없습니다.'라고 답하세요.\n"
    )

    with st.chat_message("assistant"):
        with st.spinner("규정을 확인하는 중..."):
            response = client.responses.create(
                model="gpt-5-mini",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "system", "content": f"[국립부경대학교 도서관 규정 전문]\n{LIB_RULES}"},
                    {"role": "user", "content": user_q},
                ],
            )
            answer = response.output_text
            st.write(answer)

    st.session_state.lib_chat.append({"role": "assistant", "content": answer})
