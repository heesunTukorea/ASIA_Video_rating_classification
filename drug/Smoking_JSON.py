import os
import json
from tqdm import tqdm
from PIL import Image
from transformers import pipeline

def classify_images_smoking(images_path, output_path, checkpoint="google/owlv2-base-patch16-ensemble", score_threshold=0.1):
    """
    이미지에서 흡연 관련 객체를 탐지하고 결과를 JSON 파일로 저장합니다.

    Args:
        images_path (str): 이미지가 저장된 디렉토리 경로.
        output_path (str): JSON 결과를 저장할 파일 경로.
        checkpoint (str): 탐지에 사용할 모델 체크포인트. 기본값은 "google/owlv2-base-patch16-ensemble".
        score_threshold (float): 객체 탐지 점수의 임계값. 기본값은 0.1.

    Returns:
        None
    """
    # 탐지 모델 초기화
    detector = pipeline(model=checkpoint, task="zero-shot-object-detection")

    # 이미지 디렉토리에서 파일 목록 가져오기
    list_d = os.listdir(path=images_path)
    smoking_predict = []

    # 결과를 포맷팅하는 함수 정의
    def format_predictions(image_name, predictions):
        """
        탐지 결과를 흡연 객체 개수와 분류 여부로 포맷팅합니다.

        Args:
            image_name (str): 이미지 파일 이름.
            predictions (list): 탐지된 객체 리스트.

        Returns:
            dict: 흡연 탐지 결과.
        """
        smoking_count = 0  # 흡연 객체 개수를 초기화
        classification = False  # 기본적으로 분류되지 않은 상태로 설정

        if predictions:  # 탐지 결과가 있을 경우
            for pred in predictions:
                if pred['score'] > score_threshold:  # 점수가 임계값을 초과하는 경우
                    smoking_count += 1
                    classification = True  # 흡연 객체가 탐지되었음을 표시
        print(image_name, smoking_count, classification)

        return {
            "image_name": image_name,  # 이미지 이름
            "smoking_count": smoking_count,  # 흡연 객체 개수
            "classification": classification  # 탐지 여부
        }

    # 각 이미지를 처리
    for image_name in tqdm(list_d, desc="Processing images"):
        image_path = os.path.join(images_path, image_name)  # 이미지 전체 경로 생성
        try:
            image = Image.open(image_path)  # 이미지를 열기
            predictions = detector(image, candidate_labels=["smoking"])  # 흡연 객체 탐지
            smoking_predict.append(format_predictions(image_name, predictions))  # 결과 저장
        except Exception as e:
            print(f"Error processing {image_name}: {e}")  # 에러 발생 시 메시지 출력

    total_scenes = len(smoking_predict)
    smoking_true_count = sum(1 for item in smoking_predict if item['classification'] is True)
    smoking_false_count = total_scenes - smoking_true_count
    true_rate = round(smoking_true_count / total_scenes, 2) if total_scenes > 0 else 0
    false_rate = round(smoking_false_count / total_scenes, 2) if total_scenes > 0 else 0

    # Generate summary JSON
    summary_data = {
        "total_scenes": total_scenes,
        "smoking_true": smoking_true_count,
        "smoking_false": smoking_false_count,
        "true_rate": true_rate,
        "false_rate": false_rate
    }
    smoking_predict.append(summary_data)

    # 결과를 JSON 파일로 저장
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(smoking_predict, json_file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_path}")  # 저장 완료 메시지 출력

# images_path = 'video_data/흡연_images_output'
# output_path = 'smoking_predictions_흡연.json'
# detect_smoking_in_images(images_path, output_path, checkpoint="google/owlv2-base-patch16-ensemble", score_threshold=0.1)
