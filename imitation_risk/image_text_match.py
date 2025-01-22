import os
from datetime import timedelta
import re
import json

# 시간 문자열을 초 단위로 변환하는 함수
def time_to_seconds(time_str):
    """시간 문자열을 초 단위로 변환"""
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

# 텍스트 파일에서 대사 데이터를 파싱하는 함수
def parse_script(file_path):
    """텍스트 파일에서 대사 데이터를 파싱"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    script = []
    time_pattern = re.compile(r"\[(\d{2}:\d{2}:\d{2}) - (\d{2}:\d{2}:\d{2})\]\s*(.*)")

    for line in lines:
        match = time_pattern.match(line)
        if match:
            start_time = time_to_seconds(match.group(1))
            end_time = time_to_seconds(match.group(2))
            text = match.group(3)
            script.append((start_time, end_time, text))

    return script

# 이미지 파일과 대사를 매칭하는 함수
def match_images_with_script(image_folder, script):
    """이미지 파일과 대사를 매칭"""
    matched_data = []

    # 이미지 파일 정렬
    image_files = sorted(
        [f for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
    )

    for image_file in image_files:
        # 이미지 파일명에서 시간 추출 (예: "오징어게임시즌2_001.png" -> 001)
        match = re.search(r"_(\d{3})", image_file)
        if match:
            image_time = int(match.group(1))  # 초 단위로 변환

            # 해당 시간에 포함된 대사를 찾음
            matched = False
            for start_time, end_time, text in script:
                if start_time <= image_time < end_time:
                    matched_data.append({"image_path": image_folder + '/' + image_file, "text": text})
                    matched = True
                    break

            # 매칭되는 시간이 없으면 "대사없음"으로 설정
            if not matched:
                matched_data.append({"image_path": image_folder + '/' + image_file, "text": "대사없음"})

    return matched_data

# 매칭 결과를 파일로 저장하는 함수
def save_matched_data(output_file_path, matched_data):
    """매칭 결과를 JSON 파일로 저장"""
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(matched_data, f, ensure_ascii=False, indent=4)

# 메인 실행 함수
def process_matching(image_folder, text_file_path, output_file_path):
    """이미지와 대사를 매칭하고 결과를 저장"""
    # 텍스트 파일에서 대사 파싱
    script = parse_script(text_file_path)

    # 이미지와 대사 매칭
    matched_data = match_images_with_script(image_folder, script)

    # 매칭 결과 저장
    save_matched_data(output_file_path, matched_data)
    return matched_data

if __name__ == "__main__":
    # 예제 실행
    image_folder = "video_data/오징어게임_ssim_hist"  # 이미지 파일 경로
    text_file_path = "video_data/오징어게임시즌2 text_output/오징어게임시즌2 _text.txt"  # 텍스트 파일 경로
    output_file_path = "video_data/matched.json"  # 결과 저장 파일 경로

    result = process_matching(image_folder, text_file_path, output_file_path)
    for item in result:
        print(item)
