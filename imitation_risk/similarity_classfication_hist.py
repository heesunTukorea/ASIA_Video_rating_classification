import os
import cv2
import numpy as np
from PIL import Image

# 이미지 폴더 경로
image_folder = "C:/Users/fprkwk/aisa_ms_project/video_data/오징어게임시즌2 _images_output"

# 장면 전환으로 간주할 유사도 임계값 (0~1, 낮을수록 엄격)
similarity_threshold = 0.5

# 장면 전환 이미지를 저장할 폴더 경로
output_folder = "C:/Users/fprkwk/aisa_ms_project/video_data/classify_hist"
os.makedirs(output_folder, exist_ok=True)

# 이미지 로드 함수
def load_images_from_folder(folder_path):
    images = []
    filenames = []
    for filename in sorted(os.listdir(folder_path)):
        file_path = folder_path + '/' + filename
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file_path)
            if img is not None:
                images.append(img)
                filenames.append(filename)
    return images, filenames

def pil_to_numpy(image):
    return np.array(image)
# Histogram 비교 함수
def calculate_histogram_similarity(image1, image2):
    # 이미지를 HSV 색상 공간으로 변환
    image1 = pil_to_numpy(image1)
    image2 = pil_to_numpy(image2)
    hsv1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)

    # 히스토그램 계산 (H, S 채널만 사용)
    hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 60], [0, 180, 0, 256])
    hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 60], [0, 180, 0, 256])

    # 히스토그램 정규화
    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    # 히스토그램 비교 (코사인 유사도 사용)
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similarity

# 이미지 로드
images, filenames = load_images_from_folder(image_folder)

# 결과를 저장할 리스트
scene_transition_images = []
scene_transition_filenames = []

# 이미지 유사도를 계산하여 장면 전환 감지
for i in range(len(images) - 1):
    similarity = calculate_histogram_similarity(images[i], images[i + 1])
    print(f"{filenames[i]}와 {filenames[i + 1]}의 유사도: {similarity:.2f}")

    # 유사도가 임계값보다 낮으면 장면 전환으로 간주
    if similarity < similarity_threshold:
        scene_transition_images.append(images[i + 1])
        scene_transition_filenames.append(filenames[i + 1])

# 장면 전환 이미지 저장
for img, filename in zip(scene_transition_images, scene_transition_filenames):
    save_path = output_folder + '/' + filename
    img.save(save_path)

print(f"장면 전환 이미지가 {len(scene_transition_images)}개 저장되었습니다. 경로: {output_folder}")
