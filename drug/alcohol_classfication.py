import os
import json
from transformers import pipeline
from collections import Counter

def detect_alcohol_in_images(image_folder, output_json_path):
    """
    이미지 폴더 내 모든 이미지를 CLIP 모델로 분석하여 음주 관련 여부를 판단하는 함수.

    Args:
        image_folder (str): 이미지 파일이 저장된 폴더 경로.
        output_json_path (str): 결과를 저장할 JSON 파일 경로.

    Returns:
        None: 결과를 JSON 파일로 저장.
    """

    # ✅ 성인 음주 관련 후보군 (0.4 임계값 유지)
    alcohol_candidates = [
        # ✅ 전체이용가 (음주가 거의 없거나 간접적인 수준)
        "A person holding a glass of alcohol or wine or beer but not drinking",  # 술잔을 들고 있지만 마시지 않는 장면
        "A dining table with a bottle of alcohol in the background",  # 배경에 와인병이 놓여 있는 식사 장면
        "A restaurant scene with unopened bottles of alcohol",  # 개봉되지 않은 술병이 있는 레스토랑 장면
        "A bartender preparing drinks at a bar",  # 바에서 바텐더가 술을 준비하는 장면
        "a scene where there's alcohol bottle or alcohol glass",

        # ✅ 12세 이상 관람가 (경미한 음주 장면 포함)
        "A person sipping alcohol or beer",  # 식사 중 와인이나 맥주를 홀짝이는 장면
        "A group of adults casually drinking beer or alcohol",  # 성인들이 가볍게 맥주를 마시는 장면
        "A person toasting with a drink in hand",  # 음료를 들고 건배하는 장면
        "A formal gathering with people drinking alcohol",  # 와인을 마시는 공식적인 모임
        # "A character drinking a small amount of alcohol",  # 적은 양의 술을 마시는 캐릭터
        "There are numerous glasses of alcohol spread across the table.",

        # ✅ 15세 이상 관람가 (음주 빈도가 높거나 취한 상태가 표현되지만 조장하지 않음)
        "A group of people drinking alcohol at a party",  # 파티에서 사람들이 술을 마시는 장면
        "A social scene where alcohol is frequently consumed",  # 사람들이 자주 술을 마시는 사회적 장면
        "A bar scene with people frequently ordering alcoholic drinks",  # 사람들이 계속해서 술을 주문하는 바 장면
        "A person enjoying alcohol in a lounge",  # 라운지에서 칵테일을 즐기는 사람

        # ✅ 청소년 관람불가 (과도한 음주, 취한 상태, 음주 조장)
        "A person engaging in binge drinking",  # 과음하는 장면
        "A group of people encouraging each other to drink more",  # 서로 술을 더 마시도록 유도하는 장면
        "A celebration scene with people excessively drinking",  # 지나치게 술을 마시는 축하 장면

       

    ]
    # ✅ 청소년 음주 관련 후보군 (0.5 임계값 적용)
    teen_alcohol_candidates = [
        "A teenager drinking alcohol at a party",  # 청소년이 파티에서 술을 마시는 장면
        "A group of teenagers consuming alcoholic beverages",  # 젊은 사람들이 함께 술을 마시는 장면
    ]

    # ✅ 비음주(일반적인 장면) 후보군 (청소년 관련 3개 추가)
    non_alcohol_candidates = [
        "It's just a scene where there's bottle or glass",
        "A person drinking water or soda",
        "A character holding a cup of coffee or tea",
        "A family having dinner together with non-alcoholic drinks",
        "A person enjoying a smoothie or juice",
        "A social gathering with no visible alcoholic beverages",
        "A bartender preparing a non-alcoholic cocktail",

        # ✅ 청소년 관련 비음주 장면 (추가된 항목)
        "A teenager drinking juice or soda",  # 청소년이 주스나 탄산음료를 마시는 장면
        "A group of teenagers playing video games",  # 청소년들이 비디오 게임을 하는 장면
        "A teenager studying in a library",  # 청소년이 도서관에서 공부하는 장면
        "a teenager playing at a party",  # 청소년이 파티에서 술을 마시는 장면
        "teenagers playing indoors or outside",
        # "A group of teenagers consuming beverages",
        "A group of teenagers playing",

        # ✅ 일반적인 일상 장면
        "A group of friends chatting in a café",
        "A person reading a book in a cozy environment",
        "A family watching TV together",
        "A couple walking in a park",
        "A person studying at a desk",
        "A child playing with toys",
        "A person working on a laptop in a café",
        "A group of students discussing a project",
        "A person exercising in a gym",
        "A character sitting in a waiting room",
        "A person shopping in a grocery store",
        "A family having a picnic in a park",
        "A person cooking in the kitchen",
        "A group of people dancing at a music festival",
        "A person sipping meal"
    ]

    # CLIP 모델 로드 (ViT-L/14 사용)
    checkpoint = "openai/clip-vit-large-patch14"
    detector = pipeline(model=checkpoint, task="zero-shot-image-classification")

    # 결과 저장 리스트
    results = []

    # 이미지 폴더 내 파일 처리
    for image_name in sorted(os.listdir(image_folder)):
        image_path = os.path.join(image_folder, image_name)

        # 이미지 파일만 처리
        if not image_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        try:
            # CLIP 모델로 예측
            predictions = detector(image_path, candidate_labels=alcohol_candidates + teen_alcohol_candidates + non_alcohol_candidates)

            # 가장 높은 확률의 예측 값 추출
            best_prediction = max(predictions, key=lambda x: x['score'])
            highest_prob = best_prediction['score']
            best_caption = best_prediction['label']

            # 청소년 음주 후보군이면 임계값 0.5 적용
            if best_caption in teen_alcohol_candidates:
                if highest_prob < 0.5:
                    best_caption = "non-alcohol"
            # 성인 음주 후보군이면 기존 0.4 임계값 적용
            elif best_caption in alcohol_candidates:
                if highest_prob < 0.4:
                    best_caption = "non-alcohol"
            # 비음주 장면
            elif best_caption in non_alcohol_candidates:
                best_caption = "non-alcohol"
                # n_best_caption = best_prediction['label']
                # best_caption = "non-alcohol"+n_best_caption
            # 음주 여부 분류
            classification = best_caption in alcohol_candidates + teen_alcohol_candidates

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

    # 총 분석된 이미지 수
    total_images = len(results)

    # best_caption 값의 등장 횟수 계산
    caption_counts = Counter(item['best_caption'] for item in results)

    # 음주 관련 best_caption 값만 필터링
    alcohol_caption_counts = {caption: caption_counts.get(caption, 0) for caption in alcohol_candidates + teen_alcohol_candidates}

    # classification 값의 true(음주 관련), false(비음주) 개수
    true_count = sum(1 for item in results if item['classification'] is True)
    false_count = total_images - true_count

    # 비율 계산
    true_rate = round(true_count / total_images, 2) if total_images > 0 else 0
    false_rate = round(false_count / total_images, 2) if total_images > 0 else 0

    # 요약 결과 생성
    summary = {
        "total_scenes": total_images,
        "alcohol_best_caption": alcohol_caption_counts,
        "non-alcohol": caption_counts.get("non-alcohol", 0),
        "alcohol_rate_true": true_rate,
        "alcohol_rate_false": false_rate
    }

    # JSON 저장
    results.append(summary)
    with open(output_json_path, "w") as json_file:
        json.dump(results, json_file, indent=4)

    print(f"JSON 저장 완료: {output_json_path}")

