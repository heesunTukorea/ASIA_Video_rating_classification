from common_processing.video_to_image_text import process_video
from drug.drug_JSON import drug
from drug.Smoking_JSON import classify_images_smoking
from horror.horror_classfication import classify_images_horror
from sexuality.Sexuality_img_JSON import classify_images_sexuality
from imitation_risk.imitaion_risk_result import imitation_risk_api
from topic.Topic_JSON import process_topic
from lines.Lines_SwearWord_JSON import process_lines
from violence.violence_JSON import violence
from violence.violence_text_JSON import violence_text_main
from sexuality.Sexuality_text_JSON import sexuality_text_main
from sexuality.sexuality_combined_JSON import classify_sexuality_combined # sexuality_combined_JSON 추가
import os
from openai import OpenAI
from dotenv import load_dotenv

#인풋데이터
video_path='video_data/연애 빠진 로맨스.mp4'#영상경로
#주제의 인풋데이터
title = '연애 빠진 로맨스' #영상제목
synopsis = '외로운 건 싫지만 연애는 서툰 서른셋 "우리"와 하고는 싶지만 연애가 힘든 스물아홉 "자영", 연애도 일도 까이기 일쑤인 두 남녀가 데이팅 어플을 통해 만나며 시작되는 이야기' #개요
genre='멜로/코미디'#장르

### .env file 로드
load_dotenv()
### API Key 불러오기
openai_api_key = os.getenv('OPENAI_API_KEY')
### OpenAI 함수 호출
client = OpenAI(api_key=openai_api_key)

#경로 및 폴더 이름 설정
base_path = video_path.split("video_data/")[1]
base_name = os.path.splitext(base_path)[0] # 오징어게임
result_folder_path = f"./result/{base_name}"
json_result_path = f'{result_folder_path}/result_json'
images_path = f'{result_folder_path}/{base_name}_images_output'
text_path=f'{result_folder_path}/{base_name}_text_output/{base_name}_text.txt'


#json 파일 경로 설정
json_class_name={'주제':f'{json_result_path}/{base_name}_topic_json.json',
                 '대사':f'{json_result_path}/{base_name}_lines_json.json',
                 '약물_술':f'{json_result_path}/{base_name}_alcohol_json.json',
                 '약물_담배':f'{json_result_path}/{base_name}_smoking_json.json',
                 '약물_마약':f'{json_result_path}/{base_name}_drug_json.json',
                 '폭력_이미지':f'{json_result_path}/{base_name}_violence_img_json.json',
                 '폭력_텍스트':f'{json_result_path}/{base_name}_violence_text_json.json',
                 '모방위험':f'{json_result_path}/{base_name}_imitaion_json.json',
                 '공포':f'{json_result_path}/{base_name}_horror_json.json',
                 '선정성_이미지':f'{json_result_path}/{base_name}_sexuality_img_json.json',
                 '선정성_텍스트':f'{json_result_path}/{base_name}_sexuality_text_json.json', 
                 '선정성_종합':f'{json_result_path}/{base_name}_sexuality_combined_json.json' # 선정성_종합 추가
                 }

#전처리 -위스퍼 -> 이미 데이터 있으면 안해도댐
process_video(input_video_path=video_path) # 이미지 텍스트 추출 whisper api포함
print('전처리 완료')
#대사
process_lines(script_path= text_path, output_path=json_class_name['대사'])
print('대사 완료')
#마약
drug(image_folder_path=images_path, output_file = json_class_name['약물_마약'], threshold=0.3) #클립 마약
print('마약 완료')
#담배
classify_images_smoking(folder_path=images_path,threshold=0.3,display_image=False,output_json_path=json_class_name['약물_담배']) #클립 담배
print('담배 완료')
#공포 이미지
classify_images_horror(image_folder=images_path, output_json_path = json_class_name['공포'])# 클립 호러
print('공포 완료')
#선정성 이미지
classify_images_sexuality(folder_path=images_path, threshold=0.3, display_image=False, output_json_path=json_class_name['선정성_이미지'])# 클립 선정성
print('선정성 이미지 완료')
#폭력 이미지
violence(image_folder_path=images_path, output_file=json_class_name['폭력_이미지'], threshold=0.45)#클립 폭력성
print('폭력 이미지 완료')

#'---------------------------------------gpt-------------------------------------------------------------------------------'

#폭력 텍스트
violence_text_main(text_path=text_path,output_path=json_class_name['폭력_텍스트'])# 폭력 텍스트 gpt
print('폭력 텍스트 완료')
#선정성 텍스트
sexuality_text_main(text_path=text_path,output_path=json_class_name['선정성_텍스트'])# 선정성 텍스트 gpt
print('선정성 텍스트 완료')
#주제
process_topic(text_output_path=text_path,output_json_path=json_class_name['주제'], title=title, synopsis=synopsis, genre=genre)# 주제 gpt
print('주제 완료')

#모방위험 : 이미지가 많기때문에 따로 돌리는거 권장
imitation_risk_api(image_folder=images_path,text_file_path=json_class_name['모방위험']) #모방위험 gpt포함
print('모방위험 완료')

# 선정성 종합 분석 코드 추가
classify_sexuality_combined(image_json_file_path=json_class_name['선정성_이미지'], text_file_path=text_path, output_file=json_class_name['선정성_종합']) # 선정성 종합 gpt
print('선정성 종합 완료')


'''
- 영상제목_topic_json.json
- 영상제목_alcohol_json.json
- 영상제목_drug_json.json
- 영상제목_smoking_json.json
- 영상제목_horror_img_json.json
- 영상제목_imitation_json.json
- 영상제목_lines_json.json
- 영상제목_sexuality_img_json.json
- 영상제목_sexuality_text_json.json
- 영상제목_sexuality_combined_json.json # 추가
- 영상제목_violence_img_json.json
- 영상제목_violence_text_json.json
'''
