import json
import streamlit as st
import os
from lines.lines_JSON import filter_by_category
from topic.Topic_JSON import filter_topic
#---------------------공통 함수 ----------------------------
# JSON 파일 로드 함수
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data  

# 캡션 및 true 장면 분석 함수
def classfication_tf(data):
    summary_data = data[-1]  # 마지막 요소는 summary
    true_dict = {}
    
    for img in data[:-1]:  # 마지막 summary 제외
        if img['classification'] == True:
            img_name = os.path.splitext(img['image_name'])[0]
            try:
                best_caption = img['best_caption']
                true_dict[img_name] = best_caption
            except:
                true_dict[img_name] = ''

    return true_dict, summary_data

# Streamlit UI 구성 함수
#-------------------------------공포 --------------------------------------------------------------


#호러
def display_horror_summary(file_path):
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)
    true_dict, summary_data = classfication_tf(data)

    # 이미지 선택 박스
    true_dict_keys = list(true_dict.keys())
    st.markdown("### 🕷️ **공포 장면 분석 결과**")
    select_img = st.selectbox("📌 **공포 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)
    
    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        # st.title("🕷️ 공포 장면 분석 결과")
        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_horror = summary_data['non-horror']
        horror_rate_true = summary_data['horror_rate_true']
        horror_rate_false = summary_data['horror_rate_false']
        horror_best_caption = summary_data['horror_best_caption']

        # 공포 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 공포 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **비공포 장면 수**: {non_horror} 개 (**{horror_rate_false * 100:.1f}%**)")
            st.write(f"- **공포 장면 수**: {total_scenes - non_horror} 개 (**{horror_rate_true * 100:.1f}%**)")
            
            st.markdown(f"#### **👻 공포 장면 비율**: {horror_rate_true * 100:.1f}%")
            st.progress(min(round(horror_rate_true, 2), 1.0))  # 최대 1.0 (100%)까지

        with tab2:
            st.markdown("### 📌 **공포 장면 상세 분석**")
            for caption, count in horror_best_caption.items():
                st.write(f"- **{caption}**: {count} 건")

    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
        st.markdown(f"### **🔍 장면 분류**")
        st.write(f"💬 {true_dict[select_img]}")

#---------------------------폭력------------------------------------------
#폭력
def display_violence_summary(file_path):
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)
    # true_dict, summary_data = classfication_tf(data)
    summary_data = data["summary"]  # 마지막 요소는 summary
    true_dict = {}

    for img in data['results']:  # 마지막 summary 제외
        if img['best_caption'] != '폭력적인 장면이 없습니다.':
            img_name = os.path.splitext(img['image_name'])[0]
            best_caption = img['best_caption']
            true_dict[img_name] = best_caption
    # 이미지 선택 박스
    true_dict_keys = list(true_dict.keys())
    st.markdown("### 💥 **폭력 장면 분석 결과**")
    select_img = st.selectbox("📌 **폭력성 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)

    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        
        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_violence = summary_data['non-violence']
        violence_rate_true = summary_data['violence_rate_true']
        violence_rate_false = summary_data['violence_rate_false']
        violence_best_caption = summary_data['violence_best_caption']

        # 폭력 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 폭력 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **폭력적이지 않은 장면 수**: {non_violence} 개 (**{violence_rate_false * 100:.1f}%**)")
            st.write(f"- **폭력 장면 수**: {total_scenes - non_violence} 개 (**{violence_rate_true * 100:.1f}%**)")
            
            st.markdown(f"#### **💥 폭력성 비율**: {violence_rate_true * 100:.1f}%")
            st.progress(min(round(violence_rate_true, 2), 1.0))  # 최대 1.0 (100%)까지

        with tab2:
            st.markdown("### 📌 **폭력 장면 상세 분석**")
            for caption, count in violence_best_caption.items():
                st.write(f"- **{caption}**: {count} 건")

    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
        st.markdown(f"### **🔍 장면 분류**")
        st.write(f"💬 {true_dict[select_img]}")
        
# --------------------------선정 -------------------------------------------------
def display_sexuality_summary(file_path):
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)
    true_dict, summary_data = classfication_tf(data)

    # 이미지 선택 박스
    true_dict_keys = list(true_dict.keys())
    st.markdown("### 🔞 **선정성 장면 분석 결과**")
    select_img = st.selectbox("📌 **선정성 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)

    # 📌 **요약 정보 표시**
    if select_img == 'summary':

        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_sexual = summary_data['non-sexual']
        sexual_rate_true = summary_data['sexual_rate_true']
        sexual_rate_false = summary_data['sexual_rate_false']
        sexual_best_caption = summary_data['sexual_best_caption']

        # 선정성 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 선정성 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **비선정성 장면 수**: {non_sexual} 개 (**{sexual_rate_false * 100:.1f}%**)")
            st.write(f"- **선정성 장면 수**: {total_scenes - non_sexual} 개 (**{sexual_rate_true * 100:.1f}%**)")
            
            st.markdown(f"#### **🔞 선정성 비율**: {sexual_rate_true * 100:.1f}%")
            st.progress(min(round(sexual_rate_true, 2), 1.0))  # 최대 1.0 (100%)까지

        with tab2:
            st.markdown("### 📌 **선정성 장면 상세 분석**")
            for caption, count in sexual_best_caption.items():
                st.write(f"- **{caption}**: {count} 건")

    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
        st.markdown(f"### **🔍 장면 분류**")
        st.write(f"💬 {true_dict[select_img]}")
#--------------------------- 대사 -----------------------------------------------
def display_lines_summary(file_path):
    """대사 요약 및 필터링 UI"""
    st.markdown("### 🗣️ **대사 분석 결과**")
    # st.markdown("### 🎬 **욕설 및 혐오 표현 비율별 대사 분류**")
    CATEGORY_LABELS = {
    "summary": "대사 비율 요약",
    "strong_abusive_percentage": "강한 욕설",
    "weak_abusive_percentage": "약한 욕설",
    "여성/가족_hate_percentage": "여성/가족 혐오",
    "남성_hate_percentage": "남성 혐오",
    "성소수자_hate_percentage": "성소수자 혐오",
    "인종/국적_hate_percentage": "인종/국적 혐오",
    "연령_hate_percentage": "연령 혐오",
    "지역_hate_percentage": "지역 혐오",
    "종교_hate_percentage": "종교 혐오"
    }

    # 카테고리 선택 박스
    select_cate = st.selectbox(
        "📌 **대사 분류 선택**",
        list(CATEGORY_LABELS.keys()),
        format_func=lambda x: CATEGORY_LABELS[x],  # 한글 라벨로 표시
        index=0
    )
    if select_cate =='summary':
        select_cate1 = 'strong_abusive_percentage'
    else:
        select_cate1 = select_cate
    # 선택한 카테고리 필터링
    filtered_lines, summary = filter_by_category(file_path, select_cate1)

    if select_cate == "summary":
        st.markdown("### 💬 **대사 비율 요약**")
        st.write("아래 표는 각 카테고리별 대사 비율(%)을 나타냅니다.")

        # 데이터를 표로 출력
        summary_table = {
            "카테고리": [],
            "비율 (%)": []
        }
        for key, value in summary.items():
            summary_table["카테고리"].append(CATEGORY_LABELS.get(key, key))
            summary_table["비율 (%)"].append(round(value, 3))

        st.table(summary_table)

        # **Progress Bar를 이용한 시각적 표현**
        st.markdown("### 📊 **시각적 비율 분석**")
        for key, value in summary.items():
            st.markdown(f"**{CATEGORY_LABELS.get(key, key)}**: {round(value, 2)}%")
            st.progress(min(value / 20, 1.0))  # 최대 100%를 기준으로 시각화 (10% 이상이면 풀바)
    
    else:
        # 대사 목록 UI 표시
        st.markdown(f"### 💬 **{CATEGORY_LABELS[select_cate]} 리스트**")

        if not filtered_lines:
            st.warning("❌ 해당 카테고리에 해당하는 대사가 없습니다.")
        else:
            with st.expander(f"📖 {CATEGORY_LABELS[select_cate]} 상세 보기", expanded=True):
                for idx, line in enumerate(filtered_lines):
                    st.markdown(f"**{idx + 1}.** `{line}`")


#--------------------------- 약물 ----------------------------------------
def display_drug_summary(file_path):
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)
    # true_dict, summary_data = classfication_tf(data)
    summary_data = data["summary"]  # 마지막 요소는 summary
    true_dict = {}

    for img in data['results']:  # 마지막 summary 제외
        if img['best_caption'] != '마약과 관련된 장면이 없습니다.':
            img_name = os.path.splitext(img['image_name'])[0]
            best_caption = img['best_caption']
            true_dict[img_name] = best_caption
    # 이미지 선택 박스
    true_dict_keys = list(true_dict.keys())
    st.markdown("### 💊 **마약 장면 분석 결과**")
    select_img = st.selectbox("📌 **마약성 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)

    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        
        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_drug = summary_data['non-drug']
        drug_rate_true = summary_data['drug_rate_true']
        drug_rate_false = summary_data['drug_rate_false']
        drug_best_caption = summary_data['drug_best_caption']

        # 마약 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 마약 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **마약이 나타나지 않는 장면 수**: {non_drug} 개 (**{drug_rate_false * 100:.1f}%**)")
            st.write(f"- **마약 장면 수**: {total_scenes - non_drug} 개 (**{drug_rate_true * 100:.1f}%**)")
            
             # 진행 바로 마약 장면 비율 시각화
            st.markdown(f"#### **💊 마약 비율**: {drug_rate_true * 100:.1f}%")
            st.progress(min(round(drug_rate_true, 2), 1.0))  # 최대 1.0 (100%)까지


        with tab2:
            st.markdown("### 📌 **마약 장면 상세 분석**")
            for caption, count in drug_best_caption.items():
                st.write(f"- **{caption}**: {count} 건")
        
    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
        st.markdown(f"### **🔍 장면 분류**")
        st.write(f"💬 {true_dict[select_img]}")
    return 

#알코올
def display_alcohol_summary(file_path):
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)
    true_dict, summary_data = classfication_tf(data)

    # 이미지 선택 박스
     # 이미지 선택 박스
    true_dict_keys = list(true_dict.keys())
    st.markdown("### 🍺 **음주 장면 분석 결과**")
    select_img = st.selectbox("📌 **음주 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)
    
    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        st.subheader(f"🎬 {base_name} 분석 요약")
        st.write('--------')
        # 기본 정보
        total_scenes = summary_data['total_scenes']
        alcohol_false = summary_data['alcohol_false']
        alcohol_true = summary_data['alcohol_true']
        true_rate = summary_data['true_rate']
        false_rate = summary_data['false_rate']


        st.markdown("#### 📊 **장면 비율 분석**")
        st.write(f"- **총 장면 수**: {total_scenes} 개")
        st.write(f"- **비음주 장면 수**: {alcohol_false} 개 (**{false_rate * 100:.1f}%**)")
        st.write(f"- **음주 장면 수**: {alcohol_true} 개 (**{true_rate * 100:.1f}%**)")

        # 진행 바로 음주 장면 비율 시각화
        st.markdown(f"#### 🍾 **음주 비율**: {round(true_rate, 2)*100}%")
        st.progress(min(true_rate, 1.0))  # 최대 1.0 (100%)까지

    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
# 담배        
def display_somke_summary(file_path):
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)
    true_dict, summary_data = classfication_tf(data)

    # 이미지 선택 박스
     # 이미지 선택 박스
    true_dict_keys = list(true_dict.keys())
    st.markdown("### 🚬 **흡연 장면 분석 결과**")
    select_img = st.selectbox("📌 **흡연 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)
    
    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        st.subheader(f"🎬 {base_name} 분석 요약")
        st.write('--------')
        # 기본 정보
        total_scenes = summary_data['total_scenes']
        smoke_false = summary_data['smoking_false']
        smoke_true = summary_data['smoking_true']
        true_rate = summary_data['true_rate']
        false_rate = summary_data['false_rate']


        st.markdown("#### 📊 **장면 비율 분석**")
        st.write(f"- **총 장면 수**: {total_scenes} 개")
        st.write(f"- **비흡연 장면 수**: {smoke_false} 개 (**{false_rate * 100:.1f}%**)")
        st.write(f"- **흡연 장면 수**: {smoke_true} 개 (**{true_rate * 100:.1f}%**)")

        # 진행 바로 흡연 장면 비율 시각화
        st.markdown(f"#### 🚬 **흡연 비율**: {round(true_rate, 2)*100}%")
        st.progress(min(true_rate, 1.0))  # 최대 1.0 (100%)까지

    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
# 약물 종합        
def display_drug_total_summary(drug_file_path,alcohol_file_path,smoke_file_path):

    tab1, tab2, tab3 = st.tabs(['음주','흡연','마약'])
    with tab1:
        display_alcohol_summary(alcohol_file_path)
    with tab2:
        display_somke_summary(smoke_file_path)
    with tab3:
        display_drug_summary(drug_file_path)
    # display_drug_summary(drug_file_path)
    
#----------------------------------------주제--------------------------------    
def display_topic_summary(file_path):
    topic_str = filter_topic(file_path)

    st.markdown("### 🎬 **주제 분석 결과**")
    st.markdown("---")

    # 주제 키워드와 설명 강조
    st.markdown("### 🏷️ **주제 키워드 3개와 설명**")
    lines = topic_str.split("\n")
    keyword_section = True  # 주제 키워드 부분을 추적하기 위한 플래그

    for line in lines:
        if "전반적 설명" in line:
            st.markdown("---")
            st.markdown("### 📌 **전반적 설명**")
            keyword_section = False  # 이후부터는 전반적 설명 부분
            continue
        
        if keyword_section and line.strip():
            if " : " in line:
                keyword, desc = line.split(" : ", 1)
                st.write(f"🔹 **{keyword}**: {desc}")
        elif line.strip():
            if "작품의 표현 방식" in line:
                st.write(f"🖌️ **{line}**")
            elif "메시지 전달 의도" in line:
                st.write(f"💡 **{line}**")
            elif "장르적 특성" in line:
                st.write(f"🎭 **{line}**")
            else:
                st.write(line)

#모방위험
def display_imitation_summary(file_path):
    """모방위험 장면 분석 결과를 Streamlit에서 출력하는 함수"""
    
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)

    # JSON 데이터가 비어 있는 경우 예외 처리
    if not data:
        return

    # Summary 데이터 가져오기
    summary_data = data[-1]["summary"]
    high_risk = summary_data["high_risk"]
    medium_risk = summary_data["medium_risk"]
    
    total_scenes = len(data) - 1  # summary 제외한 총 장면 수
    high_count = len(high_risk)
    medium_count = len(medium_risk)
    low_count = total_scenes - (high_count + medium_count)

    high_ratio = high_count / total_scenes * 100
    medium_ratio = medium_count / total_scenes * 100
    low_ratio = low_count / total_scenes * 100

    # Streamlit UI - Summary 먼저 출력
    st.markdown("### 👥 **모방위험 장면 분석 결과**")

    # Low Risk는 제외하고 Medium, High만 선택할 수 있도록 데이터 필터링
    im_data = {k: v for item in data if isinstance(item, dict) for k, v in item.items() if k != 'summary'}
    filtered_data = {k: v for k, v in im_data.items() if v["mimicry_risk"] in ["Medium", "High"]}

    # 🟡 Medium / 🔴 High 위험도에 따라 레이블 추가
    selectbox_options = ['📊 Summary'] + [
        f"{'🟡 Medium' if v['mimicry_risk'] == 'Medium' else '🔴 High'} - {k}"
        for k, v in filtered_data.items()
    ]

    # 📌 **Medium & High 이미지 선택 박스**
    select_img_label = st.selectbox("🔍 **모방위험이 감지된 이미지 선택** (Medium, High만)", selectbox_options, index=0)

    if select_img_label == '📊 Summary':
        # 📊 **요약 정보**
        st.markdown("### 📊 **모방위험 장면 요약 분석**")
        st.write(f"- **총 장면 수**: {total_scenes} 개")
        st.write(f"- 🟥 **High Risk (높음)**: {high_count} 개 (**{high_ratio:.1f}%**)")
        st.progress(high_ratio / 100)

        st.write(f"- 🟧 **Medium Risk (중간)**: {medium_count} 개 (**{medium_ratio:.1f}%**)")
        st.progress(medium_ratio / 100)

        st.write(f"- 🟢 **Low Risk (낮음)**: {low_count} 개 (**{low_ratio:.1f}%**)")
        st.progress(low_ratio / 100)

    else:
        # 선택된 이미지 키 추출 (라벨 제거)
        select_img = select_img_label.split(" - ")[1]

        # 📷 **개별 이미지 표시**
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.markdown(f"### 📷 **선택한 장면: {select_img}**")
        st.image(img_path, caption=f"🖼️ {select_img}")
        
        # 장면에 대한 설명 표시
        scene_data = filtered_data[select_img]
        context = scene_data.get('context', '설명 없음')
        risk_behavior = scene_data.get('risk_behavior', '없음')
        mimicry_risk = scene_data.get('mimicry_risk', '없음')

        # 모방위험 수준 색상 지정
        risk_levels = {
            "Medium": ("🟡 **Medium** (중간)", "⚠️ 모방 가능성이 있습니다."),
            "High": ("🔴 **High** (높음)", "🚨 위험한 수준으로 모방 가능성이 큽니다!")
        }
        
        risk_label, risk_message = risk_levels.get(mimicry_risk, ("⚪ **Unknown** (알 수 없음)", "정보가 부족합니다."))

        st.markdown("### **🔍 장면 분석**")
        st.write(f"💬 **설명**: {context}")
        st.write(f"⚠️ **위험 요소**: {risk_behavior}")
        st.markdown(f"🛑 **모방위험 수준**: {risk_label}")

