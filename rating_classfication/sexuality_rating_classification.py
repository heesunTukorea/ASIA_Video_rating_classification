### 한국어 프롬프트
import openai
import json
import os
from dotenv import load_dotenv
import re

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# 🔹 타임라인 제거 후 정제된 대사를 반환하는 함수 (파일 저장 없음)
def remove_timeline_from_text(input_file):
    """타임라인 제거 후 정제된 대사 리스트 반환"""
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    cleaned_lines = []
    for line in lines:
        # 정규 표현식을 사용하여 [00:00:00 - 00:00:00] 패턴 제거
        cleaned_text = re.sub(r"\[\d{2}:\d{2}:\d{2} - \d{2}:\d{2}:\d{2}\]\s*", "", line).strip()
        if cleaned_text:  # 빈 문자열이 아닐 경우만 추가
            cleaned_lines.append(cleaned_text)

    return cleaned_lines  # 🔹 파일 저장 없이 정제된 리스트 반환

# 등급판정 및 결과 저장 함수
def classify_sexuality_rating(input_img_path, input_text_path, output_file): 
    """ 이미지 분석 및 대사 데이터 기반 영상물 선정성 등급 판정 및 결과 저장 """
    result_folder_path = os.path.dirname(output_file)
    os.makedirs(result_folder_path, exist_ok=True)

    # 이미지 데이터 로드
    with open(input_img_path, "r", encoding="utf-8") as file:
        image_data = json.load(file)
        # JSON이 리스트 형식이면 마지막 요소 선택
        if isinstance(image_data, list):
            return image_data[-1]  # 마지막 객체 선택
        return image_data  # 객체 그대로 반환
    image_data_str = json.dumps(image_data, ensure_ascii=False, indent=2)

    # 대사 텍스트 로드
    dialogue_texts = remove_timeline_from_text(input_text_path)
    dialogue_data_json = json.dumps({"dialogues": dialogue_texts}, ensure_ascii=False, indent=2) # 키 이름 변경: "dialogues"

    # 분류 기준 (기존과 동일)
    rating_criteria = """
    <선정성>

    - [전체관람가]
        - 신체노출이 없거나 매우 약하게 표현된 것(자연스러운 신체의 부분노출 등은 전체 맥락을 고려하여 판단)
            - 일상생활에서 쉽게 경험하거나 자연스럽게 볼 수 있는 신체노출이 표현된 것
        - 일상생활에서 흔히 접할 수 있는 애정표현을 자연스럽게 표현한 것
            - 일상생활에서 쉽게 경험하거나 자연스럽게 볼 수 있는 애정표현이 표현된 것
        - 성적내용과 관련된 소리, 이미지, 언어 사용이 표현되지 않은 것
            - 성적인 내용을 암시하거나 이를 연상하게 하는 소리나 언어표현이 없는 것
    - [12세이상관람가]
        - 성적맥락과 무관한 신체노출이 간결하게 표현된 것(전쟁, 역사적 사건, 교육, 건강 등과 관련된 노출표현은 전체 맥락을 고려하여 판단)
            - 성적맥락 없는 신체노출이 간결하게 이루어진 것
        - 성적맥락과 관련된 신체노출이 가벼운 수준에서 표현되고, 성적접촉이 자극적이지 않은 것
            - 성적맥락에서 성적접촉 등을 암시하는 신체노출이 가벼운 수준으로 표현된 것
            - 선정적 몸짓 및 접촉 등이 간결한 수준인 것
        - 성적내용과 관련된 소리, 이미지, 언어 사용이 경미하고 간결하게 표현된 것
            - 성적접촉 등을 암시하거나 이를 연상하게 하는 언어표현이 간결하게 표현된 것
            - 영상 속에서의 사진, 그림 등 2차적 이미지에서의 선정적 표현이 간결한 것
    - [15세이상관람가]
        - 성적맥락과 무관한 신체노출은 자극적으로 표현되지 않아야 하며, 전체 맥락상 타당하게 표현된 것(전쟁, 역사적 사건, 교육, 건강 등에서의 노출표현은 전체 맥락을 고려하여 판단)
            - 성적맥락 없는 전신노출 등이 표현될 수 있으나 노골적이지 않은 것
        - 성적맥락과 관련된 신체노출은 특정 부위를 선정적으로 강조하지 않아야 하며, 성적행위는 구체적이고 지속적이지 않은 것
            - 성적맥락과 관련된 노출에서 상반신 및 옆·뒷면의 전신노출은 있을 수 있으나, 특정 부위(가슴, 엉덩이 등을 말하며 성기는 허용하지 않음)를 강조하지 않은 것
            - 성적행위를 나타내는 장면 혹은 성행위를 암시하는 장면 묘사가 구체적이고 지속적으로 표현되지 않은 것
            - 애무, 자위행위, 유사성행위가 구체적으로 표현되지 않고 신체 특정 부위를 선정적으로 강조하지 않을 것
        - 성적내용과 관련된 소리, 이미지, 언어 사용이 자극적으로 표현되지 않은 것
            - 성적행위, 성관계 등을 연상하게 하는 언어표현이 구체적이지 않은 것
        - 일반적인 사회윤리에 어긋나는 성적행위(예: 근친상간, 혼음 등)가 없으며 청소년으로 하여금 왜곡된 성적관념을 갖게 하지 않는 것
            - 사회윤리에 반하는 성행위가 없으며 암시적으로 묘사된 것(예: 근친상간, 다자간 성행위 등)
    - [청소년관람불가]
        - 성적맥락과 관련된 신체노출이 직접적으로 표현되어 있으나 성기 등을 강조하여 지속적으로 노출하지 않은 것
            - 신체 특정 부위의 노출이 확대되거나 직접적이고, 전신노출 등이 빈번하게 묘사된 것
        - 성적행위가 구체적이고 지속적이며 노골적으로 표현된 것
            - 성행위가 구체적이고 노골적으로 표현될 수 있으나 성기확대, 삽입 등 실제 성행위의 구체적인 묘사는 허용되지 않음
            - 신체의 일부 또는 성기구 등을 이용한 자위행위 등을 구체적으로 표현한 것
        - 성적내용과 관련된 소리, 이미지, 언어 사용이 직접적이고 자극적으로 표현된 것
            - 성적행위, 성관계 등을 암시하거나 이를 연상하게 하는 소리, 이미지, 언어표현이 직접적인 것
        - 일반적인 사회윤리에 어긋나는 성적행위(예: 근친상간, 혼음 등)가 표현되어 청소년의 성적수치심과 혐오감을 유발하는 것
            - 수간, 시간, 소아성애 등 일반적인 사회윤리에 어긋나는 성적행위 등의 표현이 없을 것
            - 아동, 청소년을 성적도구 또는 학대의 대상으로 자극적으로 묘사하지 않은 것
    """

    # 프롬프트
    prompt = f'''
    아래 제시한 대사와 이미지 분석 데이터를 보고 오직 선정성 분류 기준에 따라 영상물의 선정성 등급을 판정하고, 등급 판정의 이유를 출력하시오.
    문맥을 고려하여 판정하시오.
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

# if __name__ == "__main__":
#     base_name = "겨울왕국" # 비디오 파일 이름 (확장자 제외)
#     input_img_path = '/result_json/겨울왕국_sexuality_img_json.json' # 이미지 데이터 JSON 파일 경로
#     input_text_path = '/result/겨울왕국/겨울왕국_text_output/겨울왕국_text.txt' # 대사 텍스트 파일 경로
#     output_file = '/result/테스트테스트.json' # 결과 파일 경로
#     classify_sexuality_rating(input_img_path, input_text_path, output_file) # 함수 호출
