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
    [전체관람가]
    음주·흡연: 음주나 흡연 장면이 없거나 매우 낮은 빈도로 묘사됨. 아동·청소년의 음주, 흡연 장면이 전혀 없으며, 성인의 음주, 흡연도 간헐적이고 조장되지 않음.
    약물: 불법 약물이나 향정신성 물질, 기타 유해물질의 오남용이나 사용법이 전혀 표현되지 않음. 합법적인 약물의 사용도 비판적이지 않으며, 그로 인한 일탈적 요소나 정당화된 내용이 없음.
    [12세이상관람가]
    음주·흡연: 음주나 흡연 장면이 짧고 경미하게 표현됨. 청소년의 음주는 낮은 수준으로 나타나고, 성인의 음주와 흡연은 간결하게 묘사됨. 음주나 흡연을 미화하거나 장려하는 내용은 제한적.
    약물: 합법적인 약물 사용은 일시적이고, 오남용이나 불법 약물의 사용 방법은 전혀 표현되지 않음. 약물이 일탈적이거나 정당화되는 장면은 없음.
    [15세이상관람가]
    음주·흡연: 음주와 흡연 장면이 반복적이지 않으며, 청소년의 음주나 흡연을 미화하거나 정당화하지 않음. 성인의 음주와 흡연 장면도 지속적이지 않으며, 음주로 인한 쾌락이나 중독 상태의 장면도 지속적으로 묘사되지 않음.
    약물: 합법적인 약물 사용이나 불법 약물의 사용이 현실도피나 쾌락을 위한 오남용으로 묘사되지 않음. 불법 약물의 제조나 사용 방법은 구체적이지 않으며, 약물로 인한 일탈 행위가 정당화되거나 미화되지 않음.
    [청소년관람불가]
    음주·흡연: 음주와 흡연 장면이 지속적이고 반복적으로 나타나며, 이를 통한 쾌락을 강하게 조장함. 청소년에게 유해한 영향을 미칠 수 있는 내용이 포함됨.
    약물: 불법 약물의 제조 및 사용 방법이 구체적이고 사실적으로 묘사되며, 약물의 오남용이 조장되거나 정당화되는 내용이 있음. 약물로 인한 범법행위나 폭력 등이 미화되고 정당화되는 경우도 발생함.
    """
    
    input_data = {
        "drug_img_summary": drug_img_data,
        "drug_text_summary": drug_text_data,
        "smoking_summary": smoking_data,
        "alcohol_summary": alcohol_data
    }
    
    prompt = (
        f"""다음은 약물 관련 콘텐츠에 대한 분류 기준과 제공된 요약 데이터를 기반으로 이 미디어에 적합한 연령 등급을 결정해 주세요.
        참고: 약물 관련 콘텐츠에서 마약(“마약”)에 대한 묘사는 알코올과 담배(흡연)보다 더 엄격하게 다뤄야 합니다.
        응답은 아래와 같은 구조의 JSON 형식으로 제공해 주세요.:
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

# # 예제 실행
# if __name__ == "__main__":
#     process_drug_rating(
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁2_drug_img_json.json",
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁_drug_text_json.json",
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁_smoking_json.json",
#         "/result/범죄와의전쟁/result_json/범죄와의전쟁_alcohol_json.json",
#         "/rating_test(drug)/범죄와의전쟁2(마약,담배,술)_drug_rating.json"
#     )
