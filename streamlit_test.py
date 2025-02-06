import streamlit as st
import base64
from PIL import Image
from classification_runner_def import total_classification_run
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# base64 인코딩 함수
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        st.write(f"파일을 찾을 수 없습니다: {image_path}")
        return None

# 기본 정보 표시 함수
def display_basic_info(analysis_results, cols):
    for i, col in enumerate(cols):
        with col:
            keys = ["구분", "한글제명/원재명", "신청사", "대표", "등급분류일자", "관람등급"] if i == 0 else ["등급분류번호/유해확인번호", "상영시간(분)", "감독", "감독국적", "주연", "주연국적", "계약연도", "정당한권리자", "제작년도"]
            for key in keys:
                st.write(f"**{key}:** {analysis_results.get(key, '데이터 없음')}")

# 🔹 등급 분석 실행 함수
def process_video_classification():
    input_data = st.session_state["input_data"]
    uploaded_file = st.session_state["uploaded_file"]

    if uploaded_file:
        upload_folder = "C:/Users/chloeseo/ms_project/test_v6/st_upload_file/"
        os.makedirs(upload_folder, exist_ok=True)  # 폴더가 없으면 생성

        video_path = os.path.join(upload_folder, uploaded_file.name)  # 업로드된 파일 저장 경로 설정
        with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        print(f"✅ 업로드된 파일 저장 완료: {video_path}")
        # 🔹 `total_classification_run()`에 전달할 입력값 구성
        video_data_lists = [
            video_path,
            input_data["제목"],
            input_data["시놉시스"],  
            input_data["장르"],
            input_data["분석 시작 시간"],
            input_data["분석 지속 시간"],
            input_data["영상 언어"][:2]
        ]
        
        # 🔹 `total_classification_run()` 실행하여 분석 결과 얻기
        try:
            rating_value, final_result_rating, reason_list, rating_dict = total_classification_run(video_data_lists)
            # ✅ `None`이 반환되었을 경우 오류 메시지 출력
            if rating_value is None or final_result_rating is None or reason_list is None:
                st.error("🚨 등급 분석 실행 중 오류 발생: 분석 결과가 없습니다.")
                return
        except Exception as e:
            st.error(f"등급 분류 실행 중 오류 발생: {e}")
            return
        
        # 📌 현재 날짜 가져오기 (YYYY-MM-DD 형식)
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # 🔹 분석 결과 저장
        st.session_state["analysis_results"] = {
            "구분": input_data["구분"],
            "한글제명/원재명": input_data["제목"],
            "신청사": input_data["신청사"],
            "시놉시스": input_data["시놉시스"],
            "등급분류일자": today_date,  # 현재 날짜 자동 설정
            "접수일자" : today_date,
            "관람등급": rating_value,
            "감독": input_data["감독"],  
            "감독 국적": input_data["감독 국적"],  
            "주연 배우": input_data["주연 배우"],  
            "주연 배우 국적": input_data["주연 배우 국적"],  
            "내용정보 탑3": {criterion: rating_value for criterion in final_result_rating},
            "내용정보": rating_dict,  # ✅ 모든 기준별 등급 포함
            "서술적 내용기술": "\n".join(reason_list) if reason_list else "데이터 없음",
            "대표" : input_data["대표"]
        }
        # 🔹 결과 페이지로 이동
        st.write("등급 분류 요청이 제출되었습니다!")
        st.query_params["page"] = "result"
        st.rerun()

# 페이지 상태 관리 및 세션 상태 초기화
page = st.query_params.get("page", "")
if "input_data" not in st.session_state:
    st.session_state["input_data"] = {}
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = {}
if "uploaded_file" not in st.session_state:  # 🔥 오류 방지를 위해 초기화
    st.session_state["uploaded_file"] = None

# 메인 페이지
if page == "":
    st.title("비디오 등급 분류 시스템")
    try:
        image = Image.open("C:/Users/chloeseo/Downloads/서비스이미지.png")  # 실제 이미지 파일 경로로 변경
        st.image(image, use_container_width=True)
    except FileNotFoundError:
        st.write(" ")
    st.write("비디오 콘텐츠에 적절한 등급을 지정하는 시스템입니다. 아래 버튼을 클릭하여 시작하세요.")

    if st.button("등급 분류 시작"):
        st.query_params["page"] = "upload"
        st.rerun()


