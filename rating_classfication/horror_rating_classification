import json
import openai
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정
API_KEY = os.getenv("OPENAI_API_KEY")

# 최신 OpenAI API 클라이언트 사용
client = openai.Client(api_key=API_KEY)

# JSON 파일 로드 함수
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # JSON이 리스트 형식이면 첫 번째 요소 선택
    if isinstance(data, list):
        return data[0]  # 첫 번째 객체 선택
    return data  # 객체 그대로 반환

# JSON 데이터를 파일로 저장하는 함수
def save_json_raw(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)

# 등급판정 및 결과 저장 함수
def get_horror_rating(input_json_path, output_json_path):
    # JSON 데이터 불러오기
    data = load_json(input_json_path)

    # 필요한 데이터 추출
    total_scenes = data.get("total_scenes", "")
    horror_best_caption = data.get("horror_best_caption", "")
    non_horror = data.get("non-horror", "")
    horror_rate_true = data.get("horror_rate_true", "")
    horror_rate_false = data.get("horror_rate_false", "")

    # GPT 프롬프트 생성 (JSON 응답 강제)
    prompt = f"""
    다음은 영화의 장면 중 공포와 관련된 데이터야. 영상물등급위원회의 영상등급판정 기준에 따라 공포 부분 등급을 판정하고, 판정 근거를 1줄로 서술해.
    반드시 JSON 형식으로 출력하고, 코드 블록을 포함하지 말고 순수 JSON만 출력해. 키는 "rating"과 "reason" 두 개만 사용해야 해.
    - total_scenes: {total_scenes}
    - horror_best_caption: {horror_best_caption}
    - non-horror: {non_horror}
    - horror_rate_true: {horror_rate_true}
    - horror_rate_false: {horror_rate_false}

    출력 예시:
    {{
      "rating": "15세 이상 관람가",
      "reasoning": "공포 요소가 일부 포함되었으나 심각한 수준은 아님."
    }}
    """

    # OpenAI API 요청
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 영상 등급 분류 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    # GPT 응답 처리 (JSON 검증 없이 저장)
    result = response.choices[0].message.content

    # 응답이 비어 있는지 확인
    if result is None or result.strip() == "":
        print("❌ GPT 응답이 비어 있습니다. API 요청이 실패했을 가능성이 있습니다.")
        return

    print(f"✅ GPT 응답이 {output_json_path} 파일로 저장되었습니다.")
    print("✅ GPT 응답:", result)  # 응답 확인

    # JSON 파일로 저장 
    save_json_raw(result, output_json_path)

# # 함수 실행
# input_json_path = 'C:/Users/Administrator/movie/result/수리남/result_json/수리남_horror_json.json'
# output_json_path = 'C:/Users/Administrator/movie/rating/수리남_horror_rating.json'
# get_horror_rating(input_json_path, output_json_path)
