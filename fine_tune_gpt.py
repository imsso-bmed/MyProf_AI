import os
import time
from openai import OpenAI
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def prepare_training_data(original_folder, edited_folder):
    training_data = []
    for filename in os.listdir(original_folder):
        if filename.endswith('.txt'):
            original_path = os.path.join(original_folder, filename)
            edited_path = os.path.join(edited_folder, filename)
            
            if os.path.exists(edited_path):
                input_text = read_file_content(original_path)
                output_text = read_file_content(edited_path)
                training_data.append({"input": input_text, "output": output_text})
    
    return training_data

# 데이터 준비
original_folder = 'original'
edited_folder = 'edited'
training_data = prepare_training_data(original_folder, edited_folder)

# 데이터 포맷팅
def format_training_data(data):
    return [{"messages": [{"role": "user", "content": item["input"]},
                          {"role": "assistant", "content": item["output"]}]} for item in data]

formatted_data = format_training_data(training_data)

# 데이터를 JSONL 파일로 저장
with open("training_data.jsonl", "w", encoding='utf-8') as f:
    for entry in formatted_data:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")

# 파일 업로드
with open("training_data.jsonl", "rb") as f:
    file = client.files.create(file=f, purpose='fine-tune')

# 파인튜닝 작업 생성 및 실행
job = client.fine_tuning.jobs.create(training_file=file.id, model="gpt-3.5-turbo")

print("파인튜닝 작업이 시작되었습니다. 작업 ID:", job.id)

# 파인튜닝 작업 상태 확인 및 대기
while True:
    job_status = client.fine_tuning.jobs.retrieve(job.id)
    print(f"파인튜닝 작업 상태: {job_status.status}")
    
    if job_status.status == "succeeded":
        print("파인튜닝이 완료되었습니다!")
        fine_tuned_model_id = job_status.fine_tuned_model
        print(f"파인튜닝된 모델 ID: {fine_tuned_model_id}")
        break
    elif job_status.status == "failed":
        print("파인튜닝 작업이 실패했습니다.")
        break
    
    time.sleep(60)  # 1분마다 상태 확인

# 파인튜닝된 모델 사용
def use_fine_tuned_model(model_id, input_text):
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "당신은 논문 작성을 지도하는 경험 많은 교수입니다."},
            {"role": "user", "content": input_text}
        ]
    )
    return response.choices[0].message.content

# 파인튜닝이 성공적으로 완료된 경우에만 테스트 실행
if 'fine_tuned_model_id' in locals():
    test_input = "이 논문의 결론 부분을 검토해주세요."
    result = use_fine_tuned_model(fine_tuned_model_id, test_input)
    print(f"파인튜닝된 모델의 응답: {result}")
else:
    print("파인튜닝이 완료되지 않아 테스트를 건너뜁니다.")