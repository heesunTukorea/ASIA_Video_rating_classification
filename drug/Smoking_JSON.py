import os
import json
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import unicodedata

def classify_images_smoking(folder_path, output_json_path):
    """
    이미지에서 흡연 장면을 탐지하고, 비흡연 후보군과 비교하여 최종 판정을 내립니다.
    결과는 JSON 파일로 저장됩니다.
    """

    # 🚬 흡연 관련 텍스트 후보군 (Positive Class)
    text_candidates_smoking = [
        "A person smoking a cigarette",  
        "A cigarette with visible smoke",  
        "A person exhaling a thick cloud of smoke",  
        "A person vaping with a visible vapor cloud",  
        "A person smoking a cigar",  
        "A cigarette with ashes forming at the tip", 
        "A person flicking ash from a cigarette",  
        "A person holding a cigarette between their fingers",  
        "A person holding a lit cigarette in their mouth",  
    ]

    # 🚫 비흡연 관련 텍스트 후보군 (Negative Class)
    text_candidates_non_smoking = [
        "A person sitting without smoking",  
        "A person drinking coffee without smoking", 
        "A person standing in a non-smoking area",  
        "A person holding a lighter without a cigarette",  
        "A person using a lighter to ignite a candle", 
        "A person holding a lollipop in their mouth",
        "A person holding a white stick(not a cigarette) in their mouth"
    ]

    # CLIP 모델 및 프로세서 초기화
    clip = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

    def detect_smoking_scene(image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 경로를 찾을 수 없습니다: {image_path}")

        img = Image.open(image_path)

        # CLIP을 사용하여 흡연 & 비흡연 텍스트 후보군 비교
        inputs_smoking = processor(text=text_candidates_smoking, images=img, return_tensors="pt", padding=True)
        inputs_non_smoking = processor(text=text_candidates_non_smoking, images=img, return_tensors="pt", padding=True)

        outputs_smoking = clip(**inputs_smoking)
        outputs_non_smoking = clip(**inputs_non_smoking)

        probs_smoking = outputs_smoking.logits_per_image.softmax(dim=1)
        probs_non_smoking = outputs_non_smoking.logits_per_image.softmax(dim=1)

        # 각 그룹에서 최고 확률을 가진 후보 선택
        highest_prob_smoking = probs_smoking.max().item()
        highest_prob_non_smoking = probs_non_smoking.max().item()

        # 🚬 흡연 장면인지 여부 결정 (흡연 확률이 더 높을 때만 True)
        is_smoking_scene = highest_prob_smoking > highest_prob_non_smoking

        return {
            "image_name": f"frame_{os.path.splitext(os.path.basename(image_path))[0].split('_')[-1]}.png",
            "highest_prob_smoking": highest_prob_smoking,
            "highest_prob_non_smoking": highest_prob_non_smoking,
            "classification": is_smoking_scene
        }

    folder_path = unicodedata.normalize('NFC', folder_path)
    output_json_path = unicodedata.normalize('NFC', output_json_path)

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"폴더 경로를 찾을 수 없습니다: {folder_path}")

    image_files = [
        os.path.join(folder_path, file) for file in sorted(os.listdir(folder_path))
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    ]

    results = []
    caption_counts = {}

    for image_path in image_files:
        print(f"분석 중: frame_{os.path.splitext(os.path.basename(image_path))[0].split('_')[-1]}.png")
        result = detect_smoking_scene(image_path)
        # classification이 True인 경우 흡연 후보군 중 최고 확률에 해당하는 캡션 추출
        if result["classification"]:
            img = Image.open(image_path)
            inputs_smoking = processor(text=text_candidates_smoking, images=img, return_tensors="pt", padding=True)
            outputs_smoking = clip(**inputs_smoking)
            probs_smoking = outputs_smoking.logits_per_image.softmax(dim=1)
            _, best_idx = probs_smoking.max(dim=1)
            caption = text_candidates_smoking[best_idx.item()]
            result["caption"] = caption
            caption_counts[caption] = caption_counts.get(caption, 0) + 1
        else:
            result["caption"] = "흡연에 해당하는 장면 없음"
        results.append(result)

    # 📊 통계 요약 생성
    total_scenes = len(results)
    smoking_true_count = sum(1 for item in results if item['classification'] is True)
    smoking_false_count = total_scenes - smoking_true_count
    true_rate = round(smoking_true_count / total_scenes, 2) if total_scenes > 0 else 0
    false_rate = round(smoking_false_count / total_scenes, 2) if total_scenes > 0 else 0

    summary_data = {
        "total_scenes": total_scenes,
        "smoking_true": smoking_true_count,
        "smoking_captions": caption_counts, 
        "smoking_false": smoking_false_count,
        "true_rate": true_rate,
        "false_rate": false_rate
    }
    results.append(summary_data)

    # 📝 결과 JSON 파일로 저장 (폴더가 없으면 생성)
    output_folder = os.path.dirname(output_json_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 📝 결과 JSON 파일로 저장
    sorted_results = sorted(results[:-1], key=lambda x: int(x["image_name"].split("_")[-1].split(".")[0]))  # 마지막 요약 데이터 제외 후 정렬
    sorted_results.append(summary_data)  # 마지막 요약 데이터 다시 추가
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print(f"✅ 결과 저장 완료: {output_json_path}")
    
# folder_path = 'video_data/흡연_images_output'
# output_json_path = 'smoking_predictions.json'
# classify_images_smoking(folder_path, output_json_path)
