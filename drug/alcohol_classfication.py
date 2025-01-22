import os
import json
from tqdm import tqdm
from PIL import Image
from transformers import pipeline

def detect_alcohol_in_images(images_path, output_path, checkpoint="google/owlv2-base-patch16-ensemble", score_threshold=0.1):
    """
    이미지에서 알코올 관련 객체를 탐지하고 결과를 JSON 파일로 저장합니다.

    Args:
        images_path (str): 이미지가 저장된 디렉토리 경로.
        output_path (str): JSON 결과를 저장할 파일 경로.
        checkpoint (str): 탐지에 사용할 모델 체크포인트. 기본값은 "google/owlv2-base-patch16-ensemble".
        score_threshold (float): 객체 탐지 점수의 임계값. 기본값은 0.1.

    Returns:
        None
    """
    # 탐지 모델 초기화
    detector = pipeline(model=checkpoint, task="zero-shot-object-detection", batch_size=1)

    # 이미지 디렉토리에서 파일 목록 가져오기
    list_d = os.listdir(path=images_path)
    alcohol_predict = {}

    # 결과를 포맷팅하는 함수 정의
    def format_predictions(image_name, predictions):
        """
        탐지 결과를 알코올 객체 개수와 분류 여부로 포맷팅합니다.

        Args:
            image_name (str): 이미지 파일 이름.
            predictions (list): 탐지된 객체 리스트.

        Returns:
            dict: 알코올 탐지 결과.
        """
        alcohol_count = 0  # 알코올 객체 개수를 초기화
        classification = False  # 기본적으로 분류되지 않은 상태로 설정
        #print(predictions)
        if predictions:  # 탐지 결과가 있을 경우
            for pred in predictions:
                if pred['score'] > score_threshold:  # 점수가 임계값을 초과하는 경우
                    alcohol_count += 1
                    classification = True  # 알코올 객체가 탐지되었음을 표시
        print(image_name,alcohol_count,classification)

        return {
            "image_name": image_name,  # 이미지 이름
            "alcohol_count": alcohol_count,  # 알코올 객체 개수
            "classification": classification  # 탐지 여부
        }
        

    # 각 이미지를 처리
    for image_name in tqdm(list_d, desc="Processing images"):
        image_path = os.path.join(images_path, image_name)  # 이미지 전체 경로 생성
        try:
            image = Image.open(image_path)  # 이미지를 열기
            predictions = detector(image, candidate_labels=["alcohol"])  # 알코올 객체 탐지
            alcohol_predict[image_name] = format_predictions(image_name, predictions)  # 결과 저장
        except Exception as e:
            print(f"Error processing {image_name}: {e}")  # 에러 발생 시 메시지 출력

    # 결과를 JSON 파일로 저장
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(alcohol_predict, json_file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_path}")  # 저장 완료 메시지 출력
    
images_path = 'video_data/술꾼_images_output'
output_path = 'alcohol_predictions_술꾼.json'
detect_alcohol_in_images(images_path, output_path, checkpoint="google/owlv2-base-patch16-ensemble", score_threshold=0.1)






