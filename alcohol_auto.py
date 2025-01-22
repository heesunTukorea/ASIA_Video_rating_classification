import os
from common_processing.video_to_image_text import extract_images
from drug.alcohol_classfication import detect_alcohol_in_images
#video_data에 있는 모든 영상 리스트를 가져와서 실행 
def alcohol_auto_code():
    videos_path='video_data'
    video_list=os.listdir(videos_path)
    
    for index,video in enumerate(video_list):
        #경로설정 관련 부분  
        base_name = os.path.splitext(video)[0] # 오징어게임
        video_path =  f'{videos_path}/{video}' # video_data/오징어게임.mp4
        print(base_name +' 시작')
        #result폴더 생성
        os.makedirs(f"./result", exist_ok=True)
        result_folder_path = f"./result/{base_name}"
        os.makedirs(result_folder_path, exist_ok=True)
        #이미지 분할 생성 경로
        output_images_path = result_folder_path + f"/{base_name}_images_output" + f"/frame_%03d.png"
        images_output_folder=os.path.dirname(output_images_path)
        os.makedirs(images_output_folder, exist_ok=True)
        #json 결과 폴더 미리 생성
        json_result_path= result_folder_path+"/result_json"
        os.makedirs(json_result_path, exist_ok=True)
        #영상에서 이미지 분할
        extract_images(video_path, output_images_path)
        
        #알코올 분류 코드
        output_path = f'{json_result_path}/{base_name}_alcohol_json.json' 
        detect_alcohol_in_images(images_output_folder, output_path, checkpoint="google/owlv2-base-patch16-ensemble", score_threshold=0.1)
        print(f'{index}/{len(video_list)}, {base_name} 완료')