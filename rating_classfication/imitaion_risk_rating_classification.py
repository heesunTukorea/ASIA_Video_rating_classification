import openai
import json
from dotenv import load_dotenv
import os
# OpenAI API 키 설정
# .env 파일 로드


load_dotenv()

# 환경 변수 사용

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY



# GPT 호출 함수
def process_imitaion_rating(lines_data):


    # 사용자 메시지 생성
    user_message = [
        {"type": "text", "text": f"""
        
        Evaluate the given content based on the Korean Media Rating Board's "Imitable Behavior" classification.

        ### Rating Criteria:

        전체관람가:
        - No or minimal depiction of weapon use.
        - No or minimal portrayal of suicide, school violence, bullying, juvenile delinquency, or criminal methods.

        12세이상관람가:
        - Low-frequency and mild depiction of imitable dangerous acts.
        - Minimal portrayal of crime techniques or illegal actions.
        - Mild portrayal of weapons, suicide, or juvenile crimes.

        15세이상관람가:
        - Some depiction of dangerous acts but not detailed or persistent.
        - Crime techniques or illegal acts are not glorified or deeply explained.
        - Some portrayal of suicide, school violence, or crime but not detailed.

        청소년관람불가:
        - Realistic and detailed depiction of weapon use.
        - Explicit crime techniques or illegal acts that could be imitated.
        - Graphic portrayal of suicide, violence, or delinquent behavior.
        ### Task:
        Analyze the provided scene and classify it into one of the five categories.
        Return the result in JSON format:

        "rating": <one of ["전체관람가", "12세이상관람가", "15세이상관람가", "청소년관람불가"]>, "reasoning": "<brief reason in Korean>"

        Input:{lines_data}
        
        input_information:
        This is the data of medium and high imitating risk among the data extracted for context, risk behavior, and likelihood of imitating by extracting the image being transformed
        """},
    ]

    # GPT API 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": user_message}
        ],
        max_tokens=500
    )
    # print(f'응답 확인 : \n{response.choices[0].message.content}')
    result_text = response.choices[0].message.content
    result_text = result_text.replace("json","")
    result_text = result_text.replace("```","")
    json_result = json.loads(result_text)
    # 응답 결과 반환
    return json_result

# 입력 데이터를 처리하는 함수
def imitaion_risk_classify(input_file, output_file):
    """
    JSON 파일로부터 입력 데이터를 읽어와 GPT로 처리하고 결과를 JSON 파일로 저장합니다.
    """
    # 입력 데이터 읽기
    with open(input_file, "r", encoding="utf-8") as f:
        lines_data = json.load(f)
#     {
#     "strong_abusive_percentage": 17.95,
#     "weak_abusive_percentage": 7.69
# }
    summary_data=lines_data[-1]
    result = process_imitaion_rating(lines_data=summary_data)
    print(result)

    # 결과를 JSON 파일로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"Processing complete. Results saved to {output_file}")

if __name__ == "__main__":
    # 예제 실행 코드
    input_file = "result/스파이/result_json/스파이_imitation_json.json"  # 입력 이미지 폴더 경로
    output_file = "스파이_test1.json"  # 출력 폴더 경로
    imitaion_risk_classify(input_file, output_file)