# ✅ 함수 실행 예시
if __name__ == "__main__":
    image_folder_path = "video_data/음주_images_output"
    output_json_path = "./음주.json"
    
    detect_alcohol_in_images(image_folder_path, output_json_path)

# import os
# import json
# from tqdm import tqdm
# from PIL import Image
# from transformers import pipeline

# def detect_alcohol_in_images(images_path, output_path, checkpoint="google/owlv2-base-patch16-ensemble", score_threshold=0.1):
#     """
#     이미지에서 알코올 관련 객체를 탐지하고 결과를 JSON 파일로 저장합니다.

#     Args:
#         images_path (str): 이미지가 저장된 디렉토리 경로.
#         output_path (str): JSON 결과를 저장할 파일 경로.
#         checkpoint (str): 탐지에 사용할 모델 체크포인트. 기본값은 "google/owlv2-base-patch16-ensemble".
#         score_threshold (float): 객체 탐지 점수의 임계값. 기본값은 0.1.

#     Returns:
#         None
#     """
#     # 탐지 모델 초기화
#     detector = pipeline(model=checkpoint, task="zero-shot-object-detection")

#     # 이미지 디렉토리에서 파일 목록 가져오기
#     list_d = os.listdir(path=images_path)
#     alcohol_predict = []

#     # 결과를 포맷팅하는 함수 정의
#     def format_predictions(image_name, predictions):
#         """
#         탐지 결과를 알코올 객체 개수와 분류 여부로 포맷팅합니다.