# 업로드 및 메타데이터 입력 페이지
elif page == "upload":
    st.title("비디오 정보 입력")
    st.write("비디오 등급 분류에 필요한 정보를 입력해주세요.")

    # 필수 입력
    category = st.selectbox("구분 *", ["선택하세요", "영화", "비디오물", "광고물", "기타"])
    title = st.text_input("제목 *")
    genre = st.selectbox("장르 *", ["선택하세요", "범죄", "액션", "드라마", "코미디", "공포", "로맨스", "SF", "판타지", "기타"])
    synopsis = st.text_input("시놉시스 *")
    applicant = st.text_input("신청사 *")
    representative = st.text_input("대표 *")
    director = st.text_input("감독 *")
    director_nationality = st.selectbox("감독 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    lead_actor = st.text_input("주연 배우 *")
    lead_actor_nationality = st.selectbox("주연 배우 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    video_language = st.selectbox("영상 언어 *", ["선택하세요", "ko", "en", "ja", "cn", "es", "fr", "it"])
    # 옵션 입력
    start_time = st.text_input("분석 시작 시간 (HH:MM:SS, 선택사항)", value="")
    duration = st.text_input("분석 지속 시간 (HH:MM:SS, 선택사항)", value="")
    # 파일 업로드
    uploaded_file = st.file_uploader("비디오 업로드 *", type=["mp4", "mov", "avi"], help="MP4, MOV 또는 AVI 형식, 최대 3GB")

    if uploaded_file is not None:
        st.session_state["uploaded_file"] = uploaded_file
        st.write("파일 업로드 완료!")

    if st.button("등급 분류 요청"):
        if not all([genre, category, applicant, director_nationality, title, lead_actor_nationality, representative, video_language, director, lead_actor, uploaded_file]):
            st.error("모든 필수 항목을 입력해주세요.")
        else:
            # 📌 start_time과 duration이 빈 문자열("")이면 None으로 변환
            start_time = start_time if start_time.strip() else None
            duration = duration if duration.strip() else None

            # 입력 데이터 저장
            st.session_state["input_data"] = {
                "구분": category,
                "장르" : genre,
                "제목": title,
                "시놉시스" : synopsis,
                "신청사": applicant,
                "감독": director,
                "감독 국적": director_nationality,
                "주연 배우": lead_actor,
                "주연 배우 국적": lead_actor_nationality,
                "대표": representative,
                "영상 언어": video_language[:2],
                "업로드 파일": uploaded_file.name if uploaded_file else None,
                "분석 시작 시간": start_time,
                "분석 지속 시간": duration
            }
            # 🔹 등급 분석 실행
            process_video_classification()

elif page == "result":
    
    # 🔹 아이콘 경로 설정 (업로드된 파일이 저장된 경로)
    icon_dir = "C:/Users/chloeseo/ms_project/영등위png/내용정보"

    icon_map = {
        "주제": os.path.join(icon_dir, "주제.png"),
        "선정성": os.path.join(icon_dir, "선정성.png"),
        "폭력성": os.path.join(icon_dir, "폭력성.png"),
        "공포": os.path.join(icon_dir, "공포.png"),
        "대사": os.path.join(icon_dir, "대사.png"),
        "약물": os.path.join(icon_dir, "약물.png"),
        "모방위험": os.path.join(icon_dir, "모방위험.png")
    }

    # 🔹 등급별 색상 매핑
    rating_color_map = {
        "전체관람가": "green",
        "12세이상관람가": "yellow",
        "15세이상관람가": "orange",
        "청소년관람불가": "red",
        "제한상영가": "gray"
    }

    st.title("비디오 등급 분류 결과")

    # 분석 결과 가져오기
    analysis_results = st.session_state.get("analysis_results", {})

    if not analysis_results:
        st.error("🚨 분석 결과가 없습니다. 먼저 비디오 등급 분류를 수행해주세요.")
        st.stop()

    # 🔹 분석 결과를 표로 정리
    result_data = {
        "구분": analysis_results.get("구분", "데이터 없음"),
        "접수일자": analysis_results.get("접수일자", "데이터 없음"), 
        "한글제명/원재명": analysis_results.get("한글제명/원재명", "데이터 없음"),
        "신청사": analysis_results.get("신청사", "데이터 없음"),
        "대표": analysis_results.get("대표", "데이터 없음"),
        "등급분류일자": analysis_results.get("등급분류일자", "데이터 없음"),
        "관람등급": analysis_results.get("관람등급", "데이터 없음"),
        "감독": analysis_results.get("감독", "데이터 없음"),
        "감독 국적": analysis_results.get("감독 국적", "데이터 없음"),
        "주연 배우": analysis_results.get("주연 배우", "데이터 없음"),
        "주연 배우 국적": analysis_results.get("주연 배우 국적", "데이터 없음"),
        # "서술적 내용기술": analysis_results.get("서술적 내용기술", "데이터 없음")
    }

    st.write("### 🎬 비디오 등급 분류 정보")

    # 관람등급 가져오기
    rating = result_data["관람등급"]
    rating_color = rating_color_map.get(rating, "black")  # 기본값: 검정색

    # 관람등급 출력 (HTML 스타일 적용)
    st.markdown(
        f"<p style='color:{rating_color}; font-weight:bold; font-size:24px;'>{rating}</p>",
        unsafe_allow_html=True
    )

    st.table(result_data)


    # # 나머지 정보 테이블로 출력
    # st.table({k: v for k, v in result_data.items() if k != "관람등급"})  

    # # 🔥 관람등급만 빨간색 굵은 글씨로 출력
    # st.markdown(f"**관람등급:** <span style='color:red; font-weight:bold;'>{result_data['관람등급']}</span>", unsafe_allow_html=True)
    # st.table(result_data)
    

    ### 내용정보 
    # # 🔹 등급 기준별 결과 출력
    # st.write("### 📊 내용정보")
    # rating_data = [
    #     {"항목": key, "등급": value} for key, value in analysis_results.get("내용정보", {}).items()
    # ]
    # st.table(rating_data)

    st.write("### 📊 내용정보")

    # 🔹 모든 기준별 등급을 표로 표시 (내용정보)
    content_info = analysis_results.get("내용정보", {})

    if content_info:
        content_info_list = [{"항목": key, "등급": value} for key, value in content_info.items()]
        st.table(content_info_list)  # ✅ Streamlit의 기본 table 기능 활용

    # 🔹 내용정보 top3 가져오기
    content_info_top = analysis_results.get("내용정보 탑3", {})

    if content_info_top:
        # 🔹 등급별 점수화 (높은 등급일수록 높은 값)
        rating_score = {"전체관람가": 0, "12세이상관람가": 1, "15세이상관람가": 2, "청소년관람불가": 3, "제한상영가": 4}
        
        # 🔹 데이터 변환 (높은 등급순 정렬)
        sorted_content = sorted(content_info_top.items(), key=lambda x: rating_score[x[1]], reverse=True)

        # 🔹 상위 3개 항목 선택
        top_3 = sorted_content[:3]

        # 🔹 상위 3개 항목 강조 (PNG 아이콘 표시)
        st.write("### 📌 내용정보 표시항목 (Top 3)")
        col1, col2, col3 = st.columns(3)

        for idx, (category, rating) in enumerate(top_3):
            with [col1, col2, col3][idx]:
                icon_path = icon_map.get(category)
                if icon_path and os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    st.image(image, caption=f"{category}: {rating}", use_container_width=True) # 이렇게하면 st 특성상 너비 자동으로 맞춰져서 너무 커짐..                
                else:
                    st.markdown(f"**{category}**: <span style='color:{rating_color_map[rating]}; font-weight:bold;'>{rating}</span>", unsafe_allow_html=True)


    # 🔹 분석 사유 출력
    st.write("### 📝 서술적 내용기술")
    reason_text = analysis_results.get("서술적 내용기술", "데이터 없음")

    if reason_text and reason_text != "데이터 없음":
        # 줄바꿈 적용하여 출력
        formatted_text = reason_text.replace("\n", "<br>")  
        st.markdown(f"<p style='font-size:18px; line-height:1.6;'>{formatted_text}</p>", unsafe_allow_html=True)
    else:
        st.write("데이터 없음")

    
    # 🔹 메인 페이지로 돌아가는 버튼
    if st.button("🔄 시작 화면으로 돌아가기"):
        st.query_params["page"] = ""
        st.rerun()
