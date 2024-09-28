from docx import Document
import difflib
import re
import os



print("현재 작업 디렉토리:", os.getcwd())

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return ' '.join([para.text for para in doc.paragraphs])

def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

def save_sentences_to_files(sentences, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for i, sentence in enumerate(sentences, 1):
        file_path = os.path.join(folder, f'text{i}.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sentence)

def compare_documents(original_path, edited_path, original_folder, start_count, edited_folder):
    change_count = int(start_count)
    
    # 텍스트 추출
    original_text = extract_text_from_docx(original_path)
    edited_text = extract_text_from_docx(edited_path)

    # 문장으로 분리
    original_sentences = split_into_sentences(original_text)
    edited_sentences = split_into_sentences(edited_text)

    # 수정된 문장 찾기
    matcher = difflib.SequenceMatcher(None, original_sentences, edited_sentences)
    
    

    # 폴더 생성
    if not os.path.exists(original_folder):
        os.makedirs(original_folder)
    if not os.path.exists(edited_folder):
        os.makedirs(edited_folder)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':  # 수정된 문장만 처리
            for i, j in zip(range(i1, i2), range(j1, j2)):
                original = original_sentences[i].strip()
                edited = edited_sentences[j].strip()
                
                # 원본 문장 저장
                with open(os.path.join(original_folder, f'text{change_count}.txt'), 'w', encoding='utf-8') as f:
                    f.write(original)
                
                # 수정된 문장 저장
                with open(os.path.join(edited_folder, f'text{change_count}.txt'), 'w', encoding='utf-8') as f:
                    f.write(edited)

                change_count += 1

    return change_count - int(start_count)

def process_multiple_documents(file_pairs, original_folder, edited_folder):
    if not os.path.exists(original_folder):
        os.makedirs(original_folder)
    if not os.path.exists(edited_folder):
        os.makedirs(edited_folder)

    total_changes = 0
    start_count = 1  # 정수로 초기화

    for original_file, edited_file in file_pairs:
        changes = compare_documents(original_file, edited_file, original_folder, start_count, edited_folder)
        total_changes += changes
        start_count += changes
        print(f"처리 완료: {original_file} - {edited_file}")

    print(f"총 {total_changes}개의 수정된 문장 쌍이 저장되었습니다.")
    print(f"원본 문장: {original_folder}")
    print(f"수정된 문장: {edited_folder}")

# 사용 예시
base_path = r'C:\Users\ABC\Desktop\Lucas_AI\feedback_data'
file_pairs = [
    (os.path.join(base_path, '1-before.docx'), os.path.join(base_path, '1-after.docx')),
    (os.path.join(base_path, '2-before.docx'), os.path.join(base_path, '2-after.docx')),
    (os.path.join(base_path, '3-before.docx'), os.path.join(base_path, '3-after.docx')),
    (os.path.join(base_path, '4-before.docx'), os.path.join(base_path, '4-after.docx'))
]
original_folder = 'original'
edited_folder = 'edited'

process_multiple_documents(file_pairs, original_folder, edited_folder)