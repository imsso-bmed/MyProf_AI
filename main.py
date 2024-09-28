import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# API 호출 예시
response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "당신은 논문 작성을 지도하는 경험이 많은 교수입니다."},
        {"role": "user", "content": "다음 텍스트를 검토하고 개선사항을 제안해주세요: [테스트 텍스트]"}
    ]
)

print(response.choices[0].message.content)
