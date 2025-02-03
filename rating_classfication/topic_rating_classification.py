import openai
import json
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def classify_topic_rating(json_file_path, result_file_path):
    """ 주제 데이터를 분석하여 등급을 판정하고 결과를 저장 """
    result_folder_path = os.path.dirname(result_file_path)
    os.makedirs(result_folder_path, exist_ok=True)
    
    # JSON 파일 로드
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # 첫 번째 프롬프트 (분류 기준 학습)
    prompt_1 = """
    다음은 영등위의 분류 기준인 주제, 대사, 폭력성, 약물, 선정성, 공포, 모방위험 7가지 중, '주제'를 전체관람가, 12세이상 관람가, 15세이상 관람가, 청소년관람불가, 제한상영가 이렇게 5가지 등급으로 나누는 각 기준이다.
    <주제>
    - [전체관람가]
        - 사회나 가족의 긍정적 가치나 의미 등을 알려주고, 건전한 가징악적 결말 등을 통해 긍정적 가치를 최종적으로 확인하는 내용인 것(유·아동이 이해할 수 있는 가치관 형성에 도움을 주는 것
        - 아동에게 위협이나 위험을 느끼게 하는 유해한 내용이 없는 것
            - 사랑, 가족, 평화, 우정, 정의, 포용, 공존 등 보편적이고 윤리적인 가치를 명확히 다루는 것
            - 인간과 사회의 부정적인 면이 경미하게 표현되는 경우에는 권선 방식으로 표현될 것)
            - 아동 및 청소년에게 위협이 되는 내용이 없고 전 연령층이 수용 가능한 것
    - [12세이상관람가]
        - 범죄, 폭력, 청소년 비행, 사회의 부정적 현실이나 갈등 등을 다루고 있으나 청소년들의 인격 형성에 부정적인 영향을 미치지 않는 것
        - 12세 이상 청소년에게 위협이나 위험을 느끼게 하는 유해한 내용이 없는 것
            - 인간과 사회의 부정적인 면에 대한 표현을 비판적으로 이해하기 위해서는 12세 이상의 경험과 지식이 필요한 경우
            - 범죄, 폭력, 청소년 비행, 그 외 사회의 부정적 현실이나 갈등 등이 부분적으로 다뤄지고 있지만 청소년들의 인격 형성에 부정적인 영향을 미치지 않는 것
    - [15세이상관람가]
        - 범죄, 폭력, 청소년 비행, 성적 문란 등을 미화하거나 정당화하지 않는 것
        - 15세 이상 청소년에게 위협이나 위험을 느끼게 하는 유해한 내용이 없는 것
            - 청소년에게 유해한 내용이 표현될 수 있으나 그 정도가 높지 않고, 15세 이상의 청소년이 수용 가능한 것
            - 범죄, 폭력, 청소년 비행 등을 자극적으로 표현하거나 미화·정당화하지 않은 것
    - [청소년관람불가]
        - 청소년에게 유해한 영향을 끼칠 수 있는 자극적인 주제와 내용을 다룬 것
        - 일반적인 성인이 이해하고 수용할 수 있는 수준으로 사회적 질서를 지나치게 문란하게 하지 않는 것
            - 청소년에게 유해한 영향을 끼칠 수 있는 자극적인 주제와 내용을 다룬 것  
    """
    
    # 두 번째 프롬프트 (JSON 데이터 입력 후 등급 판정)
    prompt_2_template = """
    당신은 영상물 등급 분류 위원이다.
    영상의 '주제'에 해당하는 데이터를 보고 영상물의 등급과 등급 판정의 이유를 출력하시오.
    반드시 아래 형식을 지켜서 출력하시오오:

    최종 등급: [등급]
    등급 판정 이유: [한 문장으로 간단히 설명]

    데이터:
    {data}
    """
    
    def get_chatgpt_response(prompt):
        """ 최신 OpenAI ChatGPT API 호출 """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    def parse_rating_response(response):
        """ GPT 응답에서 최종 등급과 이유를 추출하는 함수 """
        rating, reason = "", ""
        for line in response.split("\n"):
            if "최종 등급:" in line:
                rating = line.replace("최종 등급:", "").strip()
            elif "등급 판정 이유:" in line:
                reason = line.replace("등급 판정 이유:", "").strip()
        return rating, reason
    
    # 1. ChatGPT에 '주제' 기준 학습시키기
    get_chatgpt_response(prompt_1)
    print("'주제' 기준 학습 완료")
    
    # 2. 등급 판정 요청
    topic_data = json.dumps(json_data, ensure_ascii=False, indent=2)
    prompt_2 = prompt_2_template.format(data=topic_data)
    rating_result = get_chatgpt_response(prompt_2)
    
    # 3. 결과 저장
    final_rating, rating_reason = parse_rating_response(rating_result)
    result_json = {
        "최종 등급": final_rating,
        "등급 판정 이유": rating_reason
    }
    
    # 4. 결과 JSON 파일 저장 (한글 출력 유지)
    with open(result_file_path, "w", encoding="utf-8") as outfile:
        json.dump(result_json, outfile, ensure_ascii=False, indent=2)
    
    print(f"결과 저장 완료 : '{result_file_path}'")
    return result_json
