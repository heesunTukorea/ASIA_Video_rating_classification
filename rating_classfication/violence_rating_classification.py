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

# 이미지 JSON 파일 로드 함수
def load_imgjson(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # JSON이 리스트 형식이면 마지막 요소 선택
    if isinstance(data, list):
        return data[-1]  # 마지막 객체 선택
    return data  # 객체 그대로 반환

# 대사 텍스트 파일을 JSON 형식 리스트로 반환 함수
def load_textjson(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        parsed_data = [{"text": line.strip()} for line in lines if line.strip()]  # 빈 줄 제거 후 저장
    return parsed_data

# JSON 데이터를 파일로 저장하는 함수
def save_json_raw(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4) 

# 등급판정 및 결과 저장 함수
def classify_violence_rating(input_img_path, input_text_path, result_json_path):
    # JSON 데이터 불러오기
    img_data = load_imgjson(input_img_path)
    text_data = load_textjson(input_text_path)

    # 필요한 데이터 추출
    violence_summary = img_data.get("summary", "")
    all_text = text_data

    img_summary_data = {"violence_summary" : violence_summary}

    img_json_data = {json.dumps(img_summary_data, ensure_ascii=False)}
    text_json_data = {json.dumps(all_text, ensure_ascii=False)}
    # GPT 프롬프트 생성
    rating_criteria = """
    다음은 영등위의 분류 기준 중 '폭력성'을 전체관람가, 12세이상관람가, 15세이상관람가, 청소년관람불가, 제한상영가 5가지 등급으로 나누는 각 기준이다.
    - 전체관람가 : 폭력성의 요소가 차지하는 비율이 낮고 경미하게 표현된 것 또는 폭력적인 장면이 없는 것
    - 12세이상관람가 : 폭력성의 요소가 존재하나 간결하게 표현된 것
    - 15세이상관람가 : 폭력성의 요소가 다소 존재하나 15세 이상 청소년이 사회, 가족, 학교 등에서 습득한 지식과 경험을 통하여 충분히 수용 가능한 것
    - 청소년관람불가 : 폭력성의 요소나 대사가 과도하며, 그 표현 정도가 구체적이고 직접적이며 노골적인 것
    
    """

    prompt = f"""
        
        아래 제시하는 대사데이터와 이미지데이터는 영화의 장면 중 폭력성과 관련된 데이터이다. 대사와 이미지를 종합해 아래에 제시하는 분류 기준과 영상물등급위원회의 기준에 따라 영상물의 등급을 판정하고, 등급 판정의 이유를 출력하시오.
        반드시 아래 형식을 지켜서 json 형식으로 결과를 출력하시오:

        대사 데이터 :
        {text_json_data}

        이미지 데이터 :
        {img_json_data}

        분류기준 : 
        {rating_criteria}

        형식 :
        {{
            "rating": "관람 등급 (전체관람가, 12세이상관람가, 15세이상관람가, 청소년관람불가, 제한상영가)",
            "reasoning": "한글로 간단한 설명"
        }}  
    """
    def get_chatgpt_response(prompt):
    #최신 OpenAI ChatGPT API 호출
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "당신은 영상물 등급 분류 위원이다. 전문가로써 정확한 답변만 해야한다." },
                    {"role": "user", "content": prompt}]
    )
        return response.choices[0].message.content.strip()

    # 함수 실행, 결과물을 JSON 파일 저장 
    response = get_chatgpt_response(prompt)
    response = response.replace("json","")
    response = response.replace("```","")
    parsed_result = json.loads(response)
    with open(result_json_path, "w", encoding="utf-8") as outfile:
        json.dump(parsed_result, outfile, ensure_ascii=False, indent=2)
    
    print(f"✅ GPT 응답이 {result_json_path} 파일로 저장되었습니다.")
    print("✅ GPT 응답:", response)
    return parsed_result

# # 함수 실행
# img_file_path = "input image json path"
# text_file_path = "input text txt path"
# result_file_path = "result save path"
# classify_violence_rating(img_file_path, text_file_path, result_file_path)
