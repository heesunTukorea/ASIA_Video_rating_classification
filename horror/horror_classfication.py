import os
import json
from transformers import pipeline
from collections import Counter


def classify_images_horror(image_folder, output_json_path):
#     horror_candidates = [
#     "A scene that evokes psychological fear and suffering",  # 심리적 공포와 고통이 느껴지는 장면
#     "An image that induces tension and anxiety",  # 긴장감과 불안감을 유발하는 이미지
#     "A character with a terrified facial expression",  # 공포에 질린 표정을 짓는 등장인물
#     "A frightening or grotesque scene",  # 무섭거나 혐오스러운 장면
#     "A horror scene with blood and violence",  # 피와 폭력이 포함된 공포 장면
#     "An eerie setting with supernatural elements",  # 초자연적 요소가 포함된 으스스한 환경
#     "A creepy doll or mannequin in a horror-like setting",  # 섬뜩한 인형이나 마네킹이 등장하는 장면
#     "An image featuring ghosts or shadowy figures",  # 유령이나 검은 형체가 등장하는 이미지
#     "A disturbing face with unnatural or deformed features",  # 비정상적이거나 변형된 얼굴을 가진 무서운 캐릭터
#     "A dark atmosphere with threatening elements and horror context",  # 위협적인 요소가 포함된 공포 분위기 (일반적인 어두운 장면과 구별)
#     "A nightmarish scene resembling a horror movie",  # 공포 영화와 유사한 악몽 같은 장면
#     "A terrifying figure lurking in the shadows",  # 그림자 속에서 도사리는 무서운 형체
#     "A sudden appearance of a ghostly or monstrous entity",  # 갑작스럽게 등장하는 유령이나 괴물
#     "A corpse, skeleton, or rotting body in a horror setting",  # 공포스러운 배경 속 시체, 해골, 부패한 몸
#     "An unsettling stare from an unnatural creature",  # 비정상적인 존재의 불길한 응시
#     "A horror figure covered in blood",  # 피에 뒤덮인 공포 캐릭터
#     "A monster or zombie attacking someone",  # 괴물 또는 좀비가 사람을 공격하는 장면
#     "A demonic presence with glowing eyes"  # 빛나는 눈을 가진 악마적 존재
#     # "A horror scene with dark rituals or occult symbols"  # 어둠의 의식이나 오컬트 기호가 등장하는 공포 장면
# ]


