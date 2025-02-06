import os
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import torch.nn.functional as F

# 디바이스 설정
def get_device():
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 모델 로드 함수
def load_model_and_tokenizer(model_path, device):
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model.to(device)
    return model, tokenizer

# 욕설 예측 함수
def predict_abuse(model, tokenizer, sentence, device):
    model.eval()
    tokenized_sent = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**tokenized_sent)
    probs = F.softmax(outputs.logits, dim=-1)
    confidence, predicted_class = torch.max(probs, dim=-1)
    confidence = confidence.item()
    
    if predicted_class.item() == 0:  # 욕설
        if confidence >= 0.9:
            return "강한 욕설", confidence
        elif confidence >= 0.5:
            return "약한 욕설", confidence
    return "정상", confidence

def predict_hate(model, tokenizer, sentence, device):
    categories = ["여성/가족", "남성", "성소수자", "인종/국적", "연령", "지역", "종교", "기타 혐오"]
    model.eval()
    
    tokenized_sent = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
    
    with torch.no_grad():
        outputs = model(**tokenized_sent)
    
    probs = F.softmax(outputs.logits, dim=-1)
    
    # 모든 카테고리별로 0.5 이상이면 혐오로 판단
    predicted_labels = (probs > 0.5).tolist()[0]  # [True, False, False, True, ...] 형태로 변환

    # 카테고리별 혐오 여부 판단
    result = {category: "혐오" if pred else "비혐오" for category, pred in zip(categories, predicted_labels)}
    
    # 전체 혐오 여부 판단
    overall_hate = "혐오 표현 있음" if any(predicted_labels) else "혐오 표현 없음"
    
    return overall_hate, result

# 대사 분석 및 결과 집계
def analyze_script(abuse_model_path, hate_model_path, script_path):
    device = get_device()
    abuse_model, abuse_tokenizer = load_model_and_tokenizer(abuse_model_path, device)
    hate_model, hate_tokenizer = load_model_and_tokenizer(hate_model_path, device)
    
    total_sentences = 0
    strong_abusive, weak_abusive = 0, 0
    hate_counts = {"여성/가족": 0, "남성": 0, "성소수자": 0, "인종/국적": 0, "연령": 0, "지역": 0, "종교": 0, "기타 혐오": 0}
    
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    
    for line in script.splitlines():
        sentence = line.strip()
        if not sentence:
            continue
        
        total_sentences += 1
        
        # 욕설 분석
        abuse_label, _ = predict_abuse(abuse_model, abuse_tokenizer, sentence, device)
        if abuse_label == "강한 욕설":
            strong_abusive += 1
        elif abuse_label == "약한 욕설":
            weak_abusive += 1
        
        # 혐오 표현 분석
        _, hate_results = predict_hate(hate_model, hate_tokenizer, sentence, device)
        for category, value in hate_results.items():
            if value == "혐오":
                hate_counts[category] += 1
    
    # 비율 계산
    strong_abusive_percentage = (strong_abusive / total_sentences) * 100 if total_sentences > 0 else 0
    weak_abusive_percentage = (weak_abusive / total_sentences) * 100 if total_sentences > 0 else 0
    hate_percentages = {category: (count / total_sentences) * 100 if total_sentences > 0 else 0 for category, count in hate_counts.items()}
    
    result = {
        "strong_abusive_percentage": round(strong_abusive_percentage, 2),
        "weak_abusive_percentage": round(weak_abusive_percentage, 2),
        **{f"{category}_hate_percentage": round(value, 2) for category, value in hate_percentages.items()}
    }
    
    return result

# 결과 처리 및 파일 저장
def process_script(script_path, output_path):
    abuse_model_path = 'lines/JminJ'  # 욕설 탐지 모델 경로
    hate_model_path = 'lines/Unsmile'  # 혐오 탐지 모델 경로
    
    # 분석 결과 생성
    analysis_result = analyze_script(abuse_model_path, hate_model_path, script_path)
    
    # 결과를 JSON 파일로 저장
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(analysis_result, json_file, ensure_ascii=False, indent=4)
    
    print(f"분석 결과가 '{output_path}' 파일에 저장되었습니다.")

# # 예제 실행
# if __name__ == "__main__":
#     process_script(
#         "result/수상한 그녀/수상한 그녀_text_output/수상한 그녀_text.txt",
#         "result/수상한 그녀/result_json/수상한 그녀_totallines_json.json"
#     )