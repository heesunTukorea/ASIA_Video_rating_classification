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
def process_lines_rating(lines_data):


    # 사용자 메시지 생성
    user_message = [
        {"type": "text", "text": f"""
        
        Evaluate the given dialogue based on the Korean Media Rating Board's criteria for age classification.
        ### Rating Criteria:

        전체관람가: 
        - No or minimal profanity, slang, or offensive language.
        - No violent, sexual, or discriminatory expressions.
        - No language harmful to children's linguistic habits.

        12세이상관람가: 
        - Light profanity or slang, used infrequently.
        - Mild violent or suggestive language, but not harmful to teenagers.
        - Minimal discriminatory expressions, brief and indirect insults.

        15세이상관람가: 
        - Moderate profanity, slang, or offensive language.
        - Insults or aggressive expressions, but not excessively repeated.
        - Some violent or suggestive dialogue, but not glorified.
        - Limited discriminatory or degrading remarks.

        청소년관람불가: 
        - Strong and repeated profanity, vulgar or derogatory language.
        - Repeatedly offensive, humiliating, or degrading expressions.
        - Explicitly violent or sexual dialogue.
        - Frequent discriminatory expressions.

        상영제한가:
        - Extreme profanity, sexually explicit or degrading speech.
        - Strongly discriminatory language harming human dignity.
        - Promotion of anti-social behavior or criminal acts.
        - Violation of democratic values or extreme hate speech.

        ### Task:
        Analyze the provided dialogue and classify the content into one of the five categories.
        Return the result in JSON format:

        "rating": <one of ["전체관람가", "12세이상관람가", "15세이상관람가", "청소년관람불가", "상영제한가"]>, "reasoning": "<brief reason in Korean>"

        Input:
        "dialogue":{lines_data}
        When you convert an image to one cut per second
        Strong_abusive_percent is the ratio of strong swear words
        Weak_abusive_percent is the rate of weak profanity
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
    print(f'응답 확인 : \n{response.choices[0].message.content}')
    result_text = response.choices[0].message.content
    result_text = result_text.replace("json","")
    result_text = result_text.replace("```","")
    json_result = json.loads(result_text)
    # 응답 결과 반환
    return json_result

# 입력 데이터를 처리하는 함수
def lines_classify(input_file, output_file):
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
    result = process_lines_rating(lines_data)
    print(result)

    # 결과를 JSON 파일로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"Processing complete. Results saved to {output_file}")

if __name__ == "__main__":
    # 예제 실행 코드
    input_file = "result/아저씨/result_json/아저씨_lines_json.json"  # 입력 이미지 폴더 경로
    output_file = "아저씨_test.json"  # 출력 폴더 경로
    lines_classify(input_file, output_file)