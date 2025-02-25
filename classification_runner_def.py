from common_processing.video_to_image_text import process_video
from drug.drug_JSON import drug
from drug.drug_text_JSON import drug_text
from drug.Smoking_JSON import classify_images_smoking
from horror.horror_classfication import classify_images_horror
from sexuality.Sexuality_img_JSON import classify_images_sexuality
from imitation_risk.imitaion_risk_result import imitation_risk_api
from topic.Topic_JSON import process_topic
from lines.lines_JSON import process_script
from violence.violence_JSON import violence
from drug.alcohol_classfication import detect_alcohol_in_images
from rating_classfication.topic_rating_classification import classify_topic_rating 
from rating_classfication.lines_rating_classification import process_dialogue_rating
from rating_classfication.drugs_rating_classification import process_drug_rating
from rating_classfication.horror_rating_classification import get_horror_rating
from rating_classfication.imitaion_risk_rating_classification import imitaion_risk_classify
from rating_classfication.violence_rating_classification import classify_violence_rating
from rating_classfication.sexuality_rating_classification import classify_sexuality_rating
import os
from openai import OpenAI
from dotenv import load_dotenv 
import json
import streamlit as st

#경로,이름,시놉시스,장르,시작시간,시작시간부터 지속 시간,언어    
def classify_run(video_path,title,synopsis,genre,start_time,duration,language):
    ### .env file 로드
    load_dotenv()
    ### API Key 불러오기
    openai_api_key = os.getenv('OPENAI_API_KEY')
    ### OpenAI 함수 호출
    client = OpenAI(api_key=openai_api_key)
    #경로 및 폴더 이름 설정
    base_path = video_path.split("./video_data/")[1] # main함수 실행시
    base_name = os.path.splitext(base_path)[0] # 오징어게임
    result_folder_path = f"C:/Users/chloeseo/ms_project/test_v6/result/{base_name}"
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
                    '약물_마약텍스트':f'{json_result_path}/{base_name}_drug_text_json.json',
                    '폭력_이미지':f'{json_result_path}/{base_name}_violence_img_json.json',
                    '폭력_텍스트':f'{json_result_path}/{base_name}_violence_text_json.json',
                    '모방위험':f'{json_result_path}/{base_name}_imitation_json.json',
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
    #전처리 -위스퍼 -> 이미 데이터 있으면 안해도댐
    
    process_video(input_video_path=video_path,start_time=start_time,duration=duration,language=language) # 이미지 텍스트 추출 whisper api포함
    print('전처리 완료')
    st.write('✔️ 영상 전처리 완료 (1/11)')
    
    #대사
    process_script(script_path= text_path, output_path=json_class_name['대사'])
    print('대사 완료')
    st.write('✔️ 대사 전처리 완료 (2/11)')
    
    #마약 이미지
    drug(image_folder_path=images_path, output_file = json_class_name['약물_마약'], threshold=0.65) #클립 마약
    print('마약 이미지 완료')
    st.write('✔️ 마약 이미지 전처리 완료 (3/11)')
    
    #마약 텍스트
    drug_text(input_file=text_path,output_file = json_class_name['약물_마약텍스트']) #마약 텍스트 gpt
    print('마약 텍스트 완료')
    st.write('✔️ 마약 대사 전처리 완료 (4/11)')
    
    #담배
    classify_images_smoking(folder_path=images_path, output_json_path=json_class_name['약물_담배']) #클립 담배
    print('담배 완료')
    st.write('✔️ 흡연 전처리 완료 (5/11)')
    
    #술
    detect_alcohol_in_images(image_folder=images_path, output_json_path=json_class_name['약물_술'])
    print('술 완료')
    st.write('✔️ 음주 전처리 완료 (6/11)')
    
    #공포 이미지
    classify_images_horror(image_folder=images_path, output_json_path = json_class_name['공포'])# 클립 호러
    print('공포 완료')
    st.write('✔️ 공포 전처리 완료 (7/11)')
    
    #선정성 이미지
    classify_images_sexuality(folder_path=images_path, threshold=0.5, display_image=False, output_json_path=json_class_name['선정성_이미지'])# 클립 선정성
    print('선정성 이미지 완료')
    st.write('✔️ 선정성 전처리 완료 (8/11)')
    
    #폭력성 이미지
    violence(image_folder_path=images_path, output_file=json_class_name['폭력성_이미지'], threshold=0.45)#클립 폭력성
    print('폭력성 이미지 완료')
    st.write('✔️ 폭력성 전처리 완료 (9/11)')
    
    
    #'---------------------------------------gpt-------------------------------------------------------------------------------'
    
    

    #주제
    process_topic(text_output_path=text_path,output_json_path=json_class_name['주제'], title=title, synopsis=synopsis, genre=genre)# 주제 gpt
    print('주제 완료')
    st.write('✔️ 주제 전처리 완료 (10/11)')

    #모방위험 : 이미지가 많기때문에 따로 돌리는거 권장
    imitation_risk_api(image_folder=images_path,text_file_path=text_path, time_interval=1) #모방위험 gpt포함 # ime_interval=1 30초당 1번이면 30으로 변경
    print('모방위험 완료')
    st.write('✔️ 모방위험 전처리 완료 (11/11)')

    st.write('')
    st.write('--------------')
    st.write('✔️ 모든 전처리 완료')
    st.write('--------------')
    st.write('')
    st.write('🔄 등급분류 시작')
    #------------------------------------------최종 분류---------------------------------------------------------------------'
    #주제 등급 분류
    classify_topic_rating(json_file_path=json_class_name['주제'], result_file_path=json_class_name['주제_등급'])
    print('주제 등급 판정 완료')
    st.write('✔️ 주제 등급 판정 완료 (1/7)')
    
    #대사 등급 분류 
    process_dialogue_rating(dialogue_json=json_class_name['대사'],output_json_path=json_class_name['대사_등급'])
    print('대사 등급 판정 완료')
    st.write('✔️ 대사 등급 판정 완료 (2/7)')
    
    #약물 등급 분류 
    process_drug_rating(drug_img_json=json_class_name['약물_마약'], drug_text_json=json_class_name['약물_마약텍스트'], smoking_json=json_class_name['약물_담배'], alcohol_json=json_class_name['약물_술'], output_json_path=json_class_name['약물_등급'])
    print('약물 등급 판정 완료')
    st.write('✔️ 약물 등급 판정 완료 (3/7)')
    
    #공포 등급 분류 
    get_horror_rating(input_json_path=json_class_name['공포'], output_json_path=json_class_name['공포_등급'])
    print('공포 등급 판정 완료')
    st.write('✔️ 공포 등급 판정 완료 (4/7)')
    
    #모방위험 등급 분류 
    imitaion_risk_classify(input_file=json_class_name['모방위험'],input_text_file = text_path, output_file=json_class_name['모방위험_등급'])
    print('모방 위험 등급 판정 완료')
    st.write('✔️ 모방위험 등급 판정 완료 (5/7)')
    
    #폭력성 등급 분류 
    classify_violence_rating(input_img_path=json_class_name['폭력성_이미지'], input_text_path=text_path, result_json_path=json_class_name['폭력성_등급'])
    print('폭력성 등급 판정 완료')
    st.write('✔️ 폭력성 등급 판정 완료 (6/7)')
    
    #선정성 등급 분류 
    classify_sexuality_rating(input_img_path=json_class_name['선정성_이미지'], input_text_path=text_path, output_file=json_class_name['선정성_등급'])
    print('선정성 등급 판정 완료')
    st.write('✔️ 선정성 등급 판정 완료 (7/7)')
    
    #최종 등급 계산
    rating_dict,reason_dict={},{}# 등급 딕셔너리, 이유 딕셔너리
    #각 json을 불러와서 등급과 이유를 할당
    for key, value in json_class_name.items():
        if '_등급' in key:
            key_name = key.split('_')[0]
            try:
                with open(value, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                rating_dict[key_name] = json_data['rating']
                reason_dict[key_name] = json_data['reasoning']
            except:
                pass
    #최종 등급과 등급선정 기준  
    rating_num={'전체관람가':0, '12세이상관람가':12, '15세이상관람가':15, '청소년관람불가':19, '상영제한가':100}# max값 비교를 위한 딕셔너리
    video_rating_num = max([rating_num[i] for i in rating_dict.values()])        
    final_result_rating = [key for key, value in rating_dict.items() if rating_num[value] == video_rating_num ]
    
    
    #----------------------------------------- 결과 출력 -----------------------------------
    #결과
    rating_value=[key for key,value in rating_num.items() if value==video_rating_num][0]
    print(rating_value)# 최종 분류 등급 (ex 전체이용가)
    print(final_result_rating)# 최종 등급 받은 기준 (ex [폭력성,주제])
    print(rating_dict)# 각 기준별 등급 (ex {'주제': '12세이상관람가', '대사': '12세이상관람가', '약물': '12세이상관람가', '폭력성': '12세이상관람가', '모방위험': '12세이상관람가', '공포': '12세이상관람가', '선정성': '12세이상관람가'})
    
    ### 모든 항목에 대한 판정 이유 출력됨
    # #판정 이유 나열
    # reason_list=[]
    # for key,value in reason_dict.items():
    #     reason_text = f'{key}: {value}'
    #     reason_list.append(reason_text)
    #     print(reason_text)# 판정 이유들 출력

    ### 최종 등급에 해당하는 항목만 이유 출력되도록
    # 판정 이유 나열 (최종 등급에 해당하는 항목만 reason_list에 추가)
    reason_list = []
    for key, value in reason_dict.items():
        if key in final_result_rating:  # ✅ 최종 등급에 해당하는 항목만 reason_list에 포함
            reason_text = f'{key}: {value}'
            reason_list.append(reason_text)

    print("최종 reason_list:", reason_list)  # ✅ 최종 리스트 확인 -> streamlit 전달 확인용
    
    return rating_value, final_result_rating, reason_list, rating_dict # 각 기준별 등급도 반환되게 추가

def total_classification_run(video_data_lists):
    try:
        # 리스트 언패킹 오류 방지를 위해 직접 변수 할당
        video_path = video_data_lists[0]
        title = video_data_lists[1]
        synopsis = video_data_lists[2]
        genre = video_data_lists[3]
        start_time = video_data_lists[4] if video_data_lists[4] is not None else 0
        duration = video_data_lists[5] if video_data_lists[5] is not None else 0
        language = video_data_lists[6]

        # `classify_run()` 실행
        rating_value, final_result_rating, reason_list, rating_dict = classify_run(video_path, title, synopsis, genre, start_time, duration, language)

        return rating_value, final_result_rating, reason_list, rating_dict
    except Exception as e:
        print(f"total_classification_run() 실행 중 오류 발생: {e}")
        return None, None, None

# # if __name__ == "__main__":
# #     #영상 그대로 쓸거면 시간 값 None
# #     #경로,이름,시놉시스,장르,시작시간,시작시간부터 지속 시간,언어         
# #     video_data_lists=['C:/Users/chloeseo/ms_project/test_v6/video_data/술꾼도시여자들.mp4',
# #                       '술꾼도시여자들',
# #                       '하루 끝의 술 한잔이 인생의 신념인 세 여자의 일상과 과거를 코믹하게 그려낸 본격 기승전 술 드라마',
# #                       '로맨틱코미디, 우정, 드라마'
# #                       ,None,None,"ko"]  
# #     rating_value, final_result_rating, reason_list = total_classification_run(video_data_lists)#최종등급(ex '전체이용가')(text),최종등급기준(ex ['폭력','공포'])(list),분류 이유(ex ['폭력: .....','공포:.....'])(list)
