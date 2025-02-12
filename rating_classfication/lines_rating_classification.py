import os
import json
from dotenv import load_dotenv
from openai import OpenAI

def load_env():
    """Load OpenAI API key from .env file."""
    load_dotenv()
    return os.getenv('OPENAI_API_KEY')

def initialize_openai_client(api_key):
    """Initialize OpenAI client with the provided API key."""
    return OpenAI(api_key=api_key)

def analyze_dialogue_rating(openai_client, dialogue_data):
    """
    Analyze dialogue data to determine an appropriate age rating.
    """
    rating_criteria = """
    Classification criteria for dialogue-based ratings:**  
    All Ages (전체관람가): No or minimal use of profanity, vulgarity, or offensive language. No violent or suggestive dialogue. No discriminatory or demeaning expressions.  
    - 강한 욕설과 약한 욕설이 전혀 없거나 극히 미미함 (0~1% 이하)  
    - 혐오 표현(인종, 지역, 성소수자, 여성/가족 등)이 없음  
    - 아동과 청소년의 언어 습관에 부정적인 영향을 주지 않는 대사  

    12+ (12세이상관람가): Mild profanity, slang, or low-frequency offensive language. No significant impact on youth language habits. Minimal discriminatory or insulting expressions.  
    - 강한 욕설이 없거나 거의 없음 (0% 수준)  
    - 약한 욕설 비율이 낮음 (약 5% 이하)  
    - 혐오 표현(인종, 지역 등)이 일부 포함되었으나 경미한 수준  

    15+ (15세이상관람가): Strong profanity, vulgarity, or offensive language used but not continuously repeated. Some aggressive or humiliating expressions, but within acceptable narrative context.  
    - 강한 욕설이 일부 포함되었으나 빈도가 낮음 (약 0.5% 이상)  
    - 약한 욕설 비율이 중간 정도 (약 2~10%)  
    - 혐오 표현이 일부 포함되었으나 지속적이지 않음  

    Adults Only (청소년관람불가): Frequent and repetitive use of harsh profanity, vulgarity, or offensive language. Explicitly demeaning, humiliating, or violent dialogue. Continuous discrimination or personal attacks.  
    - 강한 욕설이 빈번하게 등장 (약 9% 이상)  
    - 약한 욕설 비율이 매우 높음 (약 36% 이상)  
    - 성소수자, 인종, 지역 등 특정 대상에 대한 혐오 표현이 강하거나 지속적으로 포함됨  
    """
    
    prompt = (
        f"""Based on the following classification criteria and provided dialogue, determine the appropriate age rating for this media.
        Respond strictly in JSON format with:
        {{
            \"rating\": \"관람 등급 (전체관람가, 12세이상관람가, 15세이상관람가, 청소년관람불가)\",
            \"reasoning\": \"한글로 간단한 설명 한 줄\"
        }}
        
        Criteria:
        {rating_criteria}
        
        Dialogue Data:
        {json.dumps(dialogue_data, indent=4, ensure_ascii=False)}"""
    )
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    
    response = response.choices[0].message.content
    response = response.replace("json","")
    response = response.replace("```","")
    return response

def save_json_result(output_json_path, result):
    """Save the result as a JSON file."""
    try:
        parsed_result = json.loads(result)
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(parsed_result, json_file, ensure_ascii=False, indent=4)
        print(f"Analysis result saved at '{output_json_path}'")
    except json.JSONDecodeError:
        print("JSON decoding failed. Response:", result)

def process_dialogue_rating(dialogue_json, output_json_path):
    """Main function to process dialogue-based content rating."""
    # Load API key
    openai_api_key = load_env()
    if not openai_api_key:
        raise ValueError("OpenAI API key not found in .env file.")
    
    # Initialize OpenAI client
    client = initialize_openai_client(openai_api_key)
    
    # Load JSON data
    with open(dialogue_json, "r", encoding="utf-8") as f:
        dialogue_data = json.load(f)["summary"]
        
    # Perform analysis
    analysis_result = analyze_dialogue_rating(client, dialogue_data)
    
    # 결과 저장
    save_json_result(output_json_path, analysis_result)

# # Example execution
# if __name__ == "__main__":
#     process_dialogue_rating(
#         "텍스트 결과/수상한 그녀_lines_json.json",
#         "텍스트 분류 결과/수상한그녀1.json"
#     )
