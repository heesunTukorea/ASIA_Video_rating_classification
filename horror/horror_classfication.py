import os
import json
from transformers import pipeline



def classify_images_horror(image_folder, output_json_path):
    horror_candidates = [
    "A scene that evokes psychological fear and suffering",  # 심리적 공포와 고통이 느껴지는 장면
    "An image that induces tension and anxiety",  # 긴장감과 불안감을 유발하는 이미지
    "A character with a terrified facial expression",  # 공포에 질린 표정을 짓는 등장인물
    "A frightening or grotesque scene",  # 무섭거나 혐오스러운 장면
    "A dark atmosphere with threatening elements",  # 어두운 분위기와 위협적인 요소
    "An image with sudden jump-scare effects",  # 갑작스러운 놀람 효과가 포함된 이미지
    "An unrealistic and menacing fantasy character",  # 비현실적이고 위협적인 판타지 캐릭터
    "A visual effect that creates an eerie atmosphere",  # 공포 분위기를 조성하는 시각적 효과
    "A fantasy creature with a terrifying appearance"  # 무서운 외양을 가진 판타지 생물체
    ]

    non_horror_candidates = [
        "A scene with a peaceful and stable atmosphere",  # 평화롭고 안정적인 분위기의 장면
        "An image that feels bright and warm",  # 밝고 따뜻한 분위기가 느껴지는 이미지
        "A natural landscape depicted in tranquility",  # 자연 경관이 평온하게 묘사된 장면
        "A frame showing everyday and familiar activities",  # 일상적이고 친숙한 활동이 표현된 화면
        "A scene featuring characters smiling",  # 웃고 있는 등장인물이 나오는 장면
        "A cozy and comfortable indoor space",  # 쾌적하고 편안한 실내 공간
        "An outdoor scene with bright sunlight",  # 밝은 햇살이 비치는 야외 장면
        "An image completely free of horror elements",  # 공포 요소가 전혀 없는 이미지
        "A moment conveying joy and comfort",  # 즐거움과 편안함이 느껴지는 순간
        "An environment that feels pure and safe",  # 순수하고 안전한 환경이 표현된 화면
        "A character with a casual expression" # 아무렇지 않은 표정을 짓고있는 등장인물
    ]

    checkpoint = "openai/clip-vit-large-patch14"
    detector = pipeline(model=checkpoint, task="zero-shot-image-classification")
    """
    이미지 폴더 내 모든 이미지를 CLIP 모델로 분류하고 JSON 파일로 저장하는 함수.
    
    Args:
        image_folder (str): 이미지 파일이 저장된 폴더 경로.
        output_json_path (str): 결과를 저장할 JSON 파일 경로.
        horror_candidates (list): 공포 관련 텍스트 후보군.
        non_horror_candidates (list): 공포스럽지 않은 텍스트 후보군.
    
    Returns:
        None: JSON 파일로 결과를 저장.
    """
    # 결과 저장용 리스트
    results = []
    
    # 이미지 폴더 내 파일 처리
    for image_name in sorted(os.listdir(image_folder)):
        image_path = os.path.join(image_folder, image_name)
        
        # 이미지 파일만 처리 (예: .png, .jpg, .jpeg)
        if not image_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        
        try:
            # CLIP 모델로 예측
            predictions = detector(image_path, candidate_labels=horror_candidates + non_horror_candidates)
            # 가장 높은 확률과 해당 레이블 추출
            best_prediction = max(predictions, key=lambda x: x['score'])

            highest_prob = best_prediction['score']
            best_caption = best_prediction['label']
            if best_caption in horror_candidates:
                if highest_prob < 0.4:
                    best_caption = "non-horror"
                    
            elif best_caption in non_horror_candidates:
                best_caption = "non-horror"
            
            
            # 공포 여부 판단 (True: 공포 관련, False: 공포스럽지 않은)
            classification = best_caption in horror_candidates
            
            
            print(f"Image: {image_name}, Classification: {classification}, Best Caption: {best_caption}, Highest Probability: {highest_prob}")
            # 결과 저장
            results.append({
                "image_name": image_name,
                "best_caption": best_caption,
                "highest_prob": str(highest_prob),
                "classification": classification
            })
        except Exception as e:
            print(f"Error processing {image_name}: {e}")
    
    # 결과를 JSON 파일로 저장
    with open(output_json_path, "w") as json_file:
        json.dump(results, json_file, indent=4)
    
    print(f"JSON 저장 완료: {output_json_path}")

# 텍스트 후보군 정의

# 함수 실행 예시
# if __name__ == "__main__":
#     image_folder_path = "video_data/범죄도시_images_output"
#     output_json_path = "./범죄도시.json"
    
#     classify_images_horror(image_folder_path, output_json_path, horror_candidates, non_horror_candidates)
    
    
    