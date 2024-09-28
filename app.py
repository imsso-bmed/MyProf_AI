import streamlit as st
import os
from openai import OpenAI

# Streamlit Cloud에서는 .env 파일을 사용하지 않으므로 조건부로 import
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Streamlit Cloud에서는 이 부분을 무시합니다

from openai import OpenAI

# Streamlit 설정
st.set_page_config(page_title="Academic Writing Feedback AI", page_icon="📝")

# API 키 설정 (Streamlit Cloud에서는 st.secrets 사용)
api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 파인튜닝된 모델 ID
MODEL_ID = st.secrets.get("MODEL_ID", "ft:gpt-3.5-turbo-0613:your-org:your-model-name:your-version")

@st.cache_data
def get_feedback(text, language):
    try:
        system_message = (
            "You are an experienced professor providing feedback on academic writing. "
            f"Provide specific and constructive feedback in {language}. "
            "Focus on improving the structure, argumentation, and use of evidence in the text."
        )
        
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Please review the following text and suggest improvements: {text}"}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while generating feedback: {str(e)}")
        return None

st.title("📝 Academic Writing Feedback AI")

# 언어 선택 옵션
language = st.selectbox(
    "Select feedback language / 피드백 언어 선택",
    ("English", "한국어")
)

user_input = st.text_area("Enter the text you want feedback on / 피드백을 받고 싶은 텍스트를 입력하세요:", height=200)

if st.button("Get Feedback / 피드백 받기"):
    if user_input:
        with st.spinner("Generating feedback / 피드백을 생성 중입니다..."):
            feedback = get_feedback(user_input, language)
        if feedback:
            st.subheader("📌 Feedback / 피드백:")
            st.write(feedback)
    else:
        st.warning("Please enter some text / 텍스트를 입력해주세요.")

with st.sidebar:
    st.header("ℹ️ How to Use / 사용 방법")
    st.write("1. Select your preferred feedback language.")
    st.write("2. Enter or paste the text you want feedback on.")
    st.write("3. Click the 'Get Feedback' button.")
    st.write("4. Review the AI-generated professor-style feedback.")
    
    st.header("🔒 Privacy / 개인정보 보호")
    st.write("Your input is used only for generating feedback and is not stored.")
    
    st.header("ℹ️ Model Information / 모델 정보")
    st.write(f"Current model in use / 현재 사용 중인 모델: {MODEL_ID}")