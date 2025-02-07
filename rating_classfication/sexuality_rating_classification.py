### 한국어 프롬프트
import openai
import json
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def load_dialogue_texts(file_path):
    """ 파일에서 대사 텍스트를 한 줄씩 읽어 리스트로 반환 """
    with open(file_path, "r", encoding="utf-8") as f:
        texts = f.read().splitlines()
    return texts

# 등급판정 및 결과 저장 함수
def classify_sexuality_rating(input_img_path, input_text_path, output_file): 
    """ 이미지 분석 및 대사 데이터 기반 영상물 선정성 등급 판정 및 결과 저장 """
    result_folder_path = os.path.dirname(output_file)
    os.makedirs(result_folder_path, exist_ok=True)

    # 이미지 데이터 로드
    with open(input_img_path, "r", encoding="utf-8") as file:
        image_data = json.load(file)
    image_data_str = json.dumps(image_data, ensure_ascii=False, indent=2)

    # 대사 텍스트 로드
    dialogue_texts = load_dialogue_texts(input_text_path)
    dialogue_data_json = json.dumps({"dialogues": dialogue_texts}, ensure_ascii=False, indent=2) # 키 이름 변경: "dialogues"

    # 분류 기준 (기존과 동일)
    rating_criteria = """
    다음은 영등위의 분류 기준 중 '선정성'을 전체관람가, 12세이상관람가, 15세이상관람가, 청소년관람불가 5가지 등급으로 나누는 각 기준이다.
    - 전체관람가 : 선정정의 요소가 없거나 매우 약하게 표현된 것
    - 12세이상관람가 : 선정성의 요소가 경미하고 간결하게 표현된 것
    - 15세이상관람가 : 15세 이상 청소년이 사회, 가족, 학교 등에서 습득한 지식과 경험을 통하여 충분히 수용 가능한 것
    - 청소년관람불가 : 선정성의 요소가 과도하며, 그 표현 정도가 구체적이고 직접적이며 노골적인 것
    """

    # 프롬프트
    prompt = f'''
    아래 제시한 대사와 이미지 분석 데이터를 보고 분류 기준에 따라 영상물의 등급을 판정하고, 등급 판정의 이유를 출력하시오. 
    반드시 아래 형식을 지켜서 json 형식으로 결과를 출력하시오:

    대사 데이터(영상 내 선정적인 대사) :
     {dialogue_data_json}

    이미지 데이터 :
    {image_data_str}

    분류 기준 :
    {rating_criteria}

    형식 :
    {{
            \"rating\": \"관람 등급 (전체관람가, 12세이상관람가, 15세이상관람가, 청소년관람불가, 제한상영가)\",
            \"reasoning\": \"한글로 간단한 설명 한 줄\"
    }}  

    '''
    
    def get_chatgpt_response(prompt):
        """ 최신 OpenAI ChatGPT API 호출 """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "당신은 영상물 등급 분류 위원이다. 전문가로써 정확한 답변만 해야한다." },
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    # 함수 실행, 결과물을 JSON 파일 저장 
    response = get_chatgpt_response(prompt)
    response = response.replace("`json", "").replace("`", "")
    parsed_result = json.loads(response)
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(parsed_result, outfile, ensure_ascii=False, indent=2)
    
    print(f"결과 저장 완료 : '{output_file}'")
    return parsed_result

if __name__ == "__main__":
    base_name = "연애 빠진 로맨스" # 비디오 파일 이름 (확장자 제외)
    input_img_path = f'result/{base_name}/result_json/{base_name}_sexuality_img_json.json' # 이미지 데이터 JSON 파일 경로
    input_text_path = f'result/{base_name}/{base_name}_text_output/{base_name}_text.txt' # 대사 텍스트 파일 경로
    output_file = f'result/{base_name}/result_json/{base_name}_sexuality_rating_json.json' # 결과 파일 경로
    classify_sexuality_rating(input_img_path, input_text_path, output_file) # 함수 호출
