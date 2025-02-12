import os
from dotenv import load_dotenv
from openai import OpenAI
import json

def load_env():
    """.env 파일에서 OpenAI API 키를 로드합니다."""
    load_dotenv()
    return os.getenv('OPENAI_API_KEY')

def initialize_openai_client(api_key):
    """제공된 API 키를 사용하여 OpenAI 클라이언트를 초기화합니다."""
    return OpenAI(api_key=api_key)

def load_generated_text(file_path):
    """생성된 텍스트 파일을 읽어 문자열로 반환합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"텍스트 파일을 찾을 수 없습니다: {file_path}")

def analyze_metadata_and_script(openai_client, metadata, script):
    """
    메타데이터와 대사를 분석하여 키워드, 설명, 표현 방식, 메시지 전달 의도,
    장르적 특성을 JSON 형식으로 추출합니다.
    """
    prompt = (
        f"다음 메타데이터와 대사를 분석해서 JSON 형식으로 결과를 출력해줘. 반드시 아래 형식을 유지해야 해."
        "\n\n"
        "{"
        "    \"keywords\": ["
        "        {\"keyword\": \"키워드1\", \"description\": \"키워드1에 대한 설명\"},"
        "        {\"keyword\": \"키워드2\", \"description\": \"키워드2에 대한 설명\"},"
        "        {\"keyword\": \"키워드3\", \"description\": \"키워드3에 대한 설명\"}"
        "    ],"
        "    \"overallDescription\": {"
        "        \"expression\": \"작품의 표현 방식 설명\","
        "        \"intention\": \"작품의 메시지 전달 의도 설명\","
        "        \"genreSpecificFeatures\": \"장르적 특성 설명\""
        "    }"
        "}"
        "\n\n"
        f"메타데이터:\n{json.dumps(metadata, ensure_ascii=False, indent=4)}\n\n"
        f"대사:\n{script}"
    )

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    ai_response = response.choices[0].message.content
    ai_response = ai_response.replace("json","")
    ai_response = ai_response.replace("```","")
    return ai_response

def parse_analysis_result(result):
    """결과를 JSON 형식으로 변환하며, 변환 실패 시 오류를 처리합니다."""
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        print("JSON 디코딩 실패. 응답 내용:", result)
        return None

def process_topic(text_output_path, output_json_path, title, synopsis, genre):
    """메타데이터 및 대사 분석을 처리하는 메인 함수."""
    # API 키 로드
    openai_api_key = load_env()
    if not openai_api_key:
        raise ValueError(".env 파일에서 OpenAI API 키를 찾을 수 없습니다.")

    # OpenAI 클라이언트 초기화
    client = initialize_openai_client(openai_api_key)

    # 생성된 텍스트 파일 경로 설정
    text_output_path = text_output_path

    # 저장된 텍스트 파일 읽기
    try:
        script = load_generated_text(text_output_path)
        print(f"텍스트 파일에서 내용을 성공적으로 읽었습니다: {text_output_path}")
    except FileNotFoundError as e:
        print(e)
        return

    # 메타데이터 구성
    metadata = {
        "title": title,
        "synopsis": synopsis,
        "genre": genre
    }

    # 메타데이터와 대사 분석
    analysis_result = analyze_metadata_and_script(client, metadata, script)

    # 결과를 JSON 형식으로 변환
    analysis_json = parse_analysis_result(analysis_result)
    if analysis_json:
        # 결과를 JSON 파일로 저장
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(analysis_json, json_file, ensure_ascii=False, indent=4)
        print(f"분석 결과가 '{output_json_path}' 파일에 저장되었습니다.")

def filter_topic(json_path):
    """분석된 JSON 파일을 읽고 특정 형식으로 변환합니다."""
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            analysis_json = json.load(file)
    except FileNotFoundError:
        return "파일을 찾을 수 없습니다."
    except json.JSONDecodeError:
        return "JSON 파일을 디코딩할 수 없습니다."
    
    topic_str = "주제 키워드 3개와 설명\n"
    for keyword_data in analysis_json.get("keywords", []):
        topic_str += f"{keyword_data['keyword']} : {keyword_data['description']}\n"
    
    topic_str += "\n전반적 설명\n"
    overall_desc = analysis_json.get("overallDescription", {})
    topic_str += f"작품의 표현 방식 : {overall_desc.get('expression', '없음')}\n"
    topic_str += f"메시지 전달 의도 : {overall_desc.get('intention', '없음')}\n"
    topic_str += f"장르적 특성 : {overall_desc.get('genreSpecificFeatures', '없음')}\n"
    
    return topic_str

# if __name__ == "__main__":
#     process_topic(
#     text_output_path='result\마스크걸\마스크걸_text_output\마스크걸_text.txt',
#     output_json_path='topic/topicJSON.json',  # 파일 확장자 추가 및 슬래시로 경로 수정
#     title="마스크걸",
#     synopsis='외모 콤플렉스를 가진 평범한 직장인 김모미가 밤마다 마스크로 얼굴을 가린 채 인터넷 방송 BJ로 활동하면서 의도치 않은 사건에 휘말리며 벌어지는 이야기',
#     genre='스릴러'
# )

# if __name__ == "__main__":
#     print(filter_topic("topic/topicJSON.json"))