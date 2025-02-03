import openai
import json
import base64
from dotenv import load_dotenv
import os
from imitation_risk.image_text_match import process_matching
# OpenAI API 키 설정
# .env 파일 로드



load_dotenv()

# 환경 변수 사용

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
# 시스템 메시지로 기본 지침 설정
  # 새로운 데이터에 초점을 맞춘 사용자 메시지
    # 입력된 새로운 데이터를 분석해 주세요.
    # 텍스트: 장면 설명입니다.
    # 이미지 경로: 장면과 관련된 이미지의 파일 경로입니다.
    # 아래 JSON 구조로 결과를 생성해 주세요
    # 한국어로 응답해 주세요.
            # 주어진 텍스트와 이미지 경로를 분석하여 아래 질문에 기반한 JSON 데이터를 생성하세요.
            # 1. **맥락(Context)**: 텍스트와 이미지를 활용하여 장면의 주요 상황을 간단히 설명하세요.
            # 2. **위험 행동(Risk Behavior)**: 모방 위험을 초래할 수 있는 행동이나 요소를 식별하세요.
            # 3. **모방 가능성(Mimicry Risk)**: 모방 위험 수준(낮음, 보통, 높음)을 평가하고 간단히 이유를 설명하세요.
            # 4. **도구 및 장소(Tools & Environment)**: 장면에서 사용된 도구나 물체를 명시하고 환경을 설명하세요.
            # 5. **메시지 성격(Message Tone)**: 전달되는 메시지가 긍정적, 중립적, 부정적인지 명시하세요.
# 이미지 파일을 Base64로 인코딩하는 함수

def encode_image(image_path):
    """
    이미지 파일 경로를 받아 Base64로 인코딩된 문자열을 반환합니다.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# GPT 호출 함수
def process_scene_data(scene_text, image_path):
    """
    텍스트와 Base64 이미지 데이터를 GPT로 보내 분석 결과를 JSON으로 반환합니다.
    """
    # 이미지 파일을 Base64로 인코딩
    base64_image = encode_image(image_path)
    # 이미지 파일 이름에서 확장자 제거
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    # 사용자 메시지 생성
    user_message = [
        {"type": "text", "text": f"""
        Please analyze the following scene and image.
        - Text: {scene_text}
        - Image: The provided image is
        
        Generate the result in JSON format:
        {{
          "{image_name}": {{
            "context": "[Describe the main context of the scene based on the text and image.]",
            "risk_behavior": "[Describe any risk behaviors that could encourage mimicry.]",
            "mimicry_risk": "[Select one: Low/Medium/High]",
          }}
        }}
        output is only json
        Please respond in English. 
        """},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
    ]

    # GPT API 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert at generating JSON data. Analyze the input text and image and generate a structured JSON result."},
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
def process_input_file(input_file, output_file):
    """
    JSON 파일로부터 입력 데이터를 읽어와 GPT로 처리하고 결과를 JSON 파일로 저장합니다.
    """
    # 입력 데이터 읽기
    with open(input_file, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    results = []
    for scene in scenes:
        try:
            # 첫 번째 시도
            result = process_scene_data(scene["text"], scene["image_path"])
            print(result)
            results.append(result)
        except Exception as e:
            print(f"Error processing scene: {scene['text']} on first attempt with error: {str(e)}")
            try:
                # 두 번째 시도
                print("Retrying...")
                result = process_scene_data(scene["text"], scene["image_path"])
                print(result)
                results.append(result)
            except Exception as retry_e:
                print(f"Error processing scene: {scene['text']} on second attempt with error: {str(retry_e)}")
                # 두 번째 시도도 실패한 경우
                results.append({"scene": scene["text"], "error": str(retry_e)})
        # 결과를 JSON 파일로 저장
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        print(f"Processing complete. Results saved to {output_file}")

# 메인 함수
def imitation_risk_api(image_folder,text_file_path):
    """
    메인 실행 함수. 입력 파일 경로와 출력 파일 경로를 지정합니다.
    """
      # 텍스트 파일 경로
    # output_file_path = "result/오징어게임시즌2/matched.json"  # 결과 저장 파일 경로
    base_path = os.path.dirname(image_folder)
    base_name = base_path.split('result/')[1] 
    result,input_file= process_matching(image_folder, text_file_path)
    input_file = input_file
    #input_file = "test.json"  # 입력 JSON 파일 경로
    output_file = f"{base_path}/result_json/{base_name}_imitation_json.json"  # 출력 JSON 파일 경로
    process_input_file(input_file, output_file)

# image_folder = "result/아저씨/아저씨_images_output" #이미지 폴더 경로
# text_file_path = "result/아저씨/아저씨_text_output/아저씨_text.txt"#대사 경로
# imitation_risk_api(image_folder,text_file_path) # result_json 폴더에 자동으로 파일 생성