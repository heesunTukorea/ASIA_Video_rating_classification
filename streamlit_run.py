import streamlit as st
import base64
from PIL import Image
from classification_runner_def import total_classification_run
import os
import datetime
import time
import matplotlib.pyplot as plt
import sys
import io

# 페이지 설정 추가
st.set_page_config(page_title="영상물 등급 분류 시스템", page_icon="🎬", layout="wide")
# st.set_page_config(page_title="영상물 등급 분류 시스템", page_icon="🎬", layout="centered")

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
                "대표" : input_data["대표"]
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
# if "analysis_done" not in st.session_state:  # ✅ 분석 완료 상태 초기화
#     st.session_state["analysis_done"] = False  
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
    st.markdown("<p class='centered'>비디오 콘텐츠에 적절한 등급을 지정하는 시스템입니다.<br>공정하고 신뢰할 수 있는 등급 분류를 경험해보세요.<br>아래 버튼을 클릭하여 시작하세요.</p>", unsafe_allow_html=True)

    # 버튼 중앙 정렬
    if st.button("등급 분류 시작"):
        st.query_params["page"] = "upload"
        st.rerun()

    # 프로젝트 소개 페이지로 이동
    if st.button("프로젝트 소개"):
        st.query_params["page"] = "project"
        st.rerun()


# 프로젝트 소개 페이지
elif page == "project":
    st.title("GRAB")
    with st.expander("🔍 프로젝트 개요 보기"):
        st.write("AI를 활용하여 영상물의 등급을 잡아라!")
        st.write("영상물의 내용을 분석하여 적절한 등급을 판정하는 시스템입니다.")

    # 상위 메뉴 선택
    main_menu = st.selectbox("📌 GRAB 정보", ["페이지 정보", "팀원 소개", "기타"])

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
        st.image(image, use_container_width=True)  # 이미지를 전체 너비로 맞추기

    elif main_menu == "기타":
        st.header("📌 기타 정보")
        # 깔끔한 'GitHub 보러가기' 버튼 추가
        st.markdown(
            '📎[GitHub 보러가기](https://github.com/heesunTukorea/ASIA_Video_rating_classification.git)',
            unsafe_allow_html=True
        )
        st.write("데이터 출처 등 기타 정보")

    # 메인 화면으로 이동
    if st.button("Main"):
        st.query_params["page"] = ""
        st.rerun()


