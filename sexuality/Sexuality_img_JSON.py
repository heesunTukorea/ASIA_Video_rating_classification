# # 필요한 라이브러리 설치
# pip install -q transformers
# pip install -q torch torchvision
# pip install -q pillow

# 라이브러리 임포트
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import matplotlib.pyplot as plt
import json
import os

# CLIP 모델 및 프로세서 초기화
clip = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# CLIP 모델을 이용해 이미지에서 선정성을 판단하는 함수
def detect_sexual_content(image_path, sexual, non_sexual, threshold=0.3, display_image=True, output_json_path=None):
   
    # 이미지 불러오기
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지 경로를 찾을 수 없습니다: {image_path}")

    img = Image.open(image_path)

    # 입력 데이터 전처리
    all_candidates = sexual + non_sexual
    inputs = processor(text=all_candidates, images=img, return_tensors="pt", padding=True)

    # 모델 추론
    outputs = clip(**inputs)

    # 이미지-텍스트 유사도 계산
    logits_per_image = outputs.logits_per_image  # 이미지-텍스트 유사도
    probs = logits_per_image.softmax(dim=1)  # 소프트맥스 확률 계산

    # 가장 높은 유사도를 가진 텍스트와 해당 확률
    best_match_idx = probs.argmax()  # 가장 높은 확률의 텍스트 인덱스
    best_caption_candidate = all_candidates[best_match_idx]  # 가장 유사한 텍스트
    highest_prob = probs[0, best_match_idx].item()  # 해당 텍스트의 유사도 점수

    # 선정적 콘텐츠 여부 확인
    is_sexual = best_caption_candidate in sexual and highest_prob >= threshold

    # best_caption 설정
    best_caption = best_caption_candidate if is_sexual else "선정적인 장면이 없습니다."

    # 결과 출력
    if display_image:
        plt.axis('off')
        plt.imshow(img)
        plt.show()

    result = {
        "image_name": f"frame_{os.path.splitext(os.path.basename(image_path))[0].split('_')[-1]}.png",
        "best_caption": best_caption,
        "highest_prob": highest_prob,
        "classification": is_sexual
    }

    if result["classification"]:
        print(f"\U0001F51E 선정적 콘텐츠 감지됨")
        print(f"Generated Caption: {best_caption}")
        print(f"Similarity Score: {highest_prob}")
    else:
        print("\u2705 선정적 콘텐츠 없음")

    return result

# 폴더 내 모든 이미지를 분석하고 결과를 JSON 파일로 저장하는 함수
def analyze_folder(folder_path, sexual, non_sexual, threshold=0.3, display_image=False, output_json_path=None):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"폴더 경로를 찾을 수 없습니다: {folder_path}")

    image_files = [
        os.path.join(folder_path, file) for file in os.listdir(folder_path)
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    ]

    results = []
    for image_path in image_files:
        print(f"분석 중: frame_{os.path.splitext(os.path.basename(image_path))[0].split('_')[-1]}.png")
        result = detect_sexual_content(
            image_path,
            sexual,
            non_sexual,
            threshold=threshold,
            display_image=display_image
        )
        results.append(result)

    # JSON 파일로 저장
    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        print(f"전체 결과가 {output_json_path}에 저장되었습니다.")

    return results

if __name__ == "__main__":
    # 텍스트 후보군 리스트
    sexual = [
        # 선정적 
        'They are having sex',
        "They are engaging in simulated sexual activity.",
        "There are direct full body exposure.",
        "They are kissing on the lips.",
        "They are having physical contact and touching in revealing clothes.",
        "There are upper body exposure especially chest in revealing clothes.",
        "bikini"
    ]
    non_sexual =[
        # 일반적 
        "A peaceful scene",
        "A person walking in the street",
        "A calm conversation between people",
        "A person smiling, laughing, surprising",
        "A serene and tranquil environment",
        "a photo of a drinking coke",
        "a photo of a drinking",
        "a photo of a person bleeding",
        "a photo of a ghost",
        "a photo of a smoking",
        "a photo of a knife posing a threat",
        "a photo of a gun posing a threat",
        "people and animal",
        "There are family",
        'They are eating food'
    ]

    # 폴더 경로
    folder_path = "./video2imgs/인간중독_video2imgs"

    # JSON 저장 경로
    output_json_path = "./sexual_res_json/인간중독_results.json"

    # 함수 호출
    try:
        results = analyze_folder(
            folder_path,
            sexual,
            non_sexual,
            threshold=0.3,
            display_image=False,
            output_json_path=output_json_path
        )
        # 결과 출력
        print(f"총 {len(results)}개의 이미지가 분석되었습니다.")
    except FileNotFoundError as e:
        print(e)
