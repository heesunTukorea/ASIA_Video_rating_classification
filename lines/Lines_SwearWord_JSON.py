import os
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import torch.nn.functional as F

# 디바이스 설정
def get_device():
    """GPU가 사용 가능한 경우 GPU, 그렇지 않으면 CPU를 반환합니다."""
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 모델과 토크나이저 로드
def load_model_and_tokenizer(model_path, device):
    """모델과 토크나이저를 로드하고 디바이스로 이동합니다."""
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model.to(device)
    return model, tokenizer

# 문장 예측 함수
def predict_sentence(model, tokenizer, sentence, device):
    """주어진 문장에 대해 욕설 여부를 예측합니다."""
    model.eval()

    # 문장 토크나이즈
    tokenized_sent = tokenizer(
        sentence,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    ).to(device)

    with torch.no_grad():
        outputs = model(
            input_ids=tokenized_sent['input_ids'],
            attention_mask=tokenized_sent['attention_mask'],
            token_type_ids=tokenized_sent.get('token_type_ids')
        )

    logits = outputs[0]

    # 소프트맥스를 사용한 확률 계산
    probs = F.softmax(logits, dim=-1)
    confidence, predicted_class = torch.max(probs, dim=-1)

    confidence = confidence.item()

    # 라벨 분류
    if predicted_class.item() == 0:  # 욕설
        if confidence >= 0.9:
            label = 0  # 강한 욕설
        elif confidence >= 0.5:
            label = 1  # 약한 욕설
        else:
            label = 2  # 정상
    else:
        label = 2  # 정상

    return label, confidence

# 대사 분석 및 결과 집계
def lines_result(model_path, script_path):
    device = get_device()
    model, tokenizer = load_model_and_tokenizer(model_path, device)

    total_sentences = 0
    strong_abusive = 0
    weak_abusive = 0

    # 텍스트 파일 읽기
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    for line_num, line in enumerate(script.splitlines(), 1):
        sentence = line.strip()
        if not sentence:
            continue

        total_sentences += 1
        label, confidence = predict_sentence(model, tokenizer, sentence, device)

        if label == 0:
            strong_abusive += 1
        elif label == 1:
            weak_abusive += 1

    strong_abusive_percentage = (strong_abusive / total_sentences) * 100 if total_sentences > 0 else 0
    weak_abusive_percentage = (weak_abusive / total_sentences) * 100 if total_sentences > 0 else 0

    result = {
        "strong_abusive_percentage": round(strong_abusive_percentage, 2),
        "weak_abusive_percentage": round(weak_abusive_percentage, 2)
    }

    return result

# 결과 처리 및 파일 저장
def process_lines(script_path, output_path):
    model_path = 'lines/JminJ'
    script_path = script_path

    # 분석 결과 생성
    analysis_result = lines_result(model_path, script_path)

    # 결과를 JSON 파일로 저장
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(analysis_result, json_file, ensure_ascii=False, indent=4)

    print(f"분석 결과가 '{output_path}' 파일에 저장되었습니다.")
