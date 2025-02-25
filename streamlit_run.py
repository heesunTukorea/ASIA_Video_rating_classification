import streamlit as st
import base64
from PIL import Image
from classification_runner_def import total_classification_run
from st_summary_def import streamlit_summary_def
import os
import datetime
import time
import matplotlib.pyplot as plt
import pandas as pd 
import json 
import sys
import io
import plotly.express as px
import altair as alt

# ✅ 페이지 설정 추가
st.set_page_config(page_title="영상물 등급 분류 시스템", page_icon="🎬", layout="wide")

# base64 인코딩 함수
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        st.write(f"파일을 찾을 수 없습니다: {image_path}")
        return None

# 🔹 Base64 변환 함수 - result 페이지 포스터 출력용
def image_to_base64(uploaded_file):
    try:
        file_bytes = uploaded_file.getvalue()  # 파일의 바이너리 데이터 가져오기 (read() 대신 getvalue())
        return base64.b64encode(file_bytes).decode("utf-8")  # Base64로 인코딩
    except Exception as e:
        st.error(f"🚨 이미지 변환 중 오류 발생: {e}")
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
        
        # video_path 세션 상태에 저장 => result 페이지에서 base_name 만들 용
        st.session_state["video_path"] = video_path  

        # 🔹 `total_classification_run()`에 전달할 입력값 구성
        video_data_lists = [
            video_path,
            input_data["제목"],
            input_data["소개"],  
            input_data["장르"],
            input_data["분석 시작 시간"],
            input_data["분석 지속 시간"],
            input_data["영상 언어"][:2]
        ]

        # 🔹 Streamlit 상태 표시 (로딩 시작)
        col1, col2, col3 = st.columns([1,6,1])
        with col2:
            with st.status("🎬 등급 분석 중입니다. 잠시만 기다려 주세요.", expanded=False) as status:
                # st.write("🔄 AI 모델이 영상을 분석하고 있습니다.")
                time.sleep(2)  

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
                
                # ✅ 기존 분석 결과 삭제 (새로운 값 저장을 위해)
                if "analysis_results" in st.session_state:
                    del st.session_state["analysis_results"]

                # 🔹 언어 코드 → 언어 이름 변환 확인
                selected_language_name = {v: k for k, v in languages.items()}.get(input_data["영상 언어"], "데이터 없음") # 위 3개 코드 한줄로

                # 🔹 분석 결과 저장
                st.session_state["analysis_results"] = {
                    "구분": input_data["구분"],
                    "한글제명/원재명": input_data["제목"],
                    "신청사": input_data["신청사"],
                    "소개": input_data["소개"],
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
                    "대표" : input_data["대표"],
                    "영상 언어": selected_language_name,  # ✅ "ko" → "한국어" 변환
                    "포스터" : input_data["포스터"]
                }
                    
            # ✅ 등급 분석이 끝났다는 상태 업데이트
            st.session_state["analysis_done"] = True  
            st.rerun()  # 다시 렌더링하여 버튼이 표시되도록 함

    # 🔹 표준 출력 원래대로 복구
    sys.stdout = sys.__stdout__

# 페이지 상태 관리 및 세션 상태 초기화
page = st.query_params.get("page", "")
if "input_data" not in st.session_state:
    st.session_state["input_data"] = {}
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = {}
if "uploaded_file" not in st.session_state:  # 오류 방지를 위해 초기화
    st.session_state["uploaded_file"] = None
if page == "upload" and "analysis_done" not in st.session_state:
    st.session_state["analysis_done"] = False
if "graph_rendered" not in st.session_state:
    st.session_state["graph_rendered"] = False
if "description_rendered" not in st.session_state:
    st.session_state["description_rendered"] = False


