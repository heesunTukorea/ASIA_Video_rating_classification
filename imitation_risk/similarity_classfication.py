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
            images.append(img)
            filenames.append(filename)
    return images, filenames

def calculate_orb_similarity(image1, image2):
    """ORB로 이미지 유사도 계산 (예외 처리 추가)"""
    try:
        image1 = cv2.cvtColor(np.array(image1), cv2.COLOR_RGB2BGR)
        image2 = cv2.cvtColor(np.array(image2), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"ORB 변환 오류: {e}")
        return 0
    
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(image1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(image2, None)

    if descriptors1 is None or descriptors2 is None:
        return 0  

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    similarity = len(matches) / max(len(keypoints1), len(keypoints2))
    return similarity

def calculate_ssim_similarity(image1, image2):
    """SSIM으로 이미지 유사도 계산 (예외 처리 추가)"""
    try:
        image1 = pil_to_numpy(image1)
        image2 = pil_to_numpy(image2)

        if image1.shape != image2.shape:
            return 0  

        gray1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
        ssim_score, _ = ssim(gray1, gray2, full=True)
        return ssim_score
    except Exception as e:
        print(f"SSIM 계산 오류: {e}")
        return 0  

def calculate_adaptive_threshold(similarities, base_threshold=0.5, k=1.0):
    """IQR 기반 이상치 제거 후 적응형 임계값 계산"""
    similarities = np.array(similarities)

    if len(similarities) < 3:  
        return base_threshold  

    q1 = np.percentile(similarities, 25)
    q3 = np.percentile(similarities, 75)
    iqr = q3 - q1
    filtered_similarities = similarities[(similarities >= q1 - 1.5 * iqr) & (similarities <= q3 + 1.5 * iqr)]

    mean_similarity = np.mean(filtered_similarities)
    std_similarity = np.std(filtered_similarities)

    return max(base_threshold, mean_similarity - k * std_similarity)

def detect_scene_transitions(image_folder, output_folder, base_orb_threshold, base_ssim_threshold, min_gap=3, k=1.0):
    """적응형 ORB와 SSIM 임계값을 사용하여 장면 전환 탐지 및 저장"""
    os.makedirs(output_folder, exist_ok=True)

    images, filenames = load_images_from_folder(image_folder)
    scene_transition_images = []
    scene_transition_filenames = []

    orb_similarities = []
    ssim_similarities = []

    last_saved_index = -min_gap  # 연속 저장 방지를 위한 변수

    if images:
        first_image = images[0]
        first_filename = filenames[0]
        first_save_path = os.path.join(output_folder, first_filename)
        first_image.resize((224, 224)).save(first_save_path)
        scene_transition_images.append(first_image)
        scene_transition_filenames.append(first_filename)
        last_saved_index = 0
        print(f"첫 번째 이미지 저장: {first_filename}")

    for i in range(len(images) - 1):
        orb_score = calculate_orb_similarity(images[i], images[i + 1])
        ssim_score = calculate_ssim_similarity(images[i], images[i + 1])

        orb_similarities.append(orb_score)
        ssim_similarities.append(ssim_score)

        print(f"{filenames[i]} ↔ {filenames[i + 1]} | ORB: {orb_score:.2f}, SSIM: {ssim_score:.2f}")

    adaptive_orb_threshold = calculate_adaptive_threshold(orb_similarities, base_orb_threshold, k)
    adaptive_ssim_threshold = calculate_adaptive_threshold(ssim_similarities, base_ssim_threshold, k)

    print(f"적응형 ORB 임계값: {adaptive_orb_threshold:.2f}, SSIM 임계값: {adaptive_ssim_threshold:.2f}")

    for i, (orb_score, ssim_score) in enumerate(zip(orb_similarities, ssim_similarities)):
        if orb_score < adaptive_orb_threshold and ssim_score < adaptive_ssim_threshold:
            if i - last_saved_index >= min_gap:  # 최소 간격(min_gap) 체크
                print(f"장면 전환 탐지: {filenames[i + 1]}")
                scene_transition_images.append(images[i + 1])
                scene_transition_filenames.append(filenames[i + 1])
                last_saved_index = i + 1  # 마지막 저장 인덱스 업데이트

    if len(scene_transition_images) > 90:
        print("추출된 이미지가 90장을 초과하여 SSIM 임계값을 재조정합니다.")
        adaptive_ssim_threshold = np.percentile(ssim_similarities, 10)  

        scene_transition_images = []
        scene_transition_filenames = []
        last_saved_index = -min_gap  # 초기화

        for i, (orb_score, ssim_score) in enumerate(zip(orb_similarities, ssim_similarities)):
            if orb_score < adaptive_orb_threshold and ssim_score < adaptive_ssim_threshold:
                if i - last_saved_index >= min_gap:  # 연속 이미지 방지
                    print(f"장면 전환 재탐지: {filenames[i + 1]} (조정된 SSIM 임계값 적용)")
                    scene_transition_images.append(images[i + 1])
                    scene_transition_filenames.append(filenames[i + 1])
                    last_saved_index = i + 1  

    for img, filename in zip(scene_transition_images, scene_transition_filenames):
        save_path = os.path.join(output_folder, filename)
        img.resize((224, 224)).save(save_path)

    print(f"장면 전환 이미지 {len(scene_transition_images)}개 저장 완료. 경로: {output_folder}")

if __name__ == "__main__":
    image_folder = "result/써니/써니_images_output"
    output_folder = "result/써니/써니_classify"
    base_orb_threshold = 0.3
    base_ssim_threshold = 0.3
    min_gap = 3  # 최소 간격 설정 (연속 저장 방지)

    detect_scene_transitions(image_folder, output_folder, base_orb_threshold, base_ssim_threshold, min_gap)
