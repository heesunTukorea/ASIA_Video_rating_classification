import os
import json
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

def classify_images_smoking(folder_path, output_json_path, threshold=0.3, display_image=False):
    """
    이미지에서 흡연 관련 객체를 탐지하고 결과를 JSON 파일로 저장합니다.
    """
    text_candidates = [
        "A person with smoke coming from their mouth",
        "A lit cigarette",
        "A cigarette with visible smoke",
        "A cigarette held between fingers",
        "A person holding a lighter with no cigarette",
        "A person holding a lighter and cigarette",
        "A person holding a cigarette"
    ]

    # CLIP 모델 및 프로세서 초기화
    clip = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

    def detect_smoking_scene(image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 경로를 찾을 수 없습니다: {image_path}")

        img = Image.open(image_path)
        inputs = processor(text=text_candidates, images=img, return_tensors="pt", padding=True)
        outputs = clip(**inputs)

        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

        best_match_idx = probs.argmax()
        best_caption_candidate = text_candidates[best_match_idx]
        highest_prob = probs[0, best_match_idx].item()

        is_smoking_scene = highest_prob >= threshold

        return {
            "image_name": f"frame_{os.path.splitext(os.path.basename(image_path))[0].split('_')[-1]}.png",
            "highest_prob": highest_prob,
            "classification": is_smoking_scene
        }

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"폴더 경로를 찾을 수 없습니다: {folder_path}")

    image_files = [
        os.path.join(folder_path, file) for file in os.listdir(folder_path)
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    ]

    results = []

    for image_path in image_files:
        print(f"분석 중: frame_{os.path.splitext(os.path.basename(image_path))[0].split('_')[-1]}.png")
        result = detect_smoking_scene(image_path)
        results.append(result)

    # 통계 요약 생성
    total_scenes = len(results)
    smoking_true_count = sum(1 for item in results if item['classification'] is True)
    smoking_false_count = total_scenes - smoking_true_count
    true_rate = round(smoking_true_count / total_scenes, 2) if total_scenes > 0 else 0
    false_rate = round(smoking_false_count / total_scenes, 2) if total_scenes > 0 else 0

    summary_data = {
        "total_scenes": total_scenes,
        "smoking_true": smoking_true_count,
        "smoking_false": smoking_false_count,
        "true_rate": true_rate,
        "false_rate": false_rate
    }
    results.append(summary_data)

    # 결과 저장
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_json_path}")

# folder_path = 'video_data/흡연_images_output'
# output_json_path = 'smoking_predictions.json'
# classify_images_smoking(folder_path, output_json_path)