# Streamlit 실행
def streamlit_summary_def(base_name):#영상이름 ex) 스파이
    select_category = st.selectbox("📌 **분류 기준 선택**", ['주제','대사','공포','약물','폭력성','선정성','모방위험'], index=0)
    st.write("-----------------")
    if select_category == '공포':
        display_horror_summary(file_path = f'result/{base_name}/result_json/{base_name}_horror_json.json')
    elif select_category == '폭력성':  
        display_violence_summary(file_path = f'result/{base_name}/result_json/{base_name}_violence_img_json.json')
    elif select_category == '선정성':  
        display_sexuality_summary(file_path = f'result/{base_name}/result_json/{base_name}_sexuality_img_json.json')    
    elif select_category == '대사':  
        display_lines_summary(file_path=f'result/{base_name}/result_json/{base_name}_lines_json.json') 
    elif select_category == '약물':  
       display_drug_total_summary(drug_file_path=f'result/{base_name}/result_json/{base_name}_drug_json.json',
                                  alcohol_file_path=f'result/{base_name}/result_json/{base_name}_alcohol_json.json',
                                  smoke_file_path=f'result/{base_name}/result_json/{base_name}_smoking_json.json')
    elif select_category == '주제':
        display_topic_summary(file_path=f'result/{base_name}/result_json/{base_name}_topic_json.json')
    elif select_category == '모방위험':
        display_imitation_summary(file_path=f'result/{base_name}/result_json/{base_name}_imitation_json.json')
if __name__ == "__main__":
    base_name='스파이'
    streamlit_summary_def(base_name)