### 메인 페이지 ("" page)
## 가운데정렬
if page == "":
     # 🔹 메인 페이지에 들어오면 `analysis_done` 초기화
    st.session_state["analysis_done"] = False  # ✅ 분석 상태 초기화

    # 전체 중앙 정렬 스타일 적용
    st.markdown(
        """
        <style>
        .centered {
            text-align: center;
        }
        .stButton>button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 제목 가운데 정렬
    st.markdown("<h1 class='centered'>영상물 등급 분류 시스템</h1>", unsafe_allow_html=True)

    # 이미지 경로
    image_path = "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/메인이미지/메인이미지.png"
    # 빈 컬럼을 이용한 가운데 정렬
    col1, col2, col3 = st.columns([1, 2, 1])  
    with col2:  # 가운데 컬럼에 이미지 삽입
        try:
            image = Image.open(image_path)
            st.image(image, width=800)  # 원하는 크기로 설정
        except FileNotFoundError:
            st.write("이미지를 찾을 수 없습니다.")

    # 설명 텍스트 가운데 정렬
    st.markdown("<p class='centered'>비디오 콘텐츠에 적절한 등급을 지정하는 시스템입니다.<br>공정하고 신뢰할 수 있는 등급 분류를 경험해보세요.<br>아래 버튼을 클릭하여 시작하세요.</p>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns([3,2,2,2,2,3])  # 동일한 비율로 컬럼 생성

    with col3:
        if st.button("📖 프로젝트 소개"):
            st.query_params["page"] = "project"
            st.rerun()

    with col4:
        if st.button("🎬 등급 분류 시작"):
            st.query_params["page"] = "upload"
            st.rerun()


### 프로젝트 소개 페이지 (project page)
elif page == "project":
    st.title("AI를 활용한 영상물 등금 판정 시스템 : GRAB")
    with st.expander("🔍 프로젝트 개요 보기"):
        st.write("AI를 활용하여 영상물의 등급을 잡아라!")
        st.write("영상물의 내용을 분석하여 적절한 등급을 판정하는 시스템입니다.")

    # 상위 메뉴 선택
    main_menu = st.selectbox("💿 GRAB 정보", ["페이지 정보", "팀원 소개", "기타"])

    if main_menu == "페이지 정보":
        # 하위 메뉴 (가로 정렬) --> 이거 아니다..
        tab1, tab2, tab3 = st.tabs(["1.📝 영상 데이터 입력", "2.🎬 영상 등급 분류","3.📈 판별 데이터 확인"])
        with tab1:
            st.subheader("📝 영상 데이터 입력")
            
            st.markdown(f'''1️⃣ **영상 등급 분류를 위한 영상과 메타데이터 기타 신청 사항등을 입력** <br>
                        2️⃣ **영상은 현재 5GB로 제한**<br>''', unsafe_allow_html=True)
            with st.container(height=600):
                st.image('st_img/streamlit_meta.png')
        with tab2:
            st.subheader("🎬 영상 등급 분류")
            
            st.markdown(f'''1️⃣ **입력된 영상 데이터 기반으로 등급분류를 진행 후 결과 출력** <br>
                        2️⃣ **결과는 각 기준 별 모델 등급분류 결과, 시각화, 영등위 형식의 보고서 출력**<br>''', unsafe_allow_html=True)
            with st.container(height=600):
                st.image('st_img/streamlit_output.png')
        with tab3:
            st.subheader("📈 판별 데이터 확인")
            
            st.markdown(f'''1️⃣ **입력한 영상에 대한 7가지 기준의 판별 근거 데이터 제공** <br>
                        2️⃣ **기준별 판별 근거에 사용된 장면과 대사 및 총 장면에 대한 문제 장면 비율 제공**<br>''', unsafe_allow_html=True)
            with st.container(height=600):
                st.image('st_img/data_summary.png')
                
    elif main_menu == "팀원 소개":
        st.header("👨‍💻 팀원 소개")
        image = Image.open("C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/팀원소개.png")
        st.image(image, width=1500)  # wide

    elif main_menu == "기타":
        st.header("📌 기타 정보")
        # 깔끔한 'GitHub 보러가기' 버튼 추가
        st.markdown(
            '📎[GitHub 보러가기](https://github.com/heesunTukorea/ASIA_Video_rating_classification.git)',
            unsafe_allow_html=True
        )
        st.write("데이터 출처 등 기타 정보")

    # 🔹 메인 페이지로 돌아가는 버튼
    if st.button("🏠 Home"):
        st.query_params["page"] = ""
        st.rerun()


### 업로드(메타데이터 입력) 페이지 (upload page)
## 두줄 입력 => 입력 레이아웃 두줄인 경우, 로딩 상태를 버튼 중앙정렬과 분리 ∵ 로딩 상태가 col 너비에 맞춰서 이상해짐
elif page == "upload":
    
    # ✅ CSS를 사용하여 제목과 설명을 완전히 가운데 정렬
    st.markdown(
        """
        <style>
        .centered-title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
        }
        .centered-text {
            text-align: center;
            font-size: 18px;
            color: gray;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ 가운데 정렬된 제목과 설명 추가
    st.markdown("<h1 class='centered-title'>비디오 정보 입력</h1>", unsafe_allow_html=True)
    st.markdown("<p class='centered-text'>비디오 등급 분류에 필요한 정보를 입력해주세요.</p>", unsafe_allow_html=True)

    languages = {
        "한국어": "ko",
        "영어": "en",
        "일본어": "ja",
        "중국어": "zh",
        "스페인어": "es",
        "프랑스어": "fr",
        "독일어": "de",
        "이탈리아어": "it",
        "힌디어": "hi",
        "아랍어": "ar",
        "포르투갈어": "pt",
        "러시아어": "ru"
    }

    st.write('')
# 🔹 두 개의 컬럼으로 나누기
    col1, col2, col3, col4 = st.columns([1,3,3,1])
    with col2:  # ✅ 왼쪽 컬럼
        category = st.selectbox("구분 *", ["선택하세요", "영화", "비디오물", "광고물", "기타"])
        genre = st.multiselect("장르 *", ["범죄", "액션", "드라마", "코미디", "스릴러", "로맨스/멜로", "SF", "느와르", "판타지", "기타"])

    with col3:  # ✅ 오른쪽 컬럼
        title = st.text_input("제목 *")
        video_language = st.selectbox("영상 언어 *", ["선택하세요"] + list(languages.keys()))

    col1, col2, col3 = st.columns([1,6,1])
    with col2:
        synopsis = st.text_input("소개 *")

    col1, col2, col3, col4 = st.columns([1,3,3,1])
    with col2:  # ✅ 왼쪽 컬럼
        applicant = st.text_input("신청사 *")
        director = st.text_input("감독 *")
        lead_actor = st.text_input("주연 배우 *")
        start_time = st.text_input("분석 시작 시간 (HH:MM:SS, 선택사항)", value="")

    with col3:  # ✅ 오른쪽 컬럼
        representative = st.text_input("대표 *")
        director_nationality = st.selectbox("감독 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
        lead_actor_nationality = st.selectbox("주연 배우 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
        duration = st.text_input("분석 지속 시간 (HH:MM:SS, 선택사항)", value="")

    # ✅ CSS 스타일 적용
    st.markdown(
        """
        <style>
        .center-text {
            text-align: center;
            font-size: 16px;
        }

        .stButton > button {
            display: block;
            margin: auto;
            width: auto;  /* 버튼 너비 조정 */
            font-size: 16px;
            font-weight: bold;
            padding: 8px 16px;  /* 내부 여백 설정 */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 🔹 파일 업로드
    col1, col2, col3, col4 = st.columns([1,3,3,1])
    with col2:
        uploaded_img = st.file_uploader("포스터 업로드 *", type=["png", "jpg", "jpeg"])
    with col3:
        uploaded_file = st.file_uploader("비디오 업로드 *", type=["mp4", "mov", "avi"], help="MP4, MOV 또는 AVI 형식, 최대 5GB")

    if uploaded_img is not None:
    # Streamlit 세션 상태에 이미지 데이터 저장
        st.session_state["poster"] = uploaded_img

    # ✅ 파일 업로드 완료 메시지 중앙 정렬
    if uploaded_file is not None:
        st.session_state["uploaded_file"] = uploaded_file
        st.markdown('<p class="center-text">✅ 모든 파일 업로드 완료!</p>', unsafe_allow_html=True)

    st.write('')

    # ✅ 등급 분류 요청 버튼 중앙 정렬
    button_clicked = st.button("등급 분류 요청")

    # ✅ 등급 분석 실행 로직 (버튼 클릭 후 실행되도록 유지)
    if button_clicked:
        if not all([genre, category, applicant, director_nationality, title, lead_actor_nationality, representative, video_language, director, lead_actor, uploaded_file]):
            st.error("🚨 모든 필수 항목을 입력해주세요.")
        else:
            # 📌 start_time과 duration이 빈 문자열("")이면 None으로 변환
            start_time = start_time if start_time.strip() else None
            duration = duration if duration.strip() else None

            # 입력 데이터 저장
            st.session_state["input_data"] = {
                "구분": category,
                "장르": genre,
                "제목": title,
                "소개": synopsis,
                "신청사": applicant,
                "감독": director,
                "감독 국적": director_nationality,
                "주연 배우": lead_actor,
                "주연 배우 국적": lead_actor_nationality,
                "대표": representative,
                "영상 언어": languages.get(video_language, None) if video_language != "선택하세요" else "데이터 없음",
                "업로드 파일": uploaded_file.name if uploaded_file else None,
                "분석 시작 시간": start_time,
                "분석 지속 시간": duration,
                "포스터" : uploaded_img
            }

            # 🔹 등급 분석 실행 (✅ 버튼 중앙 정렬 영향을 받지 않음)
            process_video_classification()

    st.write('')
    st.write('')

    # ✅ 등급 분석이 완료되었을 때만 결과 버튼 표시
    if st.session_state.get("analysis_done", False):
        st.markdown('<p class="center-text">✅ 등급 분류가 완료되었습니다! 아래 버튼을 눌러 결과 페이지로 이동하세요.</p>', unsafe_allow_html=True)

        # ✅ 결과 페이지로 이동 버튼 중앙 정렬
        if st.button("📊 결과 페이지로 이동"):
            st.query_params["page"] = "result"
            st.rerun()

### 결과 페이지 (result page)
elif page == "result":
# 🔹 등급별 색상 매핑
    rating_color_map = {
        "전체관람가": "#2F9D27",
        "12세이상관람가": "#FFCD12",
        "15세이상관람가": "#F26F0D",
        "청소년관람불가": "#E60000",
        "제한상영가": "gray"
    }

    # 🔹 연령 등급별 색상 및 아이콘 매핑
    rating_assets = {
        "전체관람가": {"color": "#2F9D27", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/ALL.png"},
        "12세이상관람가": {"color": "#FFCD12", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/12.png"},
        "15세이상관람가": {"color": "#F26F0D", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/15.png"},
        "청소년관람불가": {"color": "#E60000", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/18.png"},
        "제한상영가": {"color": "gray", "icon": None}  # 제한상영가 이미지 없을 경우 None
    }
    # 🔹 내용정보 아이콘 매핑
    icon_dir = "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/내용정보" # 노트북
    icon_map = {
        "주제": os.path.join(icon_dir, "주제.png"),
        "선정성": os.path.join(icon_dir, "선정성.png"),
        "폭력성": os.path.join(icon_dir, "폭력성.png"),
        "공포": os.path.join(icon_dir, "공포.png"),
        "대사": os.path.join(icon_dir, "대사.png"),
        "약물": os.path.join(icon_dir, "약물.png"),
        "모방위험": os.path.join(icon_dir, "모방위험.png")
    }

    # input 받은 제목 가져오기
    analysis_results = st.session_state.get("analysis_results", {})
    video_title = analysis_results.get("한글제명/원재명", "데이터 없음")
    st.markdown(
    f"""
    <h1 style='text-align: center; font-weight: bold;'>
        비디오 등급 분류 결과<br>
        <span style='font-size: 32px; font-weight: bold;'>[{video_title}]</span>
    </h1>
    """,
    unsafe_allow_html=True
    )

    st.write('')
    # 분석 결과 가져오기
    analysis_results = st.session_state.get("analysis_results", {})

    if not analysis_results:
        st.error("🚨 분석 결과가 없습니다. 먼저 비디오 등급 분류를 수행해주세요.")
        st.stop()

    col1, col2, col3, col4, col5= st.columns([0.8,4,0.01,9,0.8])
    with col2:
        st.write("### 📊 내용정보")

    ## 왼쪽 포스터, 오른쪽 최종 등급, top3 세로로 정렬
    # 🔹 최종 등급 및 내용정보 Top3를 가로 정렬
    col1, col2, col3, col4, col5= st.columns([0.8,4,0.01,9.7,0.8])  # 왼 (포스터) - 오 (최종 등급, top3)

    # ✅ **col1
    with col2:
        # 🔹 input 받은 포스터 가져오기
        poster = analysis_results.get("포스터", None)  # ✅ "데이터 없음" 대신 None으로 설정

        if poster is not None:
            # 🔹 Base64 인코딩
            base64_image = image_to_base64(poster)

            if base64_image:
                # 🔹 CSS 적용하여 포스터 크기 조정 + 수직 중앙 정렬
                st.markdown(
                    f"""
                    <style>
                    .poster-container {{
                        display: flex;
                        justify-content: center;  /* 가로 중앙 정렬 */
                        align-items: center;  /* 세로 중앙 정렬 */
                        height: 100%;  /* 컨테이너 높이 설정 */
                        min-height: 480px; /* 최소 높이 설정 (레이아웃 유지) */
                    }}
                    </style>
                    <div class="poster-container">
                        <img src="data:image/png;base64,{base64_image}" 
                            alt="포스터 이미지"
                            style="width: 300px; height: 430px; object-fit: cover; border-radius: 10px;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("🚨 포스터 이미지 인코딩에 실패했습니다.")


    ## ✅ **col2 - 차트 아래 아이콘
    with col4:
        content_info = analysis_results.get("내용정보", {})

        # 🔹 필요한 리스트 및 매핑
        all_items = ["주제", "대사", "약물", "폭력성", "공포", "선정성", "모방위험"]
        rating_map = {
            "전체관람가": 1,
            "12세이상관람가": 2,
            "15세이상관람가": 3,
            "청소년관람불가": 4,
            "제한상영가": 5
        }
    
        # 🔹 데이터프레임 생성
        rows = []
        for item in all_items:
            label = content_info.get(item, "전체관람가")  # 기본값: 전체관람가
            val = rating_map.get(label, 1)  # 기본값 1
            color = rating_assets[label]["color"]  # 색상 가져오기

            rows.append({
                "항목": item,
                "등급": label,
                "등급값": val,
                "color": color,
                "start": 0  # 애니메이션 시작점 (0)
            })

        df = pd.DataFrame(rows)

        # 🔹 그래프 컨테이너 생성
        chart_placeholder = st.empty()

        # ✅ 1. 배경과 축이 포함된 초기 그래프 먼저 표시 (막대 없음)
        base_chart = (
            alt.Chart(df)
            .mark_bar(size=20, opacity=0)  # ✅ 초기에는 막대 안 보이게 설정
            .encode(
                x=alt.X("항목:N",
                        sort=all_items,
                        axis=alt.Axis(title=None, 
                                    labelAngle=0,
                                    labelFontSize=14,
                                    labelColor="black",
                                    tickColor="black",
                                    domainColor="black",
                                    domainWidth=2,
                                    tickWidth=2
                        )),
                y=alt.Y("등급값:Q",
                        scale=alt.Scale(domain=[0, 5.8], nice=False),
                        axis=alt.Axis(
                            title=None,
                            values=[1, 2, 3, 4, 5],
                            labelExpr=(
                                "datum.value == 1 ? '전체관람가' : "
                                "datum.value == 2 ? '12세이상관람가' : "
                                "datum.value == 3 ? '15세이상관람가' : "
                                "datum.value == 4 ? '청소년관람불가' : "
                                "'제한상영가'"
                            ),
                            labelFontSize=14,
                            labelColor="black",
                            domainColor="black",
                            domainWidth=2,
                            tickWidth=2,
                            grid=True,
                            gridColor="black",
                            gridWidth=0.1
                        )
                ),
                color=alt.Color("color:N", scale=None, legend=None),
                tooltip=["항목", "등급"]
            )
            .properties(width=600, height=300)
            .configure_view(fill="#EDEAE4", fillOpacity=0.5)  # ✅ 배경을 처음부터 적용
        )

        # ✅ 배경과 축 먼저 표시 (막대는 안 보임)
        chart_placeholder.altair_chart(base_chart, use_container_width=True)

        # 🔹 애니메이션 실행 (막대 추가)
        for step in range(1, 11):  # 10단계 애니메이션
            df["start"] = df["등급값"] * (step / 10)  # 점진적 증가

            # ✅ Altair 차트 설정 (이제 막대 보이도록 변경)
            chart = (
                alt.Chart(df)
                .mark_bar(size=40)
                .encode(
                    x=alt.X("항목:N",
                            sort=all_items,
                            axis=alt.Axis(title=None, 
                                        labelAngle=0,
                                        labelFontSize=14,
                                        labelColor="black",
                                        tickColor="black",
                                        domainColor="black",
                                        domainWidth=2,
                                        tickWidth=2
                            )),
                    y=alt.Y("start:Q",
                            scale=alt.Scale(domain=[0, 5.8], nice=False),
                            axis=alt.Axis(
                                title=None,
                                values=[1, 2, 3, 4, 5],
                                labelExpr=(
                                    "datum.value == 1 ? '전체관람가' : "
                                    "datum.value == 2 ? '12세이상관람가' : "
                                    "datum.value == 3 ? '15세이상관람가' : "
                                    "datum.value == 4 ? '청소년관람불가' : "
                                    "'제한상영가'"
                                ),
                                labelFontSize=14,
                                labelColor="black",
                                domainColor="black",
                                domainWidth=2,
                                tickWidth=2,
                                grid=True,
                                gridColor="black",
                                gridWidth=0.1
                            )
                    ),
                    color=alt.Color("color:N", scale=None, legend=None),
                    tooltip=["항목", "등급"]
                )
                .properties(width=600, height=300)
                .configure_view(fill="#EDEAE4", fillOpacity=0.5)  # ✅ 애니메이션 동안에도 배경 유지
            )

            # ✅ 그래프 업데이트 (막대가 점점 위로 차오름)
            chart_placeholder.altair_chart(chart, use_container_width=True)

            # 🔹 애니메이션 속도 조정
            time.sleep(0.1)

        # ✅ 최종 그래프 출력 (애니메이션 종료 후 추가 처리 없이 그대로 유지)
        chart_placeholder.altair_chart(chart, use_container_width=True)


    # # ✅ **최종 등급 (아이콘만 표시)**
        # ✅ **제목과 아이콘을 같은 높이에 맞추기 위한 컨테이너**
        with st.container():
            title_cols1, title_cols2, title_cols3,title_cols4 = st.columns([0.5,1,1,1])  # 최종등급 제목 + 내용정보 Top3 제목

            # ✅ **첫 번째 컬럼: 최종 등급 제목**
            with title_cols2:
                st.write("#### 최종 등급")

            # ✅ **나머지 3개 컬럼: 내용정보 Top3 제목**
            with title_cols3:
                st.write("#### 내용정보 Top3")

        # ✅ **최종등급 아이콘 + 내용정보 Top3 아이콘 가로 정렬**
        with st.container():
            cols1, cols2, cols3, cols4, cols5, cols6, cols7 = st.columns([1,1,1,1,1,1,1])  # 최종 등급(1개) + 내용정보 Top3(3개)

            # ✅ **첫 번째 컬럼: 최종 등급 아이콘**
            with cols2:
                rating = analysis_results.get("관람등급", "데이터 없음")
                rating_info = rating_assets.get(rating, {"icon": None})
                if rating_info["icon"]:
                    st.image(rating_info["icon"], width=100)

            # ✅ **나머지 3개 컬럼: 내용정보 Top3 아이콘**
            content_info_top = analysis_results.get("내용정보 탑3", {})

            if content_info_top:
                rating_score = {"전체관람가": 0, "12세이상관람가": 1, "15세이상관람가": 2, "청소년관람불가": 3, "제한상영가": 4}
                sorted_content = sorted(content_info_top.items(), key=lambda x: rating_score[x[1]], reverse=True)
                top_3 = sorted_content[:3]  # 상위 3개만 가져오기

                # ✅ **3개의 컬럼에 내용정보 아이콘 배치**
                for idx, (category, rating) in enumerate(top_3):
                    with [cols4, cols5, cols6][idx] :  # cols[1], cols[2], cols[3]에 배치
                        icon_path = icon_map.get(category)
                        if icon_path and os.path.exists(icon_path):
                            st.image(icon_path, width=100)  # 아이콘 및 텍스트 정렬
                        else:
                            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{category}</p>", unsafe_allow_html=True)


# ## ✅ **col2 - 아이콘 아래 차트
#     with col4:
#         # ✅ **제목과 아이콘을 같은 높이에 맞추기 위한 컨테이너**
#         with st.container():
#             title_cols1, title_cols2, title_cols3,title_cols4 = st.columns([0.5,1,1,1])  # 최종등급 제목 + 내용정보 Top3 제목

#             # ✅ **첫 번째 컬럼: 최종 등급 제목**
#             with title_cols2:
#                 st.write("#### 최종 등급")

#             # ✅ **나머지 3개 컬럼: 내용정보 Top3 제목**
#             with title_cols3:
#                 st.write("#### 내용정보 Top3")

#         # ✅ **최종등급 아이콘 + 내용정보 Top3 아이콘 가로 정렬**
#         with st.container():
#             cols1, cols2, cols3, cols4, cols5, cols6, cols7 = st.columns([1,1,1,1,1,1,1])  # 최종 등급(1개) + 내용정보 Top3(3개)

#             # ✅ **첫 번째 컬럼: 최종 등급 아이콘**
#             with cols2:
#                 rating = analysis_results.get("관람등급", "데이터 없음")
#                 rating_info = rating_assets.get(rating, {"icon": None})
#                 if rating_info["icon"]:
#                     st.image(rating_info["icon"], width=100)

#             # ✅ **나머지 3개 컬럼: 내용정보 Top3 아이콘**
#             content_info_top = analysis_results.get("내용정보 탑3", {})

#             if content_info_top:
#                 rating_score = {"전체관람가": 0, "12세이상관람가": 1, "15세이상관람가": 2, "청소년관람불가": 3, "제한상영가": 4}
#                 sorted_content = sorted(content_info_top.items(), key=lambda x: rating_score[x[1]], reverse=True)
#                 top_3 = sorted_content[:3]  # 상위 3개만 가져오기

#                 # ✅ **3개의 컬럼에 내용정보 아이콘 배치**
#                 for idx, (category, rating) in enumerate(top_3):
#                     with [cols4, cols5, cols6][idx] :  # cols[1], cols[2], cols[3]에 배치
#                         icon_path = icon_map.get(category)
#                         if icon_path and os.path.exists(icon_path):
#                             st.image(icon_path, width=100)  # 아이콘 및 텍스트 정렬
#                         else:
#                             st.markdown(f"<p style='text-align:center; font-weight:bold;'>{category}</p>", unsafe_allow_html=True)

#         st.write('')
#         ## 그래프 출력
#         content_info = analysis_results.get("내용정보", {})

#         # 🔹 필요한 리스트 및 매핑
#         all_items = ["주제", "대사", "약물", "폭력성", "공포", "선정성", "모방위험"]
#         rating_map = {
#             "전체관람가": 1,
#             "12세이상관람가": 2,
#             "15세이상관람가": 3,
#             "청소년관람불가": 4,
#             "제한상영가": 5
#         }
    
#         # 🔹 데이터프레임 생성
#         rows = []
#         for item in all_items:
#             label = content_info.get(item, "전체관람가")  # 기본값: 전체관람가
#             val = rating_map.get(label, 1)  # 기본값 1
#             color = rating_assets[label]["color"]  # 색상 가져오기

#             rows.append({
#                 "항목": item,
#                 "등급": label,
#                 "등급값": val,
#                 "color": color,
#                 "start": 0  # 애니메이션 시작점 (0)
#             })

#         df = pd.DataFrame(rows)
#         # 🔹 그래프 컨테이너 생성
#         chart_placeholder = st.empty()

#         # ✅ 1. 배경과 축이 포함된 초기 그래프 먼저 표시 (막대 없음)
#         base_chart = (
#             alt.Chart(df)
#             .mark_bar(size=20, opacity=0)  # ✅ 초기에는 막대 안 보이게 설정
#             .encode(
#                 x=alt.X("항목:N",
#                         sort=all_items,
#                         axis=alt.Axis(title=None, 
#                                     labelAngle=0,
#                                     labelFontSize=14,
#                                     labelColor="black",
#                                     tickColor="black",
#                                     domainColor="black",
#                                     domainWidth=2,
#                                     tickWidth=2
#                         )),
#                 y=alt.Y("등급값:Q",
#                         scale=alt.Scale(domain=[0, 5.8], nice=False),
#                         axis=alt.Axis(
#                             title=None,
#                             values=[1, 2, 3, 4, 5],
#                             labelExpr=(
#                                 "datum.value == 1 ? '전체관람가' : "
#                                 "datum.value == 2 ? '12세이상관람가' : "
#                                 "datum.value == 3 ? '15세이상관람가' : "
#                                 "datum.value == 4 ? '청소년관람불가' : "
#                                 "'제한상영가'"
#                             ),
#                             labelFontSize=14,
#                             labelColor="black",
#                             domainColor="black",
#                             domainWidth=2,
#                             tickWidth=2,
#                             grid=True,
#                             gridColor="black",
#                             gridWidth=0.1
#                         )
#                 ),
#                 color=alt.Color("color:N", scale=None, legend=None),
#                 tooltip=["항목", "등급"]
#             )
#             .properties(width=600, height=300)
#             .configure_view(fill="#EDEAE4", fillOpacity=0.5)  # ✅ 배경을 처음부터 적용
#         )

#         # ✅ 배경과 축 먼저 표시 (막대는 안 보임)
#         chart_placeholder.altair_chart(base_chart, use_container_width=True)

#         # 🔹 애니메이션 실행 (막대 추가)
#         for step in range(1, 11):  # 10단계 애니메이션
#             df["start"] = df["등급값"] * (step / 10)  # 점진적 증가

#             # ✅ Altair 차트 설정 (이제 막대 보이도록 변경)
#             chart = (
#                 alt.Chart(df)
#                 .mark_bar(size=40)
#                 .encode(
#                     x=alt.X("항목:N",
#                             sort=all_items,
#                             axis=alt.Axis(title=None, 
#                                         labelAngle=0,
#                                         labelFontSize=14,
#                                         labelColor="black",
#                                         tickColor="black",
#                                         domainColor="black",
#                                         domainWidth=2,
#                                         tickWidth=2
#                             )),
#                     y=alt.Y("start:Q",
#                             scale=alt.Scale(domain=[0, 5.8], nice=False),
#                             axis=alt.Axis(
#                                 title=None,
#                                 values=[1, 2, 3, 4, 5],
#                                 labelExpr=(
#                                     "datum.value == 1 ? '전체관람가' : "
#                                     "datum.value == 2 ? '12세이상관람가' : "
#                                     "datum.value == 3 ? '15세이상관람가' : "
#                                     "datum.value == 4 ? '청소년관람불가' : "
#                                     "'제한상영가'"
#                                 ),
#                                 labelFontSize=14,
#                                 labelColor="black",
#                                 domainColor="black",
#                                 domainWidth=2,
#                                 tickWidth=2,
#                                 grid=True,
#                                 gridColor="black",
#                                 gridWidth=0.1
#                             )
#                     ),
#                     color=alt.Color("color:N", scale=None, legend=None),
#                     tooltip=["항목", "등급"]
#                 )
#                 .properties(width=600, height=300)
#                 .configure_view(fill="#EDEAE4", fillOpacity=0.5)  # ✅ 애니메이션 동안에도 배경 유지
#             )

#             # ✅ 그래프 업데이트 (막대가 점점 위로 차오름)
#             chart_placeholder.altair_chart(chart, use_container_width=True)

#             # 🔹 애니메이션 속도 조정
#             time.sleep(0.5)

#         # # ✅ 최종 그래프 출력 (애니메이션 종료 후 추가 처리 없이 그대로 유지)
#         # chart_placeholder.altair_chart(chart, use_container_width=True)

    st.write('')
    # # # 🔹 분석 사유 출력
    # 🔹 3개의 컬럼을 생성 (비율: 0.8, 1, 0.8)
    col1, col2, col3 = st.columns([0.8, 13.01, 0.8])

    with col2:  # 중앙 정렬을 위해 col2 내부에 배치
        st.write("### 📝 서술적 내용기술")

        reason_text = analysis_results.get("서술적 내용기술", "데이터 없음")

        if reason_text and reason_text != "데이터 없음":
            # 🔹 컨테이너 박스 스타일링 (CSS 적용)
            st.markdown(
                """
                <style>
                .description-box {
                    background-color: rgba(247, 246, 244, 1);  /* 배경 투명도 */
                    padding: 20px;  /* 내부 패딩 */
                    border-radius: 10px;  /* 모서리 둥글게 */
                    border: 1px solid #CCCCCC;  /* 테두리 */
                    font-size: 16px;  /* 글자 크기 */
                    color: #333333;  /* 글자 색 */
                    line-height: 2.0;  /* 줄 간격 증가 */
                    white-space: pre-wrap;  /* 줄 바꿈 유지 */
                    text-align: left;  /* 텍스트 중앙 정렬 */
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # ✅ **하나의 컨테이너를 생성**
            text_container = st.empty()

            # 🔹 한 글자씩 출력되는 애니메이션 함수
            def stream_text():
                lines = reason_text.split("\n")  # 줄 단위로 분리
                full_text = ""  # 전체 텍스트를 담을 변수

                for i, line in enumerate(lines):
                    for char in line:
                        full_text += char  # 한 글자씩 추가
                        text_container.markdown(f'<div class="description-box">{full_text}</div>', unsafe_allow_html=True)
                        time.sleep(0.02)  # 글자마다 짧은 딜레이

                    # 🔹 마지막 줄이 아니라면 줄바꿈 추가
                    if i < len(lines) - 1:
                        full_text += "<br><br>"  # 줄 바꿈 추가
                        text_container.markdown(f'<div class="description-box">{full_text}</div>', unsafe_allow_html=True)
                        time.sleep(0.1)  # 한 줄이 완성된 후 약간의 딜레이 추가

            stream_text()

        else:
            st.warning("데이터 없음")

        st.write("")  
        st.write("")  

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
            "시놉시스" : analysis_results.get("소개", "데이터 없음"),
            "영상 언어" : analysis_results.get("영상 언어", "데이터 없음")
        }
        st.expander("📜 분석 결과 요약", expanded=False).table(result_data)

        st.divider() 

        # ✅ **JSON 파일 확인을 col2 중앙에 배치**
        st.write("### 📂 분석 결과 파일 확인")
        # 🔹 video_path 가져오기
        video_path = st.session_state.get("video_path", None)
        base_name = os.path.splitext(os.path.basename(video_path))[0] # 파일명만 추출 ex. 수리남
        streamlit_summary_def(base_name=base_name)

    st.write('')
    ### 메인 페이지로 돌아가는 버튼
    # 🔹 CSS로 버튼 중앙 정렬 & 너비 자동 조절
    st.markdown(
        """
        <style>
        .centered-button-container {
            display: flex;
            justify-content: center; /* 가로 중앙 정렬 */
            align-items: center; /* 세로 중앙 정렬 */
        }
        .stButton>button {
            font-size: 18px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 10px;
            width: auto; /* 🔹 너비 자동 조절 */
            white-space: nowrap; /* 🔹 글자 줄바꿈 방지 */
            display: flex;
            justify-content: center; /* 🔹 버튼 내부 텍스트 중앙 정렬 */
            align-items: center;
            margin: auto; /* 🔹 버튼 자체를 중앙 정렬 */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 🔹 중앙 정렬된 버튼 추가
    st.markdown('<div class="centered-button-container">', unsafe_allow_html=True)
    if st.button("🏠 Home"):
        st.query_params["page"] = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 분석 상태 초기화
    st.session_state["analysis_done"] = False