# 업로드 및 메타데이터 입력 페이지
elif page == "upload":
    st.title("비디오 정보 입력")
    st.write("비디오 등급 분류에 필요한 정보를 입력해주세요.")

    # 필수 입력
    category = st.selectbox("구분 *", ["선택하세요", "영화", "비디오물", "광고물", "기타"])
    title = st.text_input("제목 *")
    # genre = st.selectbox("장르 *", ["선택하세요", "범죄", "액션", "드라마", "코미디", "공포", "로맨스", "SF", "판타지", "기타"])
    genre = st.multiselect("장르 *", ["범죄", "액션", "드라마", "코미디", "스릴러", "로맨스", "SF", "느와르", "판타지", "기타"])
    synopsis = st.text_input("소개 *")
    applicant = st.text_input("신청사 *")
    representative = st.text_input("대표 *")
    director = st.text_input("감독 *")
    director_nationality = st.selectbox("감독 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    lead_actor = st.text_input("주연 배우 *")
    lead_actor_nationality = st.selectbox("주연 배우 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    video_language = st.selectbox("영상 언어 *", ["선택하세요", "ko", "en", "ja", "cn", "es", "fr", "it"])
    '''
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
'''
    # 옵션 입력
    start_time = st.text_input("분석 시작 시간 (HH:MM:SS, 선택사항)", value="")
    duration = st.text_input("분석 지속 시간 (HH:MM:SS, 선택사항)", value="")
    # 파일 업로드
    uploaded_file = st.file_uploader("비디오 업로드 *", type=["mp4", "mov", "avi"], help="MP4, MOV 또는 AVI 형식, 최대 5GB")

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
                "소개" : synopsis,
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

    # ✅ 등급 분석이 완료되었을 때만 버튼 표시
    if st.session_state["analysis_done"]:
        st.write("등급 분류가 완료되었습니다! 아래 버튼을 눌러 결과 페이지로 이동하세요.")
        if st.button("📊 결과 페이지로 이동"):
            st.query_params["page"] = "result"
            st.rerun()

elif page == "result":

    # 🔹 등급별 색상 매핑
    rating_color_map = {
        "전체관람가": "green",
        "12세이상관람가": "yellow",
        "15세이상관람가": "orange",
        "청소년관람불가": "red",
        "제한상영가": "gray"
    }

    # 🔹 연령 등급별 색상 및 아이콘 매핑
    rating_assets = {
        "전체관람가": {"color": "green", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/ALL.png"},
        "12세이상관람가": {"color": "yellow", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/12.png"},
        "15세이상관람가": {"color": "orange", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/15.png"},
        "청소년관람불가": {"color": "red", "icon": "C:/Users/chloeseo/ms_project/ASIA_Video_rating_classification/st_img/영등위png/연령등급/18.png"},
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

    st.title("비디오 등급 분류 결과")

    # 분석 결과 가져오기
    analysis_results = st.session_state.get("analysis_results", {})

    if not analysis_results:
        st.error("🚨 분석 결과가 없습니다. 먼저 비디오 등급 분류를 수행해주세요.")
        st.stop()

    # 🔹 연령 등급 출력 (아이콘 + 텍스트)
    rating = analysis_results.get("관람등급", "데이터 없음")
    rating_info = rating_assets.get(rating, {"color": "black", "icon": None})  # 기본값 설정

    col1, col2 = st.columns([1, 12])  # wide
    # col1, col2 = st.columns([1, 4])  # centered
    with col1:
        if rating_info["icon"]:
            st.image(rating_info["icon"], width=120)  # 아이콘 크기 조절

    with col2:
        st.markdown(
            f"<p style='color:{rating_info['color']}; font-weight:bold; font-size:35px; line-height:120px;'>{rating}</p>",
            unsafe_allow_html=True
        )
    
    st.write('')
    ### 내용정보 
    # 표
    st.write("### 📊 내용정보")

    # 🔹 모든 기준별 등급을 표로 표시 (내용정보)
    content_info = analysis_results.get("내용정보", {})

    if content_info:
        content_info_list = [{"항목": key, "등급": value} for key, value in content_info.items()]
        st.table(content_info_list)  # ✅ Streamlit의 기본 table 기능 활용

    # ## 그래프
    # st.write("### 📊 내용정보")
    # # 🔹 등급별 점수 매핑 (그래프 표현을 위해 숫자로 변환)
    # rating_score = {"전체관람가": 0, "12세이상관람가": 1, "15세이상관람가": 2, "청소년관람불가": 3, "제한상영가": 4}
    # rating_labels = list(rating_score.keys())  # Y축 라벨 (등급)
    # rating_positions = list(rating_score.values())  # Y축 위치 (0,1,2,3,4)

    # # 🔹 모든 기준별 등급을 그래프로 표시 (내용정보)
    # content_info = analysis_results.get("내용정보", {})

    # if content_info:
    #     categories = list(content_info.keys())  # X축 (각 기준)
    #     ratings = [rating_score[value] for value in content_info.values()]  # 등급을 숫자로 변환

    #     # 🔹 전체관람가(0)도 최소 높이를 가지도록 조정
    #     ratings_adjusted = [v if v > 0 else 0.5 for v in ratings]  # 전체관람가도 보이게 최소 0.5 설정

    #     # 그래프 크기 설정
    #     fig, ax = plt.subplots(figsize=(10, 5))

    #     # 가로 막대 그래프 생성 (X축이 기준, Y축이 등급)
    #     ax.bar(categories, ratings_adjusted, color='skyblue')

    #     # Y축 (등급) 라벨을 '전체관람가' ~ '제한상영가'로 변경
    #     ax.set_yticks(rating_positions)
    #     ax.set_yticklabels(rating_labels, fontsize=12)

    #     # X축 (기준) 라벨 회전
    #     ax.set_xticklabels(categories, rotation=30, ha='right', fontsize=12)

    #     # 제목 및 라벨 설정
    #     ax.set_xlabel("", fontsize=14, fontweight='bold')
    #     ax.set_ylabel("", fontsize=14, fontweight='bold')
    #     ax.set_title("", fontsize=16, fontweight='bold')

    #     # 값 표시 (막대 위에 해당 등급 라벨 표시)
    #     for i, v in enumerate(ratings):
    #         ax.text(i, ratings_adjusted[i] + 0.1, rating_labels[v], ha='center', fontsize=10, color='black', fontweight='bold')

    #     # 스트림릿에서 그래프 출력
    #     st.pyplot(fig)

    st.write('')
    ### 내용정보 top3
    # 🔹 내용정보 top3 가져오기
    content_info_top = analysis_results.get("내용정보 탑3", {})

    if content_info_top:
        # 🔹 등급별 점수화 (높은 등급일수록 높은 값)
        rating_score = {"전체관람가": 0, "12세이상관람가": 1, "15세이상관람가": 2, "청소년관람불가": 3, "제한상영가": 4}
        
        # 🔹 데이터 변환 (높은 등급순 정렬)
        sorted_content = sorted(content_info_top.items(), key=lambda x: rating_score[x[1]], reverse=True)

        # 🔹 상위 3개 항목 선택
        top_3 = sorted_content[:3]

        # # 🔹 상위 3개 항목 강조 (PNG 아이콘 표시)
        st.write("### 📌 내용정보 표시항목 (Top3)")
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, col16, col17 = st.columns(17) # wide
        # col1, col2, col3, col4, col5, col6, col7 = st.columns(7) # centered

        for idx, (category, rating) in enumerate(top_3):
            with [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, col16, col17][idx]: # wide
            # with [col1, col2, col3, col4, col5, col6, col7][idx]: # centered
                icon_path = icon_map.get(category)
                if icon_path and os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    # st.image(image, caption=f"{category}: {rating}", width=95)            
                    st.image(image, width=110)   
                else:
                    st.markdown(f"**{category}**: <span style='color:{rating_color_map[rating]}; font-weight:bold;'>{rating}</span>", unsafe_allow_html=True)
    
    st.write('')
    # # 🔹 분석 사유 출력
    st.write("### 📝 서술적 내용기술")
    
    # ## 기본 출력
    # reason_text = analysis_results.get("서술적 내용기술", "데이터 없음")

    # if reason_text and reason_text != "데이터 없음":
    #     # 줄바꿈 적용하여 출력
    #     formatted_text = reason_text.replace("\n", "<br>")  
    #     st.markdown(f"<p style='font-size:18px; line-height:1.6;'>{formatted_text}</p>", unsafe_allow_html=True)
    # else:
    #     st.write("데이터 없음")

    ## st.write_stream 사용 - 한줄씩
    reason_text = analysis_results.get("서술적 내용기술", "데이터 없음")

    if reason_text and reason_text != "데이터 없음":
        def stream_text():
            # 텍스트를 줄바꿈을 기준으로 나눠서 리스트에 저장
            lines = reason_text.split("\n")
            
            for line in lines:
                st.text(line)  # 각 줄을 따로 출력
                time.sleep(0.5)  # 각 줄 사이에 약간의 딜레이 추가

        stream_text()  # 스트리밍 함수 호출
    else:
        st.warning("데이터 없음")

    # ## st.write_stream 사용 - 한글자씩
    # reason_text = analysis_results.get("서술적 내용기술", "데이터 없음")

    # if reason_text and reason_text != "데이터 없음":
    #     def stream_text():
    #         # 텍스트를 줄바꿈을 기준으로 나누어서 리스트에 저장
    #         lines = reason_text.split("\n")
            
    #         for line in lines:
    #             # 한 줄씩 타이핑 효과 적용
    #             for char in line:
    #                 yield char  # 한 글자씩 스트리밍
    #                 time.sleep(0.03)  # 타이핑 효과를 위해 딜레이 추가
    #             yield "\n"  # 줄바꿈을 명확히 처리
    #             time.sleep(0.1)  # 각 줄 사이에 약간의 딜레이 추가

    #     # generator 객체를 st.write_stream에 넘겨줘야 함
    #     st.write_stream(stream_text())  # generator를 전달하여 스트리밍
    # else:
    #     st.warning("데이터 없음")

    st.write('')
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
        # "서술적 내용기술": analysis_results.get("서술적 내용기술", "데이터 없음")
    }
    st.expander("📜 분석 결과 요약", expanded=False).table(result_data)

    st.write('')
    # 🔹 메인 페이지로 돌아가는 버튼
    if st.button("🔄 시작 화면으로 돌아가기"):
        st.query_params["page"] = ""
        st.rerun()
