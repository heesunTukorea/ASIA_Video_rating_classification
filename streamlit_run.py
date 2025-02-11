import streamlit as st
import base64
from PIL import Image
from classification_runner_def import total_classification_run
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
st.set_page_config(page_title="영상물 등급 분류 시스템", page_icon="🎬", layout="centered")

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
            input_data["소개"],  
            input_data["장르"],
            input_data["분석 시작 시간"],
            input_data["분석 지속 시간"],
            input_data["영상 언어"][:2]
        ]

        # 🔹 Streamlit 상태 표시 (로딩 시작)
        with st.status("🎬 등급 분석 중입니다. 잠시만 기다려 주세요.", expanded=False) as status:
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
            selected_language_name = {v: k for k, v in languages.items()}.get(input_data["영상 언어"], "데이터 없음") 

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
                "영상 언어": selected_language_name  # ✅ "ko" → "한국어" 변환
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

# 메인 페이지 - 가운데정렬
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

    try:
        image = Image.open("C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/메인이미지/메인이미지.png") 
        st.image(image, use_container_width=True)  # 이미지를 전체 너비로 맞추기
    except FileNotFoundError:
        st.write(" ")

    # 설명 텍스트 가운데 정렬
    st.markdown("<p class='centered'>비디오 콘텐츠에 적절한 등급을 분류하고 판정하는 시스템입니다.<br>공정하고 신뢰할 수 있는 등급 분류를 경험해보세요.<br>아래 버튼을 클릭하여 시작하세요.</p>", unsafe_allow_html=True)

    # 두 개의 컬럼 생성 (가운데 정렬을 고려하여 비율 조정 가능)
    col1, col2, col3, col4 = st.columns([1,1,1,1])  # 동일한 비율로 컬럼 생성

    with col2:
        if st.button("📖 프로젝트 소개"):
            st.query_params["page"] = "project"
            st.rerun()

    with col3:
        if st.button("🎬 등급 분류 시작"):
            st.query_params["page"] = "upload"
            st.rerun()


# 프로젝트 소개 페이지
elif page == "project":
    st.title("AI를 활용한 영상물 등급 판정 시스템 : GRAB")
    with st.expander("🔍 프로젝트 개요 보기"):
        st.write("AI를 활용하여 영상물의 등급을 잡아라!")
        st.write("영상물의 내용을 분석하여 적절한 등급을 판정하는 시스템입니다.")

    # 상위 메뉴 선택
    main_menu = st.selectbox("💿 GRAB 정보", ["페이지 정보", "팀원 소개", "기타"])

    if main_menu == "페이지 정보":
        # 하위 메뉴 (가로 정렬) --> 이거 아니다..
        sub_menu = st.radio(
            "🔍 세부 정보", 
            ["1", "2", "3", "4"], 
            horizontal=True
        )

        # 선택한 하위 메뉴에 따라 다른 내용 출력
        if sub_menu == "1":
            st.header("📌 AI 활용 영상물 등급 판정")
            st.write("어쩌구저쩌구")
        elif sub_menu == "2":
            st.header("📌 2")
            st.write("어쩌구저쩌구")
        elif sub_menu == "3":
            st.header("📌 3")
            st.write("어쩌구저쩌구")
        elif sub_menu == "4":
            st.header("🤖 4")
            st.write("어쩌구저쩌구")

    elif main_menu == "팀원 소개":
        st.header("👨‍💻 팀원 소개")
        image = Image.open("C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/팀원소개.png")
        st.image(image, use_container_width=True)  # centered

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


### 업로드 및 메타데이터 입력 페이지
## 한줄 입력
# elif page == "upload":
    
#     st.title("비디오 정보 입력")
#     st.write("비디오 등급 분류에 필요한 정보를 입력해주세요.")

#     languages = {
#     "한국어": "ko",
#     "영어": "en",
#     "일본어": "ja",
#     "중국어": "zh",
#     "스페인어": "es",
#     "프랑스어": "fr",
#     "독일어": "de",
#     "이탈리아어": "it",
#     "힌디어": "hi",
#     "아랍어": "ar",
#     "포르투갈어": "pt",
#     "러시아어": "ru"
#     }

