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
            img = Image.open(file_path)
            if img is not None:
                images.append(img)
                filenames.append(filename)
    return images, filenames

def calculate_ssim_similarity(image1, image2):
    """두 이미지 간의 SSIM 유사도 계산"""
    image1 = pil_to_numpy(image1)
    image2 = pil_to_numpy(image2)
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    ssim_score, _ = ssim(gray1, gray2, full=True)
    return ssim_score

def calculate_histogram_similarity(image1, image2):
    """두 이미지 간의 히스토그램 유사도 계산"""
    image1 = pil_to_numpy(image1)
    image2 = pil_to_numpy(image2)
    hsv1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
    hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 60], [0, 180, 0, 256])
    hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 60], [0, 180, 0, 256])
    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similarity

def calculate_combined_similarity(image1, image2):
    """SSIM과 히스토그램 유사도를 결합하여 계산"""
    ssim_score = calculate_ssim_similarity(image1, image2)
    histogram_score = calculate_histogram_similarity(image1, image2)
    combined_score = 0.7 * ssim_score + 0.3 * histogram_score
    return combined_score

def detect_scene_transitions(image_folder, output_folder, similarity_threshold=0.6):
    """유사도 기반으로 장면 전환을 탐지하고 전환 이미지를 저장"""
    os.makedirs(output_folder, exist_ok=True)

    images, filenames = load_images_from_folder(image_folder)
    scene_transition_images = []
    scene_transition_filenames = []

    # 첫 번째 이미지를 기본적으로 저장
    if images:
        first_image = images[0]
        first_filename = filenames[0]
        first_save_path = os.path.join(output_folder, first_filename)
        first_image.resize((224, 224)).save(first_save_path)  # 저장 시 리사이즈
        print(f"첫 번째 이미지 저장: {first_filename}")

    # 이미지 간 유사도를 계산하여 장면 전환 탐지
    for i in range(len(images) - 1):
        similarity = calculate_combined_similarity(images[i], images[i + 1])
        print(f"{filenames[i]}와 {filenames[i + 1]}의 유사도: {similarity:.2f}")

        # 유사도가 임계값보다 낮으면 장면 전환으로 간주
        if similarity < similarity_threshold:
            scene_transition_images.append(images[i + 1])
            scene_transition_filenames.append(filenames[i + 1])

    # 장면 전환 이미지를 저장
    for img, filename in zip(scene_transition_images, scene_transition_filenames):
        save_path = os.path.join(output_folder, filename)
        img.resize((224, 224)).save(save_path)  # 저장 시 리사이즈

    print(f"장면 전환 이미지가 {len(scene_transition_images)+1}개 저장되었습니다. 경로: {output_folder}")

if __name__ == "__main__":
    # 예제 실행 코드
    image_folder = "result/써니/써니_images_output"  # 입력 이미지 폴더 경로
    output_folder = "result/써니/써니_classify"  # 출력 폴더 경로
    similarity_threshold = 0.5  # 유사도 임계값

    detect_scene_transitions(image_folder, output_folder, similarity_threshold)