#         Args:
#             image_name (str): 이미지 파일 이름.
#             predictions (list): 탐지된 객체 리스트.

#         Returns:
#             dict: 알코올 탐지 결과.
#         """
#         alcohol_count = 0  # 알코올 객체 개수를 초기화
#         classification = False  # 기본적으로 분류되지 않은 상태로 설정
#         #print(predictions)
#         if predictions:  # 탐지 결과가 있을 경우
#             for pred in predictions:
#                 if pred['score'] > score_threshold:  # 점수가 임계값을 초과하는 경우
#                     alcohol_count += 1
#                     classification = True  # 알코올 객체가 탐지되었음을 표시
#         print(image_name,alcohol_count,classification)

#         return {
#             "image_name": image_name,  # 이미지 이름
#             "alcohol_count": alcohol_count,  # 알코올 객체 개수
#             "classification": classification  # 탐지 여부
#         }
        

#     # 각 이미지를 처리
#     for image_name in tqdm(list_d, desc="Processing images"):
#         image_path = os.path.join(images_path, image_name)  # 이미지 전체 경로 생성
#         try:
#             image = Image.open(image_path)  # 이미지를 열기
#             predictions = detector(image, candidate_labels=["alcohol"])  # 알코올 객체 탐지
#             alcohol_predict.append(format_predictions(image_name, predictions))  # 결과 저장
#         except Exception as e:
#             print(f"Error processing {image_name}: {e}")  # 에러 발생 시 메시지 출력
#     total_scenes = len(alcohol_predict)
#     alcohol_true_count = sum(1 for item in alcohol_predict if item['classification'] is True)
#     alcohol_false_count = total_scenes - alcohol_true_count
#     true_rate = round(alcohol_true_count / total_scenes, 2) if total_scenes > 0 else 0
#     false_rate = round(alcohol_false_count / total_scenes, 2) if total_scenes > 0 else 0

#     # Generate summary JSON
#     summary_data = {
#         "total_scenes": total_scenes,
#         "alcohol_true": alcohol_true_count,
#         "alcohol_false": alcohol_false_count,
#         "true_rate": true_rate,
#         "false_rate": false_rate
#     }
#     alcohol_predict.append(summary_data)


#     # 결과를 JSON 파일로 저장
#     with open(output_path, 'w', encoding='utf-8') as json_file:
#         json.dump(alcohol_predict, json_file, ensure_ascii=False, indent=4)

#     print(f"Results saved to {output_path}")  # 저장 완료 메시지 출력
    
# # images_path = 'video_data/술꾼_images_output'
# # output_path = 'alcohol_predictions_술꾼.json'
# #detect_alcohol_in_images(images_path, output_path, checkpoint="google/owlv2-base-patch16-ensemble", score_threshold=0.1)

# ######### 연속 알코올 탐지##########






