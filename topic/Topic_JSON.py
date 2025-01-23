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
        f"다음 메타데이터와 대사에서 주제를 찾아서 키워드, 키워드의 설명, 표현방식, 메시지 전달의도, 장르적 특성을 JSON 형식으로 출력해줘. "
        f"JSON에 소개와 장르 정보도 요약해서 추가해줘.\n\n"
        f"메타데이터:\n{metadata}\n\n"
        f"대사:\n{script}"
    )

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content

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
