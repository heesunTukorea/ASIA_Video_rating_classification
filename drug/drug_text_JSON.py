import json

# 약물 관련 키워드 리스트 
drug_keywords = [" 약 ", "마약", "환각", "필로폰", "코카인", "대마", "헤로인", "펜타닐", "뽕", "코카", "아편", "캔디", "원료", "물건", "LSD", "PCP", "크리스탈", "크랭크", "던지기", ]

def load_textjson(file_path):
    """텍스트 파일을 읽고 문장을 리스트로 변환"""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        parsed_data = [{"text": line.strip()} for line in lines if line.strip()]  # 빈 줄 제거
    return parsed_data

def detect_drug_terms(text_data):
    """약물 관련 단어가 포함된 문장을 필터링"""
    including_drug = []  # 약물 관련 문장 저장
    total_sentences = len(text_data)  # 전체 문장 수
    
    for entry in text_data:
        sentence = entry["text"]
        if any(keyword in sentence for keyword in drug_keywords):  # 키워드 포함 여부 확인
            including_drug.append(sentence)

    # 일반 문장 수 계산
    non_drug_sentences = total_sentences - len(including_drug)

    # 결과 JSON 생성
    result_json = {
        "including_drug": including_drug,
        "summary": {
            "total_sentences": total_sentences,
            "drug_related_sentences": len(including_drug),
            "non_drug_sentences": non_drug_sentences
        }
    }
    return result_json

def save_to_json(result_json, output_path):
     #JSON 파일로 저장
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(result_json, json_file, ensure_ascii=False, indent=4)

def drug_text_main(input_file, output_file):

    text_data = load_textjson(input_file)
    result_json = detect_drug_terms(text_data)
    save_to_json(result_json, output_file)
    print(f"✅ 처리 완료! 결과가 {output_file}에 저장되었습니다.")

# # 실행 예시 (경로 수정)
# if __name__ == "__main__":
#     input_file = "/result/청설/청설_text_output/청설_text.txt"  # 입력 텍스트 파일 경로
#     output_file = "/result/청설/result_json/청설_drug_text_json.json"  # 출력 JSON 파일 저장 경로
#     drug_text_main(input_file, output_file)
