import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image

def pil_to_numpy(image):
    """PIL 이미지를 NumPy 배열로 변환"""
    return np.array(image)

def load_images_from_folder(folder_path):
    """폴더에서 이미지를 로드하고 파일 이름과 함께 반환"""
    images = []
    filenames = []
    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file_path).convert("RGB")
            if img is not None:
                images.append(img)
                filenames.append(filename)
    return images, filenames

def calculate_orb_similarity(image1, image2):
    """ORB로 이미지 유사도 계산"""
    # PIL 이미지를 OpenCV 이미지로 변환
    image1 = cv2.cvtColor(np.array(image1), cv2.COLOR_RGB2BGR)
    image2 = cv2.cvtColor(np.array(image2), cv2.COLOR_RGB2BGR)

    # ORB 생성
    orb = cv2.ORB_create()

    # 특징점과 디스크립터 계산
    keypoints1, descriptors1 = orb.detectAndCompute(image1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(image2, None)

    # 디스크립터 매칭
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    if descriptors1 is None or descriptors2 is None:
        return 0  # 디스크립터가 없는 경우 유사도 0 반환

    matches = bf.match(descriptors1, descriptors2)

    # 매칭 결과를 거리 기준으로 정렬
    matches = sorted(matches, key=lambda x: x.distance)

    # 유사도 계산 (매칭된 특징점의 비율 사용)
    similarity = len(matches) / max(len(keypoints1), len(keypoints2))
    return similarity

def calculate_ssim_similarity(image1, image2):
    """SSIM으로 이미지 유사도 계산"""
    image1 = pil_to_numpy(image1)
    image2 = pil_to_numpy(image2)
    gray1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    ssim_score, _ = ssim(gray1, gray2, full=True)
    return ssim_score

def calculate_adaptive_threshold(similarities, base_threshold=0.5, k=1.0):
    """유사도 평균과 표준편차를 기반으로 적응형 임계값 계산"""
    mean_similarity = np.mean(similarities)
    std_similarity = np.std(similarities)
    adaptive_threshold = max(base_threshold, mean_similarity - k * std_similarity)
    return adaptive_threshold

def detect_scene_transitions(image_folder, output_folder, base_orb_threshold, base_ssim_threshold, k=1.0):
    """적응형 ORB와 SSIM 임계값을 사용하여 장면 전환 탐지 및 저장"""
    os.makedirs(output_folder, exist_ok=True)

    images, filenames = load_images_from_folder(image_folder)
    scene_transition_images = []
    scene_transition_filenames = []

    orb_similarities = []
    ssim_similarities = []

    # 첫 번째 이미지는 저장
    if images:
        first_image = images[0]
        first_filename = filenames[0]
        first_save_path = os.path.join(output_folder, first_filename)
        first_image.resize((224, 224)).save(first_save_path)
        print(f"첫 번째 이미지 저장: {first_filename}")

    # ORB와 SSIM 유사도 계산
    for i in range(len(images) - 1):
        orb_score = calculate_orb_similarity(images[i], images[i + 1])
        orb_similarities.append(orb_score)

        ssim_score = calculate_ssim_similarity(images[i], images[i + 1])
        ssim_similarities.append(ssim_score)

        print(f"{filenames[i]}와 {filenames[i + 1]}의 ORB 유사도: {orb_score:.2f}, SSIM 유사도: {ssim_score:.2f}")

    # 적응형 임계값 계산
    adaptive_orb_threshold = calculate_adaptive_threshold(orb_similarities, base_orb_threshold, k)
    adaptive_ssim_threshold = calculate_adaptive_threshold(ssim_similarities, base_ssim_threshold, k)

    print(f"적응형 ORB 임계값: {adaptive_orb_threshold:.2f}, SSIM 임계값: {adaptive_ssim_threshold:.2f}")

    # 장면 전환 탐지
    for i, (orb_score, ssim_score) in enumerate(zip(orb_similarities, ssim_similarities)):
        if orb_score < adaptive_orb_threshold and ssim_score < adaptive_ssim_threshold:
            print(f"장면 전환 탐지: {filenames[i + 1]} (적응형 ORB+SSIM 기준)")
            scene_transition_images.append(images[i + 1])
            scene_transition_filenames.append(filenames[i + 1])

    # 이미지가 90장이 넘는 경우 SSIM 임계값 낮추기
    if len(scene_transition_images) > 90:
        print("추출된 이미지가 90장을 초과하여 SSIM 임계값을 0.2 낮춥니다.")
        adaptive_ssim_threshold -= 0.2
        scene_transition_images = []
        scene_transition_filenames = []

        for i, (orb_score, ssim_score) in enumerate(zip(orb_similarities, ssim_similarities)):
            if orb_score < adaptive_orb_threshold and ssim_score < adaptive_ssim_threshold:
                print(f"장면 전환 재탐지: {filenames[i + 1]} (임계값 조정 후)")
                scene_transition_images.append(images[i + 1])
                scene_transition_filenames.append(filenames[i + 1])

    # 장면 전환 이미지를 저장
    for img, filename in zip(scene_transition_images, scene_transition_filenames):
        save_path = os.path.join(output_folder, filename)
        img.resize((224, 224)).save(save_path)

    print(f"장면 전환 이미지가 {len(scene_transition_images)+1}개 저장되었습니다. 경로: {output_folder}")

if __name__ == "__main__":
    # 예제 실행 코드
    image_folder = "result/써니/써니_images_output"  # 입력 이미지 폴더 경로
    output_folder = "result/써니/써니_classify"  # 출력 폴더 경로
    base_orb_threshold = 0.3  # 기본 ORB 유사도 임계값
    base_ssim_threshold = 0.3  # 기본 SSIM 유사도 임계값

    detect_scene_transitions(image_folder, output_folder, base_orb_threshold, base_ssim_threshold)
