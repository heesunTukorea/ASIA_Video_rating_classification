from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import matplotlib.pyplot as plt
import json
import os
from collections import Counter

def classify_images_smoking(folder_path, threshold=0.3, display_image=False, output_json_path=None):
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
        best_caption = best_caption_candidate if is_smoking_scene else "흡연 장면이 없습니다."

        return {
            "image_name": f"frame_{os.path.splitext(os.path.basename(image_path))[0].split('_')[-1]}.png",
            "best_caption": best_caption,
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

    total_pages = len(results)
    caption_counts = Counter(item['best_caption'] for item in results)
    smoking_caption_counts = {caption: caption_counts.get(caption, 0) for caption in text_candidates}

    true_count = sum(1 for item in results if item['classification'] is True)
    false_count = total_pages - true_count

    true_rate = round(true_count / total_pages, 2) if total_pages > 0 else 0
    false_rate = round(false_count / total_pages, 2) if total_pages > 0 else 0

    summary = {
        "total_scenes": total_pages,
        "smoking_best_caption": smoking_caption_counts,
        "non-smoking": caption_counts.get("흡연 장면이 없습니다.", 0),
        "smoking_rate_true": true_rate,
        "smoking_rate_false": false_rate
    }
    results.append(summary)

    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        print(f"전체 결과가 {output_json_path}에 저장되었습니다.")

    return results

# if __name__ == "__main__":
#     folder_path = "video2imgs/흡연/국내배우흡연모음_video2imgs"
#     output_json_path = "./smoking_detection_results.json"

#     try:
#         results = classify_images_smoking(
#             folder_path,
#             threshold=0.3,
#             display_image=False,
#             output_json_path=output_json_path
#         )
#         print(f"총 {len(results)}개의 이미지가 분석되었습니다.")
#     except FileNotFoundError as e:
#         print(e)