#     # 필수 입력
#     category = st.selectbox("구분 *", ["선택하세요", "영화", "비디오물", "광고물", "기타"])
#     title = st.text_input("제목 *")
#     # genre = st.selectbox("장르 *", ["선택하세요", "범죄", "액션", "드라마", "코미디", "공포", "로맨스", "SF", "판타지", "기타"])
#     genre = st.multiselect("장르 *", ["범죄", "액션", "드라마", "코미디", "스릴러", "로맨스/멜로", "SF", "느와르", "판타지", "기타"])
#     synopsis = st.text_input("소개 *")
#     applicant = st.text_input("신청사 *")
#     representative = st.text_input("대표 *")
#     director = st.text_input("감독 *")
#     director_nationality = st.selectbox("감독 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
#     lead_actor = st.text_input("주연 배우 *")
#     lead_actor_nationality = st.selectbox("주연 배우 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
#     # video_language = st.selectbox("영상 언어 *", ["선택하세요", "ko", "en", "ja", "cn", "es", "fr", "it"])
#     video_language = st.selectbox("영상 언어 *", ["선택하세요"] + list(languages.keys()))

#     # 옵션 입력
#     start_time = st.text_input("분석 시작 시간 (HH:MM:SS, 선택사항)", value="")
#     duration = st.text_input("분석 지속 시간 (HH:MM:SS, 선택사항)", value="")
#     # 파일 업로드
#     uploaded_file = st.file_uploader("비디오 업로드 *", type=["mp4", "mov", "avi"], help="MP4, MOV 또는 AVI 형식, 최대 5GB")

#     if uploaded_file is not None:
#         st.session_state["uploaded_file"] = uploaded_file
#         st.write("파일 업로드 완료!")

#     if st.button("등급 분류 요청"):
#         if not all([genre, category, applicant, director_nationality, title, lead_actor_nationality, representative, video_language, director, lead_actor, uploaded_file]):
#             st.error("모든 필수 항목을 입력해주세요.")
#         else:
#             # 📌 start_time과 duration이 빈 문자열("")이면 None으로 변환
#             start_time = start_time if start_time.strip() else None
#             duration = duration if duration.strip() else None

#             # 입력 데이터 저장
#             st.session_state["input_data"] = {
#                 "구분": category,
#                 "장르" : genre,
#                 "제목": title,
#                 "소개" : synopsis,
#                 "신청사": applicant,
#                 "감독": director,
#                 "감독 국적": director_nationality,
#                 "주연 배우": lead_actor,
#                 "주연 배우 국적": lead_actor_nationality,
#                 "대표": representative,
#                 # "영상 언어": video_language[:2],
#                 "영상 언어": languages.get(video_language, None) if video_language != "선택하세요" else "데이터 없음",  # 선택한 언어의 코드 값 저장
#                 "업로드 파일": uploaded_file.name if uploaded_file else None,
#                 "분석 시작 시간": start_time,
#                 "분석 지속 시간": duration
#             }
#             # 🔹 등급 분석 실행
#             process_video_classification()

#     # ✅ 등급 분석이 완료되었을 때만 버튼 표시
#     if st.session_state["analysis_done"]:
#         st.write("등급 분류가 완료되었습니다! 아래 버튼을 눌러 결과 페이지로 이동하세요.")
#         if st.button("📊 결과 페이지로 이동"):
#             st.query_params["page"] = "result"
#             st.rerun()

