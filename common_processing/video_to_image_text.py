import os
import subprocess
from datetime import timedelta
from openai import OpenAI
import json
from dotenv import load_dotenv
import glob

def open_ai_load():
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI()
    whisper_client = client 
    return whisper_client

def create_dirs(base_path, relative_path):
    base_name = os.path.splitext(relative_path)[0]  
    os.makedirs(f"./result", exist_ok=True)
    result_folder_path = f"./result/{base_name}"
    os.makedirs(result_folder_path, exist_ok=True)
    output_audio_path = result_folder_path + f"/{base_name}_audio_output/{base_name}_audio.mp3"
    output_images_path = result_folder_path + f"/{base_name}_images_output/frame_%03d.png"
    output_text_path = result_folder_path + f"/{base_name}_text_output/{base_name}_text.txt"
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_images_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_text_path), exist_ok=True)
    os.makedirs(result_folder_path+"/result_json", exist_ok=True)
    return output_audio_path, output_images_path, output_text_path

def get_video_duration(input_video_path):
    """ ffmpeg를 사용하여 영상 길이를 가져오는 함수 """
    try:
        # ffmpeg 실행 후 stderr에서 Duration 정보 추출
        result = subprocess.run(
            ["ffmpeg", "-i", input_video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if not result.stderr:
            print("❌ ffmpeg 실행 중 오류 발생: stderr가 없습니다.")
            return 0

        # Duration이 포함된 라인 찾기
        duration_line = next((line for line in result.stderr.split("\n") if "Duration" in line), None)

        if duration_line:
            try:
                print(f"🔍 ffmpeg 출력에서 찾은 Duration 라인: {duration_line}")
                duration_str = duration_line.split(",")[0].split("Duration:")[1].strip()
                h, m, s = map(float, duration_str.split(":"))
                video_length = h * 3600 + m * 60 + s
                print(f"🎬 영상 길이: {video_length:.2f}초")
                return video_length
            except (ValueError, IndexError) as e:
                print(f"❌ 시간 변환 중 오류 발생: {e}")
                return 0
        else:
            print("❌ Duration 정보를 찾을 수 없습니다.")
            return 0

    except Exception as e:
        print(f"⚠️ 예외 발생: {e}")
        return 0



def extract_images(input_video_path, output_images_path, start_time=None, duration=None):
    # 전체 영상 길이 확인
    total_duration = get_video_duration(input_video_path)
    
    # 처리할 구간이 특정된 경우, 해당 구간만을 기준으로 fps 설정
    if start_time or duration:
        video_duration = duration if duration else total_duration - float(start_time or 0)
    else:
        video_duration = total_duration

    # FPS 설정: 1시간 이상이면 10초당 1장, 1시간 미만이면 1초당 1장
    fps = "1" if video_duration < 3600 else "1/10"

    print(f"🔍 영상 길이: {video_duration}초, FPS 설정: {fps}")

    command = ["ffmpeg", "-i", input_video_path, "-vf", f"fps={fps}"]

    if start_time:
        command.extend(["-ss", str(start_time)])
    if duration:
        command.extend(["-t", str(duration)])

    command.append(output_images_path)

    return subprocess.run(command)


# 오디오 추출 (ffmpeg)
def extract_audio_segments(input_video_path, output_audio_base_path, segment_duration=600):
    """ FFMPEG를 사용해 오디오를 segment_duration(초) 단위로 나눠 저장 """
    os.makedirs(os.path.dirname(output_audio_base_path), exist_ok=True)
    
    command = [
        "ffmpeg", "-i", input_video_path,
        "-f", "segment", "-segment_time", str(segment_duration),
        "-c:a", "libmp3lame", "-b:a", "192k", "-ac", "2",  # ✅ MP3 인코딩 강제 적용 & 스테레오 변환
        f"{output_audio_base_path}_%03d.mp3"
    ]
    
    return subprocess.run(command)

def transcribe_audio_segments(client, output_audio_base_path, language):
    """ 여러 개의 오디오 세그먼트를 Whisper로 변환 (실제 영상 시간 기준) """
    audio_files = sorted(glob.glob(f"{output_audio_base_path}_*.mp3"))  # 오디오 파일 정렬
    full_transcription = []

    for idx, audio_file in enumerate(audio_files):
        with open(audio_file, "rb") as f:
            print(f"🎙 Whisper 처리 중: {audio_file}")
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=f,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )

            # 현재 오디오 파일의 시작 오프셋 (idx * segment_duration 초)
            offset = idx * 600  # 10분(600초) 단위로 오프셋 추가
            for segment in transcription.segments:
                segment.start += offset
                segment.end += offset

            full_transcription.append(transcription)

    return full_transcription

def format_time(seconds):
    return str(timedelta(seconds=int(seconds))).zfill(8)

def write_text(output_text_path, results):
    with open(output_text_path, 'w', encoding='utf-8') as f:
        for result in results:
            for segment in result.segments:
                start_time = format_time(segment.start)
                end_time = format_time(segment.end)
                text = segment.text
                f.write(f"[{start_time} - {end_time}]  {text}\n")
                print(f"[{start_time} - {end_time}]  {text}")

def process_video(input_video_path, start_time=None, duration=None, language='ko'):
    client = open_ai_load()
    base_path, relative_path = input_video_path.split("video_data/")

    # 파일 확장자 확인 및 변환 (.mkv → .mp4)
    base_name, file_extension = os.path.splitext(relative_path)  # 확장자 추출
    
    if file_extension.lower() == ".mkv":
        converted_video_path = f"video_data/{base_name}.mp4"
        
        # `.mkv`를 `.mp4`로 변환
        command = [
            "ffmpeg", "-i", input_video_path, "-c:v", "copy", "-c:a", "aac", converted_video_path
        ]
        
        if subprocess.run(command).returncode == 0:
            print(f"✅ {input_video_path} → {converted_video_path} 변환 완료")
            input_video_path = converted_video_path  # 변환된 파일 경로 사용
        else:
            print("❌ MKV 변환 중 오류 발생")
            return
    
    # 디렉토리 생성 및 경로 반환
    output_audio_base_path, output_images_path, output_text_path = create_dirs(base_path, relative_path)

    # 오디오 추출 (긴 오디오는 여러 개의 조각으로 나눔)
    if extract_audio_segments(input_video_path, output_audio_base_path, segment_duration=600).returncode == 0:
        print("🔊 오디오 분할 및 추출 완료")
    else:
        print("❌ 오디오 추출 중 오류 발생")

    # 이미지 추출
    if extract_images(input_video_path, output_images_path, start_time, duration).returncode == 0:
        print("📸 이미지 추출 완료")
    else:
        print("❌ 이미지 추출 중 오류 발생")

    #Whisper로 텍스트 변환 (분할된 오디오 파일 처리)
    results = transcribe_audio_segments(client, output_audio_base_path, language=language)
    
    write_text(output_text_path, results)
    print("✅ 프로세스 완료")


# import한 후 호출 예시
# from this_module import process_video
# process_video("video_data/타짜(신의손).mp4",)
#video_data 폴더 만들고 영상넣으시면됩니다
