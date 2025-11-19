# pages/3_ChatPDF.py
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="ChatPDF", page_icon="📄")
st.title("4. ChatPDF 페이지")

if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("먼저 메인 페이지에서 OpenAI API Key를 입력하세요.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# --- session_state 초기화 ---
if "pdf_vector_store_id" not in st.session_state:
    st.session_state.pdf_vector_store_id = None

if "pdf_messages" not in st.session_state:
    st.session_state.pdf_messages = []

# --- PDF 업로드 ---
uploaded_pdf = st.file_uploader("PDF 파일 업로드", type=["pdf"])

# Vector store 생성 버튼
if uploaded_pdf and st.button("PDF로 Vector Store 생성"):
    with st.spinner("PDF 인덱싱 중..."):
        vector_store = client.vector_stores.create(name="chatpdf-store")
        client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=[uploaded_pdf]
        )
        st.session_state.pdf_vector_store_id = vector_store.id
        st.success("Vector Store 생성 완료!")

# Vector Store 삭제
if st.button("Vector Store 삭제"):
    if st.session_state.pdf_vector_store_id:
        client.vector_stores.delete(
            vector_store_id=st.session_state.pdf_vector_store_id
        )
    st.session_state.pdf_vector_store_id = None
    st.session_state.pdf_messages = []
    st.success("삭제 완료!")

# 기존 메시지 표시
for msg in st.session_state.pdf_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 질문 입력
if st.session_state.pdf_vector_store_id:
    if question := st.chat_input("PDF 내용에 대해 질문하세요"):
        st.chat_message("user").markdown(question)
        st.session_state.pdf_messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("assistant"):
            with st.spinner("검색 중..."):
                response = client.responses.create(
                    model="gpt-5-mini",
                    input=question,
                    tools=[{
                        "type": "file_search",
                        "vector_store_ids": [st.session_state.pdf_vector_store_id],
                    }],
                    instructions=(
                        "PDF 내용에서만 답변해라. 근거 없는 내용은 모른다고 말하라."
                    ),
                )
                answer = response.output_text
                st.markdown(answer)

        st.session_state.pdf_messages.append(
            {"role": "assistant",
