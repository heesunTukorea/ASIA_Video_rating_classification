from transformers import CLIPProcessor, CLIPModel
import os
import json
from PIL import Image
from collections import Counter

def drug(image_folder_path, output_file, threshold=0.65):
    
    # 모델 및 프로세서 로드
    model_name = "openai/clip-vit-large-patch14"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    # 텍스트 후보군 생성
    text_candidates = [

       # 마약
        "white powder(illegal drug) in the scene",
        "a person preparing illegal drugs for use",
        "a posture of inhaling drugs",

        # 기타
        "A picture of a person standing",
        "A peaceful scene",
        "A person walking in the street",
        "A lot of people walking in th street",
        "A calm conversation between people",
        "A person smiling and laughing",
        "The scene that people are talking about",
        "a person sitting",
        "a person standing",
        "a photo of a drinking",
        "a picture of someone kissing",
        "a picture of someone taking off his clothes",
        "a scene of violence",
        "a laboratory scene"
    ]

    # 출력 테스트 타깃 설정
    target_captions = {
        "white powder(illegal drug) in the scene",
        "a person preparing illegal drugs for use",
        "a posture of inhaling drugs"
    }

    # 결과 저장
    results = []
    caption_counts = Counter()

    # 폴더 내 모든 이미지 파일 가져오기
    image_files = os.listdir(image_folder_path)
    image_files.sort()

    # 폴더 내 모든 이미지 파일 처리
    for idx, image_name in enumerate(image_files, start=1):
        image_path = os.path.join(image_folder_path, image_name)

        try:
            # 이미지 처리 상황 출력
            print(f"처리 중: [{idx}/{len(image_files)}] {image_name}")

            # 이미지 로드
            image = Image.open(image_path).convert("RGB")

            # 입력 데이터 전처리
            inputs = processor(text=text_candidates, images=image, return_tensors="pt", padding=True)

            # 모델 추론
            outputs = model(**inputs)

            # 이미지-텍스트 유사도 계산
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

            # 가장 높은 유사도를 가진 텍스트와 해당 확률
            best_match_idx = probs.argmax()
            best_caption = text_candidates[best_match_idx]
            highest_prob = probs[0, best_match_idx].item()

            # 조건에 따른 출력
            if highest_prob >= threshold and best_caption in target_captions:
                display_caption = best_caption
                caption_counts[best_caption] += 1
            else:
                display_caption = "마약과 관련된 장면이 없습니다."

            # 결과 저장
            results.append({
                "image_name": image_name,
                "best_caption": display_caption,
                "highest_prob": highest_prob
            })

        except Exception as e:
            print(f"Error processing {image_name}: {e}")

    # 마약 관련 요약 추가
    total_scenes = len(image_files)
    drug_count = sum(caption_counts[caption] for caption in target_captions)
    non_drug_count = total_scenes - drug_count
    drug_rate_true = drug_count / total_scenes if total_scenes > 0 else 0
    drug_rate_false = non_drug_count / total_scenes if total_scenes > 0 else 0

    summary_stats = {
        "total_scenes": total_scenes,
        "drug_best_caption": {
            caption: caption_counts[caption] for caption in target_captions
        },
        "non-drug": non_drug_count,
        "drug_rate_true": drug_rate_true,
        "drug_rate_false": drug_rate_false
    }

    # JSON으로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"results": results, "summary": summary_stats}, f, indent=4, ensure_ascii=False)

    print("\n마약과 관련된 장면 빈도:")
    for caption, count in caption_counts.items():
        print(f"{caption}: {count}")

    print("\n분석 결과:")
    for result in results:
        print(result)

    print(f"\n모든 결과가 {output_file}에 저장되었습니다.")

    # 결과와 각 마약성 빈도 리턴
    return results, summary_stats

# 실행
# image_path = '/result/수리남/수리남_images_output'
# output_file = '/result/수리남/result_json/수리남_drug_img_json.json'
# drug(image_path, output_file, threshold=0.65)
