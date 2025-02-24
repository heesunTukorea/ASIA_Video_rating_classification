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
    All Ages (전체관람가): No abusive language, profanity, vulgar language, etc. or very weakly expressed, so there are no elements to offend
    not negatively affecting a child's correct language habits
    A very weak level of verbal expression that does not have abusive language or offend
    the absence of discriminatory and human rights violations
    No or very weak representation of the other person (gender/race/disability/occupation/religion/foreign/region/locality/locality/locality/locality/locality, etc.)

    12+ (12세이상관람가): the expression of light swear words, profanity, vulgar language, etc. at a low frequency
    a slight and concise expression of everyday expletives or casual swear words
    not negatively affecting the correct language habits of adolescents
    There are slang and buzzwords that are popular among adolescents, but they can be accommodated by adolescents aged 12 or older
    a minor and concise expression of discriminatory and human rights violations
    A minor and concise expression of the personality of the other person or of the expression of attack, insult, or curse
    a minor and concise expression of derogatory expressions (gender/race/disability/occupation/religion/foreign/region/loyalty, etc.) toward the other party

    15+ (15세이상관람가): There are harsh swear words, profanity, vulgar language, etc., but they are not continuously and repeatedly expressed
    There are aggressive and shaming expressions, but acceptable in terms of content development
    an absence of constant and repetitive expression of swear words, profanity, vulgar language, etc
    The use of language that is discriminatory and infringing on human rights, but the elements of verbal violence are not excessive
    A continuous and repetitive expression of the personality of the other person or of the expression of attack, insult, or curse
    continuous and repeated failure to express disparaging expressions (gender/race/disability/occupation/religion/foreign/region/locality/locality/locality/locality/locality, etc.) toward the other party

    Adults Only (청소년관람불가): Repeated and continuous use of vulgar abusive language, profanity, vulgar language, etc. at a level that causes irritating and abhorrent sexual expressions and emotional and personal insults or shame
    a constant and repeated expression of swear words, profanity, vulgar language, etc
    A continuous and repetitive expression of the person's character, attack, insult, or curse
    continuous and repetitive derogatory expressions (gender/race/disability/occupation/religion/foreign/region/locality/locality/locality/locality/locality/locality, etc.) toward the other party
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
#         "whisper/lines_result/연애빠진로맨스_lines_json.json",
#         "whisper/rating_result/연애빠진로맨스.json"
#     )
