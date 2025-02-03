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
from rating_classfication.topic_rating_classification import classify_topic_rating  # ✅ 추가된 부분

import os
from openai import OpenAI
from dotenv import load_dotenv

### 30일
#인풋데이터
video_path='/video_data/30일.mp4'#영상경로
#주제의 인풋데이터
title = '30일' #영상제목
synopsis = '''“완벽한 저에게 신은 저 여자를 던지셨죠” 지성과 외모 그리고 찌질함까지 타고난, '정열'(강하늘). 
“모기 같은 존재죠. 존재의 이유를 모르겠는?” 능력과 커리어 그리고 똘기까지 타고난, '나라'(정소민). 
영화처럼 만나 영화같은 사랑을 했지만 서로의 찌질함과 똘기를 견디다 못해 마침내 완벽한 남남이 되기로 한다. 
그러나! 완벽한 이별을 딱 D-30 앞둔 이들에게 찾아온 것은... 동반기억상실?
'''
genre='코미디' #장르


#####################################################################################################################

### .env file 로드
load_dotenv()
### API Key 불러오기
openai_api_key = os.getenv('OPENAI_API_KEY')
### OpenAI 함수 호출
client = OpenAI(api_key=openai_api_key)

#경로 및 폴더 이름 설정
base_path = video_path.split("video_data/")[1]
base_name = os.path.splitext(base_path)[0] # 오징어게임
result_folder_path = f"/result/{base_name}"
json_result_path = f'{result_folder_path}/result_json'
images_path = f'{result_folder_path}/{base_name}_images_output'
text_path=f'{result_folder_path}/{base_name}_text_output/{base_name}_text.txt'
rating_result_path = f'{result_folder_path}/rating_result' # rating_result 폴더 생성

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
                
                # ✅ 추가된 부분    
                 '주제_등급':f'{rating_result_path}/{base_name}_topic_rating.json', 
                 '대사_등급':f'{rating_result_path}/{base_name}_lines_rating.json' ,
                 '약물_등급':f'{rating_result_path}/{base_name}_drug_rating.json' ,
                 '폭력_등급':f'{rating_result_path}/{base_name}_violence_rating.json' ,
                 '모방위험_등급':f'{rating_result_path}/{base_name}_imitation_rating.json' ,
                 '공포_등급':f'{rating_result_path}/{base_name}_horror_rating.json' ,
                 '선정성_등급':f'{rating_result_path}/{base_name}_sexuality_rating.json' 
                 }

############################################# 기준별 전처리 ######################################################
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

# #'---------------------------------------gpt-------------------------------------------------------------------------------'

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
imitation_risk_api(image_folder=images_path,text_file_path=text_path) #모방위험 gpt포함
print('모방위험 완료')

print('모든 작업 완료')


############################################# 최종 등급 판정 ######################################################
# 주제 
classify_topic_rating(json_file_path=json_class_name['주제'], result_file_path=json_class_name['주제_등급'])
print('주제 등급 판정 완료')

# 대사


# 약물


# 폭력


# 모방위험


# 공포


# 선정성

