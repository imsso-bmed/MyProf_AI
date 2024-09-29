import streamlit as st
import os
from openai import OpenAI
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# Streamlit 설정
st.set_page_config(page_title="Academic Writing Improvement AI", page_icon="📝")

def init_openai_client():
    """OpenAI 클라이언트를 초기화하고 반환합니다."""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API 키가 설정되지 않았습니다. Streamlit Secrets 또는 환경 변수를 확인해주세요.")
            st.stop()
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"OpenAI 클라이언트 초기화 중 오류가 발생했습니다: {str(e)}")
        logging.error(f"OpenAI 클라이언트 초기화 오류: {str(e)}")
        st.stop()

# OpenAI 클라이언트 초기화
client = init_openai_client()

# 파인튜닝된 모델 ID
MODEL_ID = st.secrets.get("MODEL_ID") or os.getenv("MODEL_ID")
if not MODEL_ID:
    st.error("MODEL_ID가 설정되지 않았습니다. Streamlit Secrets 또는 환경 변수를 확인해주세요.")
    st.stop()

@st.cache_data
def improve_text(text, language):
    """주어진 텍스트를 개선하고 피드백을 제공합니다."""
    try:
        system_message = (
            "You are an AI assistant specializing in improving academic writing. "
            f"Provide an improved version of the input text and feedback in {language}. "
            "Focus on enhancing clarity, coherence, and academic style. "
            "Your response should be in the following format:\n"
            "Improved version: [Your improved text here]\n"
            "Feedback: [Specific and constructive feedback, including explanations of the changes]"
        )
        
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Please improve this text and provide feedback: {text}"}
            ],
            max_tokens=1000
        )
        logging.info(f"OpenAI API Response: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except Exception as e:
        error_message = f"텍스트 개선 및 피드백 생성 중 오류가 발생했습니다: {str(e)}"
        if "model_not_found" in str(e):
            error_message += "\n모델 ID가 올바른지 확인하고, OpenAI 대시보드에서 모델 상태를 확인해주세요."
        elif "invalid_api_key" in str(e):
            error_message += "\nAPI 키가 올바른지 확인해주세요."
        st.error(error_message)
        logging.error(f"텍스트 개선 및 피드백 생성 오류: {str(e)}")
        return None

def parse_result(result):
    logging.info(f"Parsing result: {result}")
    improved_version = ""
    feedback = ""
    if "Improved version:" in result and "Feedback:" in result:
        parts = result.split("Feedback:", 1)
        improved_version = parts[0].replace("Improved version:", "").strip()
        feedback = parts[1].strip()
    elif "Improved version:" in result:
        improved_version = result.replace("Improved version:", "").strip()
    else:
        improved_version = result.strip()
    logging.info(f"Parsed improved version: {improved_version}")
    logging.info(f"Parsed feedback: {feedback}")
    return improved_version, feedback

def main():
    st.title("📝 Academic Writing Improvement AI")

    # 언어 선택 옵션
    language = st.selectbox(
        "Select language / 언어 선택",
        ("English", "한국어")
    )

    user_input = st.text_area("Enter the text you want to improve / 개선하고 싶은 텍스트를 입력하세요:", height=200)

    if st.button("Improve Text and Get Feedback / 텍스트 개선 및 피드백 받기"):
      if user_input:
        with st.spinner("Improving text and generating feedback / 텍스트 개선 및 피드백 생성 중..."):
            result = improve_text(user_input, language)
        if result:
            improved_version, feedback = parse_result(result)
            
            logging.info(f"Original text: {user_input}")
            logging.info(f"Improved version: {improved_version}")
            
            if improved_version.strip() == user_input.strip():
                st.warning("The model did not provide an improved version. Please try again or check the model settings.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📌 Original Text / 원본 텍스트:")
                    st.write(user_input)
                
                with col2:
                    st.subheader("📌 Improved Version / 개선된 버전:")
                    st.write(improved_version)
            
            if feedback:
                st.subheader("📌 Feedback / 피드백:")
                st.write(feedback)
            else:
                st.info("No specific feedback provided. / 구체적인 피드백이 제공되지 않았습니다.")
        else:
            st.error("Failed to get an improvement. Please try again.")
    else:
        st.warning("Please enter some text / 텍스트를 입력해주세요.")

    with st.sidebar:
        st.header("ℹ️ How to Use / 사용 방법")
        st.write("1. Select your preferred language.")
        st.write("2. Enter or paste the text you want to improve.")
        st.write("3. Click the 'Improve Text and Get Feedback' button.")
        st.write("4. Review the improved version and feedback.")
        
        st.header("🔒 Privacy / 개인정보 보호")
        st.write("Your input is used only for generating improvements and feedback, and is not stored.")
        
        st.header("ℹ️ Model Information / 모델 정보")
        st.write(f"Current model in use / 현재 사용 중인 모델: {MODEL_ID}")

if __name__ == "__main__":
    main()