#     non_horror_candidates = [
#     "A scene with a peaceful and stable atmosphere",  # 평화롭고 안정적인 분위기의 장면
#     "An image that feels bright and warm",  # 밝고 따뜻한 분위기가 느껴지는 이미지
#     "A natural landscape depicted in tranquility",  # 자연 경관이 평온하게 묘사된 장면
#     "A frame showing everyday and familiar activities",  # 일상적이고 친숙한 활동이 표현된 화면
#     "A scene featuring characters smiling or laughing",  # 웃거나 즐거운 표정을 짓는 등장인물
#     "A cozy and comfortable indoor space",  # 쾌적하고 편안한 실내 공간
#     "An outdoor scene with bright sunlight",  # 밝은 햇살이 비치는 야외 장면
#     "An image completely free of horror elements",  # 공포 요소가 전혀 없는 이미지
#     "A moment conveying joy and comfort",  # 즐거움과 편안함이 느껴지는 순간
#     "An environment that feels pure and safe",  # 순수하고 안전한 환경이 표현된 화면
#     "A character with a casual or neutral expression",  # 무표정하거나 평범한 표정을 짓는 등장인물
#     "A nighttime cityscape with streetlights and no horror elements",  # 공포 요소 없이 단순한 야경 (어두운 장면 오분류 방지)
#     "A dimly lit room that feels cozy rather than scary",  # 어둡지만 무서운 분위기가 없는 방
#     "A character sitting in a dimly lit environment without fear",  # 공포가 느껴지지 않는 어두운 장소의 등장인물
#     "A peaceful night scene with stars in the sky",  # 밤하늘의 별이 빛나는 평화로운 장면
#     "A dark setting that does not evoke horror or fear",  # 공포나 두려움을 유발하지 않는 어두운 장면
#     "A well-lit room with soft shadows and no eerie elements",  # 부드러운 그림자가 있는 따뜻한 실내 공간
#     "A person reading a book in dim lighting",  # 어두운 조명 속에서 책을 읽는 사람 (공포 오분류 방지)
#     "A scene of people enjoying a campfire at night",  # 캠프파이어를 즐기는 사람들
#     "A family watching TV in a dimly lit living room"  # 어두운 거실에서 TV를 보고 있는 가족
# ]

    # horror_candidates = [
    #     # ✅ 심리적 불안과 긴장감을 유발하는 장면
    #     "A scene that evokes psychological fear and suffering",  # 심리적 공포와 고통이 느껴지는 장면
    #     "An image that induces tension and anxiety",  # 긴장감과 불안감을 유발하는 이미지
    #     "a human appears deeply frightened",  # 공포에 질린 등장인물이 등장하는 장면
    #     # "A moment of extreme psychological distress in a character",  # 극심한 심리적 불안이 표현된 장면
    #     "A suspenseful and unsettling moment with an eerie atmosphere",  # 긴장감을 조성하는 불길한 분위기

    #     # ✅ 무섭거나 혐오스러운 장면 (공포 표현 강도에 따른 구분)
    #     "A slightly frightening or grotesque scene",  # 경미한 수준의 무섭거나 혐오스러운 장면 (12세 이상)
    #     "A terrifying and grotesque scene with disturbing elements",  # 무섭고 혐오스러운 요소가 포함된 장면 (15세 이상)
    #     "extreme gore, blood, or body mutilation",  # 극단적인 고어, 유혈, 신체 훼손이 포함된 장면 (청소년 관람불가)

    #     # ✅ 공포 분위기의 음향 및 시각 효과
    #     "A horror scene enhanced by effects visuals",  # 공포 분위기를 조성하는 음향 및 시각 효과
    #     "A jump scare moment designed to startle the audience",  # 갑작스러운 놀람 효과 (점프 스케어)
    #     # "A horror scene with dark rituals or occult symbols",  # 어두운 의식이나 오컬트 기호가 등장하는 장면

    #     # ✅ 공포의 대상 (유령, 괴물, 판타지 크리처 등)
    #     "An image featuring a ghost or shadowy figure in a threatening pose",  # 위협적인 자세의 유령이나 검은 형체
    #     "A supernatural horror scene with demonic presence",  # 악마적인 존재가 포함된 초자연적 공포 장면
    #     "A corpse, skeleton, or rotting body in a horror setting",  # 공포스러운 배경 속 시체, 해골, 부패한 몸
    #     "A monstrous entity with glowing eyes staring menacingly",  # 빛나는 눈을 가진 공포스러운 괴물
    #     "A terrifying fantasy creature with a grotesque appearance",  # 혐오스러운 외양을 가진 공포스러운 판타지 생물체

    #     # ✅ 공포의 강도가 높은 표현 (청소년 관람불가 수준)
    #     "A highly disturbing horror scene with prolonged psychological torture",  # 지속적인 심리적 고문이 포함된 장면
    #     "A horror scene depicting brutal and prolonged violence",  # 잔혹하고 지속적인 폭력 장면
    #     "A scene with extreme fear caused by graphic, gory details",  # 극도로 자극적인 고어 표현이 포함된 장면
    #     "A prolonged scene of relentless fear and psychological trauma",  # 지속적인 공포와 심리적 충격이 포함된 장면
    # ]
    # non_horror_candidates = [
    #     "A scene with a peaceful and stable atmosphere",  # 평화롭고 안정적인 분위기의 장면
    #     "An image that feels bright and warm",  # 밝고 따뜻한 분위기가 느껴지는 이미지
    #     "A natural landscape depicted in tranquility",  # 자연 경관이 평온하게 묘사된 장면
    #     "A frame showing everyday and familiar activities",  # 일상적이고 친숙한 활동이 표현된 화면
    #     "A scene featuring characters smiling or laughing",  # 웃거나 즐거운 표정을 짓는 등장인물
    #     "A cozy and comfortable indoor space",  # 쾌적하고 편안한 실내 공간
    #     "An outdoor scene with bright sunlight",  # 밝은 햇살이 비치는 야외 장면
    #     "A nighttime cityscape with streetlights and no horror elements",  # 공포 요소 없이 단순한 야경
    #     "A dimly lit room that feels cozy rather than scary",  # 어두운 조명 속에서도 공포 분위기가 아닌 장면
    #     "A character sitting in a dimly lit environment without fear",  # 공포가 느껴지지 않는 어두운 장소의 등장인물
    #     "A peaceful night scene with stars in the sky",  # 밤하늘의 별이 빛나는 평화로운 장면
    #     "A dark setting that does not evoke horror or fear",  # 공포나 두려움을 유발하지 않는 어두운 장면
    #     "A well-lit room with soft shadows and no eerie elements",  # 부드러운 그림자가 있는 따뜻한 실내 공간
    #     "A person reading a book in dim lighting",  # 어두운 조명 속에서 책을 읽는 사람 (공포 오분류 방지)
    #     "A scene of people enjoying a campfire at night",  # 캠프파이어를 즐기는 사람들
    #     "A family watching TV in a dimly lit living room",  # 어두운 거실에서 TV를 보고 있는 가족
    #     "A foggy landscape without any ominous or eerie elements",  # 으스스한 요소 없이 단순한 안개 낀 풍경
    #     "A darkened theater with a movie playing",  # 영화가 상영 중인 어두운 극장
    #     "a scene with Amimation character",
    #     # "a Amimation character appears deeply frightened"
    # ]
    horror_candidates = [
        # ✅ 심리적 불안과 긴장감을 유발하는 장면
        # "A scene that evokes psychological fear and suffering",  # 심리적 공포와 고통이 느껴지는 장면
        "A scene with image that induces tension and anxiety",  # 긴장감과 불안감을 유발하는 이미지
        "A scene with people appears deeply frightened",  # 공포에 질린 등장인물이 등장하는 장면
        # "A moment of extreme psychological distress in a character",  # 극심한 심리적 불안이 표현된 장면
        "A scene with suspenseful and unsettling moment with an eerie atmosphere",  # 긴장감을 조성하는 불길한 분위기
        "A violence scene of scenes with some bleeding",

        # ✅ 무섭거나 혐오스러운 장면 (공포 표현 강도에 따른 구분)
        "A scene with slightly frightening or grotesque scene",  # 경미한 수준의 무섭거나 혐오스러운 장면 (12세 이상)
        "A scene with terrifying and grotesque scene with disturbing elements",  # 무섭고 혐오스러운 요소가 포함된 장면 (15세 이상)
        "A scene with horror scene with extreme gore, blood, or body mutilation",  # 극단적인 고어, 유혈, 신체 훼손이 포함된 장면 (청소년 관람불가)

        # ✅ 공포 분위기의 및 시각 효과
        "A scene with horror scene enhanced by effects visuals",  # 공포 분위기를 조성하는 음향 및 시각 효과
        "A scene with horror jump scare moment designed to startle the audience",  # 갑작스러운 놀람 효과 (점프 스케어)
        # "A horror scene with dark rituals or occult symbols",  # 어두운 의식이나 오컬트 기호가 등장하는 장면

        # ✅ 공포의 대상 (유령, 괴물, 판타지 크리처 등)
        "A scene with image featuring a ghost or shadowy figure in a threatening pose",  # 위협적인 자세의 유령이나 검은 형체
        "A scene with supernatural horror scene with demonic presence",  # 악마적인 존재가 포함된 초자연적 공포 장면
        "A scene with corpse, skeleton, or rotting body in a horror setting",  # 공포스러운 배경 속 시체, 해골, 부패한 몸
        "A scene with monstrous entity with glowing eyes staring menacingly",  # 빛나는 눈을 가진 공포스러운 괴물
        "A scene with terrifying fantasy creature with a grotesque appearance",  # 혐오스러운 외양을 가진 공포스러운 판타지 생물체

        # ✅ 공포의 강도가 높은 표현 (청소년 관람불가 수준)
        "A scene with highly disturbing horror scene with prolonged psychological torture",  # 지속적인 심리적 고문이 포함된 장면
        "A scene with depicting brutal and violence",  # 잔혹하고 지속적인 폭력 장면
        "A scene with extreme fear caused by graphic, gory details",  # 극도로 자극적인 고어 표현이 포함된 장면
        "A scene with prolonged scene of relentless fear and psychological trauma",  # 지속적인 공포와 심리적 충격이 포함된 장면
    ]
    non_horror_candidates = [
        'A medical surgical scene',
        "A scene with a peaceful and stable atmosphere",  # 평화롭고 안정적인 분위기의 장면
        "A scene with image that feels bright and warm",  # 밝고 따뜻한 분위기가 느껴지는 이미지
        "A scene with natural landscape depicted in tranquility",  # 자연 경관이 평온하게 묘사된 장면
        "A scene with frame showing everyday and familiar activities",  # 일상적이고 친숙한 활동이 표현된 화면
        "A scene with scene featuring characters smiling or laughing",  # 웃거나 즐거운 표정을 짓는 등장인물
        "A scene with cozy and comfortable indoor space",  # 쾌적하고 편안한 실내 공간
        "A scene with outdoor scene with bright sunlight",  # 밝은 햇살이 비치는 야외 장면
        "A scene with nighttime cityscape with streetlights and no horror elements",  # 공포 요소 없이 단순한 야경
        "A scene with dimly lit room that feels cozy rather than scary",  # 어두운 조명 속에서도 공포 분위기가 아닌 장면
        "A scene with character sitting in a dimly lit environment without fear",  # 공포가 느껴지지 않는 어두운 장소의 등장인물
        "A scene with peaceful night scene with stars in the sky",  # 밤하늘의 별이 빛나는 평화로운 장면
        "A scene with dark setting that does not evoke horror or fear",  # 공포나 두려움을 유발하지 않는 어두운 장면
        "A scene with well-lit room with soft shadows and no eerie elements",  # 부드러운 그림자가 있는 따뜻한 실내 공간
        "A scene with person reading a book in dim lighting",  # 어두운 조명 속에서 책을 읽는 사람 (공포 오분류 방지)
        "A scene of people enjoying a campfire at night",  # 캠프파이어를 즐기는 사람들
        "A scene with family watching TV in a dimly lit living room",  # 어두운 거실에서 TV를 보고 있는 가족
        "A scene with foggy landscape without any ominous or eerie elements",  # 으스스한 요소 없이 단순한 안개 낀 풍경
        "A scene with darkened theater with a movie playing",  # 영화가 상영 중인 어두운 극장
        "A scene with friendly creature with soft, round eyes radiating warmth",  # 부드럽고 둥근 눈을 가진 친근한 생물체  
        "A scene with playful fantasy creature with a charming and whimsical appearance",  # 사랑스럽고 유쾌한 외형을 가진 판타지 생물체  
        "A scene with just jump scare moment",  # 갑작스러운 놀람 효과 (점프 스케어)
        "Scene with Animation",
        "A scene with Animation character appears deeply frightened",
        "A scene of minor physical violence"
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
        
        # 총 페이지 수
    total_pages = len(results)

    # best_caption 값의 등장 횟수
    caption_counts = Counter(item['best_caption'] for item in results)

    # horror_candidates 리스트와 비교하여 공포 관련 best_caption 값 추출
    horror_caption_counts = {caption: caption_counts.get(caption, 0) for caption in horror_candidates}

    # classification 값의 true와 false 개수
    true_count = sum(1 for item in results if item['classification'] is True)
    false_count = total_pages - true_count

    # 비율 계산
    true_rate = round(true_count / total_pages, 2) if total_pages > 0 else 0
    false_rate = round(false_count / total_pages, 2) if total_pages > 0 else 0

    # 요약 결과 생성
    summary = {
        "total_scenes": total_pages,
        "horror_best_caption": horror_caption_counts,
        "non-horror": caption_counts.get("non-horror", 0),
        "horror_rate_true": true_rate,
        "horror_rate_false": false_rate
    }
    results.append(summary)
    # 결과를 JSON 파일로 저장
    with open(output_json_path, "w") as json_file:
        json.dump(results, json_file, indent=4)
    
    print(f"JSON 저장 완료: {output_json_path}")

# 텍스트 후보군 정의

#함수 실행 예시
if __name__ == "__main__":
    image_folder_path = "video_data/범죄도시_images_output"
    output_json_path = "./범죄도시.json"
    
    classify_images_horror(image_folder_path, output_json_path)
    
    
    
# import os
# import json
# from transformers import pipeline
# from collections import Counter


# def classify_images_horror(image_folder, output_json_path):
#     horror_candidates = [
#     "A scene that evokes psychological fear and suffering",  # 심리적 공포와 고통이 느껴지는 장면
#     "An image that induces tension and anxiety",  # 긴장감과 불안감을 유발하는 이미지
#     "A character with a terrified facial expression",  # 공포에 질린 표정을 짓는 등장인물
#     "A frightening or grotesque scene",  # 무섭거나 혐오스러운 장면
#     "A dark atmosphere with threatening elements",  # 어두운 분위기와 위협적인 요소
#     "An image with sudden jump-scare effects",  # 갑작스러운 놀람 효과가 포함된 이미지
#     "An unrealistic and menacing fantasy character",  # 비현실적이고 위협적인 판타지 캐릭터
#     "A visual effect that creates an eerie atmosphere",  # 공포 분위기를 조성하는 시각적 효과
#     "A fantasy creature with a terrifying appearance"  # 무서운 외양을 가진 판타지 생물체
#     ]

#     non_horror_candidates = [
#         "A scene with a peaceful and stable atmosphere",  # 평화롭고 안정적인 분위기의 장면
#         "An image that feels bright and warm",  # 밝고 따뜻한 분위기가 느껴지는 이미지
#         "A natural landscape depicted in tranquility",  # 자연 경관이 평온하게 묘사된 장면
#         "A frame showing everyday and familiar activities",  # 일상적이고 친숙한 활동이 표현된 화면
#         "A scene featuring characters smiling",  # 웃고 있는 등장인물이 나오는 장면
#         "A cozy and comfortable indoor space",  # 쾌적하고 편안한 실내 공간
#         "An outdoor scene with bright sunlight",  # 밝은 햇살이 비치는 야외 장면
#         "An image completely free of horror elements",  # 공포 요소가 전혀 없는 이미지
#         "A moment conveying joy and comfort",  # 즐거움과 편안함이 느껴지는 순간
#         "An environment that feels pure and safe",  # 순수하고 안전한 환경이 표현된 화면
#         "A character with a casual expression" # 아무렇지 않은 표정을 짓고있는 등장인물
#     ]

#     checkpoint = "openai/clip-vit-large-patch14"
#     detector = pipeline(model=checkpoint, task="zero-shot-image-classification")
#     """
#     이미지 폴더 내 모든 이미지를 CLIP 모델로 분류하고 JSON 파일로 저장하는 함수.
    
#     Args:
#         image_folder (str): 이미지 파일이 저장된 폴더 경로.
#         output_json_path (str): 결과를 저장할 JSON 파일 경로.
#         horror_candidates (list): 공포 관련 텍스트 후보군.
#         non_horror_candidates (list): 공포스럽지 않은 텍스트 후보군.
    
#     Returns:
#         None: JSON 파일로 결과를 저장.
#     """
#     # 결과 저장용 리스트
#     results = []
    
#     # 이미지 폴더 내 파일 처리
#     for image_name in sorted(os.listdir(image_folder)):
#         image_path = os.path.join(image_folder, image_name)
        
#         # 이미지 파일만 처리 (예: .png, .jpg, .jpeg)
#         if not image_name.lower().endswith((".png", ".jpg", ".jpeg")):
#             continue
        
#         try:
#             # CLIP 모델로 예측
#             predictions = detector(image_path, candidate_labels=horror_candidates + non_horror_candidates)
#             # 가장 높은 확률과 해당 레이블 추출
#             best_prediction = max(predictions, key=lambda x: x['score'])

#             highest_prob = best_prediction['score']
#             best_caption = best_prediction['label']
#             if best_caption in horror_candidates:
#                 if highest_prob < 0.4:
#                     best_caption = "non-horror"
                    
#             elif best_caption in non_horror_candidates:
#                 best_caption = "non-horror"
            
            
#             # 공포 여부 판단 (True: 공포 관련, False: 공포스럽지 않은)
#             classification = best_caption in horror_candidates
            
            
#             print(f"Image: {image_name}, Classification: {classification}, Best Caption: {best_caption}, Highest Probability: {highest_prob}")
#             # 결과 저장
#             results.append({
#                 "image_name": image_name,
#                 "best_caption": best_caption,
#                 "highest_prob": str(highest_prob),
#                 "classification": classification
#             })
#         except Exception as e:
#             print(f"Error processing {image_name}: {e}")
        
#         # 총 페이지 수
#     total_pages = len(results)

#     # best_caption 값의 등장 횟수
#     caption_counts = Counter(item['best_caption'] for item in results)

#     # horror_candidates 리스트와 비교하여 공포 관련 best_caption 값 추출
#     horror_caption_counts = {caption: caption_counts.get(caption, 0) for caption in horror_candidates}

#     # classification 값의 true와 false 개수
#     true_count = sum(1 for item in results if item['classification'] is True)
#     false_count = total_pages - true_count

#     # 비율 계산
#     true_rate = round(true_count / total_pages, 2) if total_pages > 0 else 0
#     false_rate = round(false_count / total_pages, 2) if total_pages > 0 else 0

#     # 요약 결과 생성
#     summary = {
#         "total_scenes": total_pages,
#         "horror_best_caption": horror_caption_counts,
#         "non-horror": caption_counts.get("non-horror", 0),
#         "horror_rate_true": true_rate,
#         "horror_rate_false": false_rate
#     }
#     results.append(summary)
#     # 결과를 JSON 파일로 저장
#     with open(output_json_path, "w") as json_file:
#         json.dump(results, json_file, indent=4)
    
#     print(f"JSON 저장 완료: {output_json_path}")

# # 텍스트 후보군 정의

# #함수 실행 예시
# if __name__ == "__main__":
#     image_folder_path = "video_data/범죄도시_images_output"
#     output_json_path = "./범죄도시.json"
    
#     classify_images_horror(image_folder_path, output_json_path)
    
    
    