## 두줄 입력 => 입력 레이아웃 두줄인 경우, 로딩 상태를 버튼 중앙정렬과 분리 ∵ 로딩 상태가 col 너비에 맞춰서 이상해짐
elif page == "upload":
    
    col_center = st.columns([2, 5, 2])  # 가운데 정렬을 위한 레이아웃 설정
    with col_center[1]:
        st.title("비디오 정보 입력")
        st.write("비디오 등급 분류에 필요한 정보를 입력해주세요.")

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
    col1, col2 = st.columns(2)
    with col1:  # ✅ 왼쪽 컬럼
        category = st.selectbox("구분 *", ["선택하세요", "영화", "비디오물", "광고물", "기타"])
        genre = st.multiselect("장르 *", ["범죄", "액션", "드라마", "코미디", "스릴러", "로맨스/멜로", "SF", "느와르", "판타지", "기타"])

    with col2:  # ✅ 오른쪽 컬럼
        title = st.text_input("제목 *")
        video_language = st.selectbox("영상 언어 *", ["선택하세요"] + list(languages.keys()))

    synopsis = st.text_input("소개 *")

    col1, col2 = st.columns(2)
    with col1:  # ✅ 왼쪽 컬럼
        applicant = st.text_input("신청사 *")
        director = st.text_input("감독 *")
        lead_actor = st.text_input("주연 배우 *")
        start_time = st.text_input("분석 시작 시간 (HH:MM:SS, 선택사항)", value="")

    with col2:  # ✅ 오른쪽 컬럼
        representative = st.text_input("대표 *")
        director_nationality = st.selectbox("감독 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
        lead_actor_nationality = st.selectbox("주연 배우 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
        duration = st.text_input("분석 지속 시간 (HH:MM:SS, 선택사항)", value="")

    # 🔹 파일 업로드 (중앙 정렬)
    uploaded_file = st.file_uploader("비디오 업로드 *", type=["mp4", "mov", "avi"], help="MP4, MOV 또는 AVI 형식, 최대 5GB")

    col_center = st.columns([1, 0.8, 1])
    with col_center[1]:
        if uploaded_file is not None:
            st.session_state["uploaded_file"] = uploaded_file
            st.write("✅ 파일 업로드 완료!")

    st.write('')
    # 🔹 버튼 중앙 정렬
    col_center = st.columns([1, 0.7, 1])  # 가운데 정렬을 위한 레이아웃 설정
    with col_center[1]:  # ✅ 버튼만 중앙 정렬
        button_clicked = st.button("등급 분류 요청")  # 버튼 클릭 여부를 변수에 저장

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
                "분석 지속 시간": duration
            }

            # 🔹 등급 분석 실행 (✅ 버튼 중앙 정렬 영향을 받지 않음)
            process_video_classification()


    st.write('')
    # ✅ 등급 분석이 완료되었을 때만 결과 버튼 표시
    if st.session_state.get("analysis_done", False):
        # 🔹 문구는 왼쪽 정렬 (col_center 바깥에서 출력)
        col_center = st.columns([1, 10, 1])
        with col_center[1]:
            st.write("✅ 등급 분류가 완료되었습니다! 아래 버튼을 눌러 결과 페이지로 이동하세요.")
        # 🔹 버튼만 중앙 정렬
        col_center = st.columns([1, 1, 1])  # 가운데 정렬을 위한 레이아웃 설정
        with col_center[1]:
            if st.button("📊 결과 페이지로 이동"):
                st.query_params["page"] = "result"
                st.rerun()

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
            <span style='font-size: 30px; font-weight: bold;'>[{video_title}]</span>
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

    ## 그래프 - 기본
    st.write("### 📊 내용정보")
    # # 🔹 내용정보 데이터
    # # 1) content_info 불러오기
    # content_info = analysis_results.get("내용정보", {})

    # # 2) 필요한 리스트와 매핑 (등급 → 1~5)
    # all_items = ["주제", "대사", "약물", "폭력성", "공포", "선정성", "모방위험"]
    # rating_map = {
    #     "전체관람가": 1,
    #     "12세이상관람가": 2,
    #     "15세이상관람가": 3,
    #     "청소년관람불가": 4,
    #     "제한상영가": 5
    # }

    # # 3) 데이터프레임 생성
    # rows = []
    # for item in all_items:
    #     label = content_info.get(item, "전체관람가")     # 항목별 등급
    #     val   = rating_map[label]                      # 1~5
        
    #     # 🔸 여기서 rating_assets에서 color를 불러옴
    #     color = rating_assets[label]["color"]
    #     rows.append({
    #         "항목": item,
    #         "등급": label,
    #         "등급값": val,
    #         "color": color
    #     })

    # df = pd.DataFrame(rows)
    # df["start"] = 0  # 막대 시작점(0)

    # # 4) Altair 차트 설정 - 컨테이너x
    # chart = (
    #     alt.Chart(df)
    #     .mark_bar(size=20)
    #     .encode(
    #         x=alt.X("항목:N",
    #                 sort=all_items,
    #                 axis=alt.Axis(title=None, 
    #                               labelAngle=0,
    #                               labelFontSize=14,
    #                             labelColor="black",  # x축 라벨 진하게
    #                             tickColor="black",  # x축 눈금 진하게
    #                             domainColor="black",  # x축 선 진하게
    #                             domainWidth=2,  # x축 선 두께
    #                             tickWidth=2  # x축 눈금 두께
    #                 )),
    #         y=alt.Y(
    #             "start:Q",
    #             scale=alt.Scale(domain=[0,5.8], nice=False),
    #             axis=alt.Axis(
    #                 title=None,
    #                 values=[1,2,3,4,5],
    #                 labelExpr=(
    #                     "datum.value == 1 ? '전체관람가' : "
    #                     "datum.value == 2 ? '12세이상관람가' : "
    #                     "datum.value == 3 ? '15세이상관람가' : "
    #                     "datum.value == 4 ? '청소년관람불가' : "
    #                     "'제한상영가'"
    #                 ),
    #                 labelFontSize=14,
    #                 labelColor="black",  # 축 라벨 색상 (진하게)
    #                 domainColor="black",  # y축 선 진하게
    #             domainWidth=2,  # y축 선 두께
    #             tickWidth=2,  # y축 눈금 두께
    #             grid=True,  # 가로선 활성화
    #             gridColor="black",  # y축 가로선 검정색
    #             gridWidth=0.1  # y축 가로선 두께 (1~2가 적당)
    #             )
    #         ),
    #         y2="등급값:Q",   # 막대 끝점
    #         color=alt.value(None),  # 일단 Altair 기본 color는 None
    #         tooltip=["항목", "등급"]
    #     )
    #     .properties(width=600, height=300)
    # )

    # # 5) 막대에 row별 color 적용
    # bars = chart.mark_bar(size=30).encode(
    #     color=alt.Color("color:N",scale=None, legend=None)
    # )
    # # 차트 배경색
    # final_chart = bars.configure_view(
    #     fill="#EDEAE4",
    #     fillOpacity=0.5
    # )
    # st.altair_chart(final_chart, use_container_width=True)

    
    ## 그래프 - 애니메이션
    # 🔹 내용정보 데이터
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
            .mark_bar(size=35)
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

    st.write('')

    ## 최종등급 - 내용정보top3 가로배열 col1 col2
    col1, col2 = st.columns([1, 2])  # col1 (최종 등급) - col2 (내용정보 Top3)

    # ✅ **col1: 최종 등급 (아이콘만 표시)**
    with col1:
        st.write("#### 최종 등급")  # 제목
        rating = analysis_results.get("관람등급", "데이터 없음")
        rating_info = rating_assets.get(rating, {"icon": None})  # 기본값 설정

        if rating_info["icon"]:
            st.image(rating_info["icon"], width=100)  # 등급 아이콘 표시

    # ✅ **col2: 내용정보 Top3**
    with col2:
        st.write("#### 내용정보 표시항목 (Top3)")

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
            col_icon1, col_icon2, col_icon3 = st.columns(3)

            for idx, (category, rating) in enumerate(top_3):
                with [col_icon1, col_icon2, col_icon3][idx]:  # 3개의 컬럼에 배치
                    icon_path = icon_map.get(category)
                    if icon_path and os.path.exists(icon_path):
                        st.image(icon_path, width=100)  # 아이콘 크기 조절
                    else:
                        st.markdown(f"**{category}**: <span style='color:{rating_color_map[rating]}; font-weight:bold;'>{rating}</span>", unsafe_allow_html=True)

    st.write('')
    st.write('')
    # ## 🔹 분석 사유 출력
    # st.write("### 📝 서술적 내용기술")

    # ## st.write_stream 사용 - 한글자씩
    # reason_text = analysis_results.get("서술적 내용기술", "데이터 없음")
    # if reason_text and reason_text != "데이터 없음":
    #     def stream_text():
    #         lines = reason_text.split("\n")  # 줄 단위로 분리

    #         for line in lines:
    #             text_container = st.empty()  # 한 줄을 출력할 컨테이너
    #             output = ""  # 한 줄의 출력을 담을 변수
                
    #             for char in line:
    #                 output += char  # 한 글자씩 추가
    #                 text_container.text(output)  # 한 줄의 출력 업데이트
    #                 time.sleep(0.02)  # 글자마다 짧은 딜레이
                
    #             time.sleep(0.2)  # 한 줄이 완성된 후 약간의 딜레이 추가
    #             st.write("")  # 줄 바꿈 (새로운 줄 시작)

    #     stream_text()
    # else:
    #     st.warning("데이터 없음")

    st.write("### 📝 서술적 내용기술")

    reason_text = analysis_results.get("서술적 내용기술", "데이터 없음")

    if reason_text and reason_text != "데이터 없음":
        # 🔹 컨테이너 박스 스타일링 (CSS 적용)
        st.markdown(
            """
            <style>
            .description-box {
                background-color: rgba(250, 245, 245, 0.6);  /* 배경 투명도 50% */
                padding: 20px;  /* 내부 패딩 */
                border-radius: 10px;  /* 모서리 둥글게 */
                border: 1px solid #CCCCCC;  /* 테두리 */
                font-size: 16px;  /* 글자 크기 */
                color: #333333;  /* 글자 색 */
                line-height: 2.0;  /* 줄 간격 증가 */
                white-space: pre-wrap;  /* 줄 바꿈 유지 */
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
                    time.sleep(0.2)  # 한 줄이 완성된 후 약간의 딜레이 추가

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
        # "서술적 내용기술": analysis_results.get("서술적 내용기술", "데이터 없음")
    }
    st.expander("📜 분석 결과 요약", expanded=False).table(result_data)

    st.divider() ###

    # 방법1-1: selectbox 안에 모든 JSON 파일 리스트 추가 -> 선택해서 expander 안에 내용 표시
    st.write("### 📂 JSON 파일 확인")

    # 🔹 분석 결과 폴더 설정
    if "analysis_results" in st.session_state:
        analysis_results = st.session_state["analysis_results"]

        # ✅ 업로드된 파일명을 올바르게 가져오기
        uploaded_file = st.session_state.get("uploaded_file", None)  # 파일 업로드 정보 가져오기

        if uploaded_file:
            uploaded_file_name = uploaded_file.name  # 파일명 가져오기
        else:
            uploaded_file_name = "unknown"

        # 📌 classification_runner_def.py에서 설정한 경로와 동일하게 설정
        base_name = os.path.splitext(uploaded_file_name)[0]  # 파일명에서 확장자 제거
        result_folder_path = f"C:/Users/chloeseo/ms_project/test_v6/result/{base_name}"
        
        json_result_path = f"{result_folder_path}/result_json"  # 기준별 JSON 저장 경로
        rating_result_path = f"{result_folder_path}/rating_result"  # 등급분류 JSON 저장 경로

        # 🔹 JSON 파일 리스트 가져오기
        json_files_criteria = []  # 기준별 JSON 파일 리스트
        json_files_rating = []  # 등급분류 JSON 파일 리스트

        if os.path.exists(json_result_path):
            json_files_criteria.extend([os.path.join(json_result_path, f) for f in os.listdir(json_result_path) if f.endswith(".json")])
        if os.path.exists(rating_result_path):
            json_files_rating.extend([os.path.join(rating_result_path, f) for f in os.listdir(rating_result_path) if f.endswith(".json")])


        # ✅ 전체 JSON 파일 확인을 위한 Expander 추가
        with st.expander("🖱️ 클릭하여 확인하세요", expanded=False):  # 기본적으로 펼쳐진 상태
            col1, col2 = st.columns(2)  # 두 개의 컬럼으로 나누기

            # ✅ 기준별 JSON 파일 표시 (왼쪽)
            with col1:
                st.write("#### 기준별 JSON 파일 확인")
 
                if json_files_criteria:
                    # 기준별 JSON 파일명을 selectbox에 표시
                    json_file_names_criteria = [os.path.basename(f) for f in json_files_criteria]
                    selected_json_criteria = st.selectbox("📄 기준별 JSON 파일을 선택하세요.", json_file_names_criteria, key="criteria_select")

                    # 선택한 파일의 경로 찾기
                    selected_json_path_criteria = next((f for f in json_files_criteria if os.path.basename(f) == selected_json_criteria), None)

                    # 선택된 JSON 파일 내용 직접 출력
                    if selected_json_path_criteria:
                        with open(selected_json_path_criteria, "r", encoding="utf-8") as file:
                            json_content = json.load(file)

                        # JSON 내용을 직접 표시 (expander 없음)
                        st.json(json_content)
                else:
                    st.warning("📁 기준별 JSON 파일이 존재하지 않습니다.")

            # ✅ 등급분류 JSON 파일 표시 (오른쪽)
            with col2:
                st.write("#### 등급분류 JSON 파일 확인")

                if json_files_rating:
                    # 등급분류 JSON 파일명을 selectbox에 표시
                    json_file_names_rating = [os.path.basename(f) for f in json_files_rating]
                    selected_json_rating = st.selectbox("📄 등급분류 JSON 파일을 선택하세요.", json_file_names_rating, key="rating_select")

                    # 선택한 파일의 경로 찾기
                    selected_json_path_rating = next((f for f in json_files_rating if os.path.basename(f) == selected_json_rating), None)

                    # 선택된 JSON 파일 내용 직접 출력
                    if selected_json_path_rating:
                        with open(selected_json_path_rating, "r", encoding="utf-8") as file:
                            json_content = json.load(file)

                        # JSON 내용을 직접 표시 (expander 없음)
                        st.json(json_content)
                else:
                    st.warning("📁 등급분류 JSON 파일이 존재하지 않습니다.")

    st.write('')
    # 🔹 메인 페이지로 돌아가는 버튼
    # col_center = st.columns([1, 1, 1])  # 컴퓨터
    col_center = st.columns([1, 0.5, 1])  # 노트북
    with col_center[1]:
        if st.button("🏠 Home"):
            st.query_params["page"] = "" 
            st.rerun()
    st.session_state["analysis_done"] = False  # ✅ 분석 상태 초기화
