import os
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
def process_lines(model_path, script):
    """Whisper에서 추출된 대사를 사용해 욕설 분석을 수행하고 결과를 JSON으로 반환합니다."""
    device = get_device()
    model, tokenizer = load_model_and_tokenizer(model_path, device)

    total_sentences = 0
    strong_abusive = 0
    weak_abusive = 0

    for line_num, line in enumerate(script.splitlines(), 1):
        sentence = line.strip()
        if not sentence:
            continue  # 빈 줄 건너뜀

        total_sentences += 1

        # 예측
        label, confidence = predict_sentence(model, tokenizer, sentence, device)

        # 카운트 증가
        if label == 0:  # 강한 욕설
            strong_abusive += 1
        elif label == 1:  # 약한 욕설
            weak_abusive += 1

    # 욕설 비율 계산
    strong_abusive_percentage = (strong_abusive / total_sentences) * 100 if total_sentences > 0 else 0
    weak_abusive_percentage = (weak_abusive / total_sentences) * 100 if total_sentences > 0 else 0

    # 결과 JSON 반환
    result = {
        #"total_sentences": total_sentences,
        #"strong_abusive": strong_abusive,
        #"weak_abusive": weak_abusive,
        #"normal_sentences": total_sentences - strong_abusive - weak_abusive,
        "strong_abusive_percentage": round(strong_abusive_percentage, 2),
        "weak_abusive_percentage": round(weak_abusive_percentage, 2)
    }#일단 강한욕설, 약한욕설의 퍼센트만 도출하도록 함. 필요시 차례대로 전체문장개수, 강한욕설문장개수, 약한욕설문장개수, 정상문장개수 도출 가능

    return result

if __name__ == "__main__":
    # 모델 경로와 Whisper에서 추출된 대사 예시
    model_path = "./JminJ"  # 모델이 저장된 디렉토리 경로
    script = (
        "이건 정상적인 문장입니다.\n"
        "너 정말 바보 같아.\n"
        "와, 이런 멍청한 짓을 하다니!\n"
        "오늘 날씨가 참 좋네요."
    ) #whisper 결과 가져오도록 수정 필요!!!!!!!!!!!!!!!

    # 결과 출력
    analysis_result = process_lines(model_path, script)
    print(analysis_result)
