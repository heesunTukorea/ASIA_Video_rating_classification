import openai
import json
import base64
from dotenv import load_dotenv
import os
from imitation_risk.image_text_match import process_matching

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def encode_image(image_path):
    """
    이미지 파일 경로를 받아 Base64로 인코딩된 문자열을 반환합니다.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_scene_data(scene_text, image_path):
    """
    텍스트와 Base64 이미지 데이터를 GPT로 보내 분석 결과를 JSON으로 반환합니다.
    """
    base64_image = encode_image(image_path)
    image_name = os.path.splitext(os.path.basename(image_path))[0]

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
            "mimicry_risk": "[Select one: Low/Medium/High]"
          }}
        }}
        output is only json
        Please respond in English. 
        """},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert at generating JSON data. Analyze the input text and image and generate a structured JSON result."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=500
    )
    
    result_text = response.choices[0].message.content
    result_text = result_text.replace("json", "").replace("```", "")
    json_result = json.loads(result_text)
    
    return json_result

def process_input_file(input_file, output_file):
    """
    JSON 파일로부터 입력 데이터를 읽어와 GPT로 처리하고 결과를 JSON 파일로 저장합니다.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    results = []
    summary = {"high_risk": [], "medium_risk": []}
    
    for scene in scenes:
        try:
            result = process_scene_data(scene["text"], scene["image_path"])
            print(result)
            results.append(result)
            
            for frame, data in result.items():
                if data["mimicry_risk"].lower() == "high":
                    summary["high_risk"].append({"context": data["context"], "risk_behavior": data["risk_behavior"]})
                elif data["mimicry_risk"].lower() == "medium":
                    summary["medium_risk"].append({"context": data["context"], "risk_behavior": data["risk_behavior"]})
            
        except Exception as e:
            print(f"Error processing scene: {scene['text']} on first attempt with error: {str(e)}")
            results.append({"scene": scene["text"], "error": str(e)})

    # 결과에 요약 정보 추가
    results.append({"summary": summary})
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"Processing complete. Results saved to {output_file}")

def imitation_risk_api(image_folder, text_file_path, time_interval=1):
    """
    메인 실행 함수. 입력 파일 경로와 출력 파일 경로를 지정합니다.
    """
    base_path = os.path.dirname(image_folder)
    base_name = base_path.split('result/')[1] 
    result, input_file = process_matching(image_folder, text_file_path, time_interval)
    output_file = f"{base_path}/result_json/{base_name}_imitation_json.json"
    process_input_file(input_file, output_file)


# image_folder = "result/아저씨/아저씨_images_output" #이미지 폴더 경로
# text_file_path = "result/아저씨/아저씨_text_output/아저씨_text.txt"#대사 경로
# imitation_risk_api(image_folder,text_file_path) # result_json 폴더에 자동으로 파일 생성