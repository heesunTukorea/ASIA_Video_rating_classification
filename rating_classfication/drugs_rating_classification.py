import os
import json
from dotenv import load_dotenv
from openai import OpenAI

def load_env():
    """.env 파일에서 OpenAI API 키를 로드합니다."""
    load_dotenv()
    return os.getenv('OPENAI_API_KEY')

def initialize_openai_client(api_key):
    """제공된 API 키를 사용하여 OpenAI 클라이언트를 초기화합니다."""
    return OpenAI(api_key=api_key)

def analyze_drug_rating(openai_client, drug_img_data, drug_text_data, smoking_data, alcohol_data):
    """
    마약, 흡연, 음주 데이터를 분석하여 약물 관련 영상물 등급을 판별합니다.
    """
    rating_criteria = """
    Classifications for drug-related ratings:
    - All Ages: No or very low frequency depiction of drinking/smoking, no youth drinking/smoking, no direct or suggestive promotion, no depiction of illegal drug manufacturing/use.
    - 12+: Mild and brief depictions of drinking/smoking, low level youth drinking, no illegal drug depictions, no glorification of substance use.
    - 15+: Drinking/smoking is not continuous or glorified, illegal drugs are not shown in detailed or realistic ways, no justification of substance abuse.
    - Adults Only: Continuous and repeated depiction of drinking/smoking, detailed and realistic depiction of illegal drugs, glorification of substance abuse, depiction of illegal activities due to drugs.
    """
    
    input_data = {
        "drug_img_summary": drug_img_data,
        "drug_text_summary": drug_text_data,
        "smoking_summary": smoking_data,
        "alcohol_summary": alcohol_data
    }
    
    prompt = (
        f"""Based on the following classification criteria for drug-related content and the provided summary data, determine the appropriate age rating for this media.
        Provide the response strictly in JSON format with the following structure:
        {{
            \"rating\": \"관람 등급 (전체관람가, 12세이상관람가, 15세이상관람가, 청소년관람불가)\",
            \"reasoning\": \"한글로 간단한 설명 한 줄\"
        }}
        
        Criteria:
        {rating_criteria}
        
        Data Summary:
        {json.dumps(input_data, indent=4, ensure_ascii=False)}"""
    )
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    ai_response = response.choices[0].message.content
    ai_response = ai_response.replace("json","")
    ai_response = ai_response.replace("```","")
    return ai_response

def save_json_result(output_json_path, result):
    """결과를 JSON 파일로 저장합니다."""
    try:
        parsed_result = json.loads(result)
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(parsed_result, json_file, ensure_ascii=False, indent=4)
        print(f"분석 결과가 '{output_json_path}' 파일에 저장되었습니다.")
    except json.JSONDecodeError:
        print("JSON 디코딩 실패. 응답 내용:", result)

def process_drug_rating(drug_img_json, drug_text_json, smoking_json, alcohol_json, output_json_path):
    """약물 관련 영상물 등급 분석을 처리하는 메인 함수."""
    # API 키 로드
    openai_api_key = load_env()
    if not openai_api_key:
        raise ValueError(".env 파일에서 OpenAI API 키를 찾을 수 없습니다.")
    
    # OpenAI 클라이언트 초기화
    client = initialize_openai_client(openai_api_key)
    
    # JSON 데이터 로드
    with open(drug_img_json, "r", encoding="utf-8") as f:
        drug_img_data = json.load(f)["summary"]
    with open(drug_text_json, "r", encoding="utf-8") as f:
        drug_text_data = json.load(f) 
    with open(smoking_json, "r", encoding="utf-8") as f:
        smoking_data = json.load(f)[-1]  # 마지막 요소가 summary
    with open(alcohol_json, "r", encoding="utf-8") as f:
        alcohol_data = json.load(f)[-1]  # 마지막 요소가 summary
    
    # 분석 수행
    analysis_result = analyze_drug_rating(client, drug_img_data, drug_text_data, smoking_data, alcohol_data)
    
    # 결과 저장
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    save_json_result(output_json_path, analysis_result)

# 예제 실행
# if __name__ == "__main__":
#     process_drug_rating(
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁2_drug_img_json.json",
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁_drug_text_json.json",
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁_smoking_json.json",
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁_alcohol_json.json",
#         "/rating_test(drug)/범죄와의전쟁2(마약,담배,술)_drug_rating.json"
#     )
