## 한국어 프롬프트 
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

    data = json.dumps(json_data, ensure_ascii=False, indent=2)
    
    # 분류 기준
    rating_criteria = """
    다음은 영등위의 분류 기준 중 '주제'를 전체관람가, 12세이상 관람가, 15세이상 관람가, 청소년관람불가, 제한상영가 5가지 등급으로 나누는 각 기준이다.
    
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
    
    # 프롬프트 (JSON 데이터 입력 후 등급 판정)
    prompt = f"""    
    아래 제시한 데이터를 보고 분류 기준에 따라 영상물의 등급을 판정하고, 등급 판정의 이유를 출력하시오.
    반드시 아래 형식을 지켜서 json 형식으로 결과를 출력하시오:

    
    데이터 :
    {data}

    분류 기준 :
    {rating_criteria}

    형식 :
    {{
            \"rating\": \"관람 등급 (전체관람가, 12세이상관람가, 15세이상관람가, 청소년관람불가)\",
            \"reasoning\": \"한글로 간단한 설명 한 줄\"
        }}  

    """
    
    def get_chatgpt_response(prompt):
        """ 최신 OpenAI ChatGPT API 호출 """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "당신은 영상물 등급 분류 위원이다. 전문가로써 정확한 답변만 해야한다." },
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    # 함수 실행, 결과물을 JSON 파일 저장 (한글 출력 유지)
    response = get_chatgpt_response(prompt)
    response = response.replace("json","")
    response = response.replace("```","")
    parsed_result = json.loads(response)
    with open(result_file_path, "w", encoding="utf-8") as outfile:
        json.dump(parsed_result, outfile, ensure_ascii=False, indent=2)
    
    print(f"결과 저장 완료 : '{result_file_path}'")
    return parsed_result

# # 파일 로드 및 직접 실행
# json_file_path = "github_test_v5_total/result/인간중독/result_json/인간중독_topic_json.json"
# result_file_path = "github_test_v5_total/result/인간중독/rating_result/인간중독_topic_rating.json"
# classify_topic_rating(json_file_path, result_file_path)
