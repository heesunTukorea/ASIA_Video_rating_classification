import streamlit as st
import base64
from PIL import Image

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

# 페이지 상태 관리 및 세션 상태 초기화
page = st.query_params.get("page", "")
if "input_data" not in st.session_state:
    st.session_state["input_data"] = {}
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = {}

# 메인 페이지
if page == "":
    st.title("비디오 등급 분류 시스템")
    try:
        image = Image.open("your_image.png")  # 실제 이미지 파일 경로로 변경
        st.image(image, use_column_width=True)
    except FileNotFoundError:
        st.write(" ")
    st.write("비디오 콘텐츠에 적절한 등급을 지정하는 시스템입니다. 아래 버튼을 클릭하여 시작하세요.")

    if st.button("등급 분류 시작"):
        st.query_params["page"] = "upload"

# 업로드 및 메타데이터 입력 페이지
elif page == "upload":
    st.title("비디오 정보 입력")
    st.write("비디오 등급 분류에 필요한 정보를 입력해주세요.")

    category = st.selectbox("구분 *", ["선택하세요", "영화", "드라마", "애니메이션", "기타"])
    title = st.text_input("제목 *")
    applicant = st.text_input("신청사 *")
    representative = st.text_input("대표 *")
    director = st.text_input("감독 *")
    director_nationality = st.selectbox("감독 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    lead_actor = st.text_input("주연 배우 *")
    lead_actor_nationality = st.selectbox("주연 배우 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    video_language = st.selectbox("영상 언어 *", ["선택하세요", "한국어", "영어", "일본어", "중국어", "기타"])
    uploaded_file = st.file_uploader("비디오 업로드 *", type=["mp4", "mov", "avi"], help="MP4, MOV 또는 AVI 형식, 최대 2GB")

    if uploaded_file is not None:
        st.write("파일 업로드 완료!")

    if st.button("등급 분류 요청"):
        if not all([category, applicant, director_nationality, title, lead_actor_nationality, representative, video_language, director, lead_actor, uploaded_file]):
            st.error("모든 필수 항목을 입력해주세요.")
        else:
            # 입력 데이터 저장
            st.session_state["input_data"] = {
                "구분": category,
                "제목": title,
                "신청사": applicant,
                "감독": director,
                "감독 국적": director_nationality,
                "주연 배우": lead_actor,
                "주연 배우 국적": lead_actor_nationality,
                "대표": representative,
                "영상 언어": video_language,
                "업로드 파일": uploaded_file.name if uploaded_file else None
            }
            # 분석 결과 생성 (임시, 실제 분석 로직으로 대체해야 함)
            st.session_state["analysis_results"] = {
                "구분": st.session_state["input_data"]["구분"],
                "한글제명/원재명": st.session_state["input_data"]["제목"],
                "신청사": st.session_state["input_data"]["신청사"],
                "등급분류일자": "2024-02-21",
                "관람등급": "12세이상관람가",
                "등급분류번호/유해확인번호": "2024-VK00960",
                "상영시간(분)": "6분",
                "감독": st.session_state["input_data"]["감독"],
                "감독국적": st.session_state["input_data"]["감독 국적"],
                "주연": st.session_state["input_data"]["주연 배우"],
                "주연국적": st.session_state["input_data"]["주연 배우 국적"],
                "계약연도": "2024",
                "정당한권리자": st.session_state["input_data"]["신청사"],
                "제작년도": "2024-02-01",
                "내용정보": {
                    "주제": "12세이상관람가",
                    "폭력성": "12세이상관람가",
                    "선정성": "12세이상관람가",
                    "공포": "12세이상관람가",
                    "약물": "12세이상관람가",
                    "모방위험": "12세이상관람가",
                    "대사": "12세이상관람가",
                },
                "서술적 내용기술": f"<{st.session_state['input_data']['제목']}>에 대한 분석 결과입니다.",
            }
            st.write("등급 분류 요청이 제출되었습니다!")
            st.query_params["page"] = "result"

# 결과 페이지
elif page == "result":
    st.title("비디오 등급 분류 결과")

    analysis_results = st.session_state["analysis_results"]

    # 아이콘 base64 인코딩
    rating_criteria_icons_base64 = {}
    for criteria in ["주제", "폭력성", "선정성", "공포", "약물", "모방위험", "대사"]:
        icon_path = f"C:/Users/chloeseo/Downloads/{criteria}.png" # 아이콘 파일명 수정 필요
        rating_criteria_icons_base64[criteria] = image_to_base64(icon_path)

    st.write("""
    <style>
    .container {
        display: flex;
        flex-direction: column;
        width: 80%;
        margin: 20px auto; /* 가운데 정렬 */
        border: 1px solid #ccc; /* 테두리 추가 */
        padding: 20px; /* 내부 여백 추가 */
    }
    .factors {
        display: flex;
        align-items: center; /* 세로 가운데 정렬 */
        margin-bottom: 20px;
    }
    .factors-label {
        font-weight: bold;
        margin-right: 10px;
    }
    .factor-bar {
        width: 30px;
        margin: 0 5px;
        background-color: lightgray;
        position: relative;
        border-radius: 3px;
    }
    .factor-level {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        border-radius: 3px;
    }
    .rating {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .rating-label {
        font-size: 2em;
        font-weight: bold;
        margin-right: 20px;
        color: #d9534f; /* 등급 색상 (예시) */
    }
    .criteria {
        display: flex;
        flex-wrap: wrap; /* 내용이 넘칠 경우 줄바꿈 */
        gap: 20px;
    }
    .criteria-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .criteria-icon {
        width: 40px;
        height: 40px;
        margin-bottom: 5px;
    }
    .notes {
        margin-top: 20px;
        border-top: 1px solid #ccc;
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.write('<div class="container">', unsafe_allow_html=True)

    # Content Rating Factors
    st.write('<div class="factors">', unsafe_allow_html=True)
    st.write('<div class="factors-label">Content Rating Factors</div>', unsafe_allow_html=True)
    for criteria, value in analysis_results["내용정보"].items():
        level = {"없음": 0, "낮음": 25, "보통": 50, "높음": 75, "심각": 100}.get(value, 0)
        color = {"없음": "lightgray", "낮음": "#5cb85c", "보통": "#f0ad4e", "높음": "#d9534f", "심각": "#d9534f"}.get(value)
        st.write(f'<div class="factor-bar" style="height: 100px;"><div class="factor-level" style="height: {level}px; background-color: {color};"></div></div>', unsafe_allow_html=True)
    st.write('</div>', unsafe_allow_html=True)

    # Final Viewing Rating
    st.write('<div class="rating">', unsafe_allow_html=True)
    st.write(f'<div class="rating-label">15</div>', unsafe_allow_html=True) # 임시 등급
    st.write('</div>', unsafe_allow_html=True)

    # Content Rating Criteria
    st.write('<div class="criteria">', unsafe_allow_html=True)
    for criteria, base64_icon in rating_criteria_icons_base64.items():
        if base64_icon:
            st.write(f"""
            <div class="criteria-item">
                <img class="criteria-icon" src="{base64_icon}" alt="{criteria} 아이콘">
                <div>{criteria}</div>
            </div>
            """, unsafe_allow_html=True)
    st.write('</div>', unsafe_allow_html=True)

    # Descriptive Content Notes
    st.write('<div class="notes">', unsafe_allow_html=True)
    st.write("Descriptive Content Notes")
    st.write(analysis_results["서술적 내용기술"])
    st.write('</div>', unsafe_allow_html=True)
    st.write('</div>', unsafe_allow_html=True) # container 닫기


    if st.button("시작 화면으로 돌아가기"):
        st.query_params["page"] = ""

# 페이지가 없을 경우
else:
    st.write("잘못된 접근입니다.")
