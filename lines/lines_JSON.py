import os
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import torch.nn.functional as F

def get_device():
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model_and_tokenizer(model_path, device):
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model.to(device)
    return model, tokenizer

def predict_abuse(model, tokenizer, sentence, device):
    model.eval()
    tokenized_sent = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**tokenized_sent)
    probs = F.softmax(outputs.logits, dim=-1)
    confidence, predicted_class = torch.max(probs, dim=-1)
    confidence = confidence.item()
    
    if predicted_class.item() == 0:
        if confidence >= 0.9:
            return "strong", confidence  # 강한 욕설
        elif confidence >= 0.5:
            return "weak", confidence  # 약한 욕설
    return "none", confidence

def predict_hate(model, tokenizer, sentence, device):
    categories = ["여성/가족", "남성", "성소수자", "인종/국적", "연령", "지역", "종교"]
    model.eval()
    tokenized_sent = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**tokenized_sent)
    probs = F.softmax(outputs.logits, dim=-1)
    predicted_labels = (probs > 0.9).tolist()[0]
    result = {category: pred for category, pred in zip(categories, predicted_labels)}
    return result

def process_script(script_path, output_path):
    abuse_model_path = 'lines/JminJ'  # 욕설 탐지 모델 경로
    hate_model_path = 'lines/Unsmile'  # 혐오 탐지 모델 경로
    device = get_device()
    abuse_model, abuse_tokenizer = load_model_and_tokenizer(abuse_model_path, device)
    hate_model, hate_tokenizer = load_model_and_tokenizer(hate_model_path, device)
    
    total_sentences = 0
    strong_abusive, weak_abusive = 0, 0
    hate_counts = {category: 0 for category in ["여성/가족", "남성", "성소수자", "인종/국적", "연령", "지역", "종교"]}
    results = []
    
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    
    for line in script.splitlines():
        sentence = line.strip()
        if not sentence:
            continue
        total_sentences += 1
        abuse_label, _ = predict_abuse(abuse_model, abuse_tokenizer, sentence, device)
        strong_abuse = abuse_label == "strong"
        weak_abuse = abuse_label == "weak"
        hate_results = predict_hate(hate_model, hate_tokenizer, sentence, device)
        
        result = {
            "lines": sentence,
            "strong_abusive_percentage": strong_abuse,
            "weak_abusive_percentage": weak_abuse,
        }
        
        for category, value in hate_results.items():
            result[f"{category}_hate_percentage"] = value
            if value:
                hate_counts[category] += 1
        
        results.append(result)
        if strong_abuse:
            strong_abusive += 1
        if weak_abuse:
            weak_abusive += 1
    
    summary = {
        "strong_abusive_percentage": (strong_abusive / total_sentences) * 100 if total_sentences > 0 else 0,
        "weak_abusive_percentage": (weak_abusive / total_sentences) * 100 if total_sentences > 0 else 0,
        **{f"{category}_hate_percentage": (count / total_sentences) * 100 if total_sentences > 0 else 0 for category, count in hate_counts.items()}
    }
    
    output_data = {"results": results, "summary": summary}
    
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(output_data, json_file, ensure_ascii=False, indent=4)
    
    print(f"분석 결과가 '{output_path}' 파일에 저장되었습니다.")

def filter_by_category(input_path, output_path, category):
    """category에는
    "strong_abusive_percentage", "weak_abusive_percentage",
    "여성/가족_hate_percentage", "남성_hate_percentage",
    "성소수자_hate_percentage", "인종/국적_hate_percentage",
    "연령_hate_percentage", "지역_hate_percentage",
    "종교_hate_percentage" 중 택"""


    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    filtered_lines = [entry["lines"] for entry in data["results"] if entry[category]]
    
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(filtered_lines, json_file, ensure_ascii=False, indent=4)
    
    print(f"필터링된 결과가 '{output_path}' 파일에 저장되었습니다.")



# #예제 실행
# if __name__ == "__main__":
#     process_script(
#         "텍스트/수상한 그녀_text.txt",
#         "텍스트 결과/수상한 그녀_lines_json.json"
#     )

# if __name__ == "__main__":
#     filter_by_category(
#         "텍스트 결과/수상한 그녀_lines_json.json",
#         "텍스트 결과/수상한 그녀lines_json.json",
#         "strong_abusive_percentage"
#     )
