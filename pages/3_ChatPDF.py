import streamlit as st
from openai import OpenAI

st.title("4. ChatPDF - PDF로 대화하기")

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


client = get_client()

if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None
if "uploaded_pdf_name" not in st.session_state:
    st.session_state.uploaded_pdf_name = None

st.markdown("### 1) PDF 파일 업로드")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

col1, col2 = st.columns([1, 1])
with col1:
    create_vs = st.button("📥 Vector Store 생성/갱신")
with col2:
    clear_vs = st.button("🧹 Clear (Vector Store 삭제)")


if create_vs:
    if not uploaded_file:
        st.warning("먼저 PDF 파일을 업로드하세요.")
    else:
        with st.spinner("Vector Store 생성 중... (PDF 임베딩)"):
            vs = client.vector_stores.create(name="chatpdf_vector_store")

            file_batch = client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vs.id,
                files=[uploaded_file],
            )

            st.session_state.vector_store_id = vs.id
            st.session_state.uploaded_pdf_name = uploaded_file.name

        st.success(f"Vector Store 생성 완료! (파일: {uploaded_file.name})")


if clear_vs and st.session_state.vector_store_id is not None:
    with st.spinner("Vector Store 삭제 중..."):
        client.vector_stores.delete(st.session_state.vector_store_id)
    st.session_state.vector_store_id = None
    st.session_state.uploaded_pdf_name = None
    st.success("Vector Store가 삭제되었습니다.")

if st.session_state.vector_store_id:
    st.info(
        f"현재 Vector Store ID: {st.session_state.vector_store_id}\n"
        f"업로드된 파일: {st.session_state.uploaded_pdf_name}"
    )
else:
    st.info("현재 활성화된 Vector Store가 없습니다. PDF를 업로드하고 Vector Store를 생성하세요.")

st.markdown("### 2) PDF 내용으로 질의응답")

question = st.text_input("PDF 내용에 대해 질문을 입력하세요")

if st.button("질문하기"):
    if not st.session_state.vector_store_id:
        st.warning("먼저 PDF를 업로드하고 Vector Store를 생성하세요.")
    elif not question:
        st.warning("질문을 입력하세요.")
    else:
        with st.spinner("PDF 내용을 검색하고 답변 생성 중..."):
            response = client.responses.create(
                model="gpt-5-mini",
                input=question,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [st.session_state.vector_store_id],
                        "max_num_results": 10,
                    }
                ],
            )
            answer = response.output_text

        st.subheader("모델 응답")
        st.write(answer)
