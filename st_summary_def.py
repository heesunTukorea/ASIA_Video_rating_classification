import json
import streamlit as st
import os
from lines.lines_JSON import filter_by_category
#---------------------공통 함수 ----------------------------
# JSON 파일 로드 함수
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data  

# 공포 장면 분석 함수
def classfication_tf(data):
    summary_data = data[-1]  # 마지막 요소는 summary
    true_dict = {}

    for img in data[:-1]:  # 마지막 summary 제외
        if img['classification'] == True:
            img_name = os.path.splitext(img['image_name'])[0]
            best_caption = img['best_caption']
            true_dict[img_name] = best_caption

    return true_dict, summary_data


#-------------------------------공포 --------------------------------------------------------------
# Streamlit UI 구성 함수
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
    st.title("🕷️ 공포 장면 분석 결과")
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
    st.title("💥 폭력 장면 분석 결과")
    select_img = st.selectbox("📌 **폭력성 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)

    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        
        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_horror = summary_data['non-violence']
        horror_rate_true = summary_data['violence_rate_true']
        horror_rate_false = summary_data['violence_rate_false']
        horror_best_caption = summary_data['violence_best_caption']

        # 공포 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 폭력 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **폭력적이지 않은 장면 수**: {non_horror} 개 (**{horror_rate_false * 100:.1f}%**)")
            st.write(f"- **폭력 장면 수**: {total_scenes - non_horror} 개 (**{horror_rate_true * 100:.1f}%**)")

        with tab2:
            st.markdown("### 📌 **폭력 장면 상세 분석**")
            for caption, count in horror_best_caption.items():
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
    st.title("🔞 선정성 장면 분석 결과")
    select_img = st.selectbox("📌 **선정성 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)

    # 📌 **요약 정보 표시**
    if select_img == 'summary':

        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_horror = summary_data['non-sexual']
        horror_rate_true = summary_data['sexual_rate_true']
        horror_rate_false = summary_data['sexual_rate_false']
        horror_best_caption = summary_data['sexual_best_caption']

        # 선정성 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 선정성 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **비선정성 장면 수**: {non_horror} 개 (**{horror_rate_false * 100:.1f}%**)")
            st.write(f"- **선정성 장면 수**: {total_scenes - non_horror} 개 (**{horror_rate_true * 100:.1f}%**)")

        with tab2:
            st.markdown("### 📌 **선정성 장면 상세 분석**")
            for caption, count in horror_best_caption.items():
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
    st.title("🗣️ 대사 분석 결과")
    st.markdown("### 🎬 **욕설 및 혐오 표현 비율별 대사 분류**")
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
        st.markdown("### 📌 **대사 비율 요약**")
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
        st.markdown(f"### 📌 **{CATEGORY_LABELS[select_cate]} 리스트**")

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
    st.title("💊 마약 장면 분석 결과")
    select_img = st.selectbox("📌 **마약성 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)

    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        
        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_horror = summary_data['non-drug']
        horror_rate_true = summary_data['drug_rate_true']
        horror_rate_false = summary_data['drug_rate_false']
        horror_best_caption = summary_data['drug_best_caption']

        # 마약 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 마약 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **마약이 나타나지 않는 장면 수**: {non_horror} 개 (**{horror_rate_false * 100:.1f}%**)")
            st.write(f"- **마약 장면 수**: {total_scenes - non_horror} 개 (**{horror_rate_true * 100:.1f}%**)")

        with tab2:
            st.markdown("### 📌 **마약 장면 상세 분석**")
            for caption, count in horror_best_caption.items():
                st.write(f"- **{caption}**: {count} 건")

    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
        st.markdown(f"### **🔍 장면 분류**")
        st.write(f"💬 {true_dict[select_img]}")

def display_alcohol_summary(file_path):
    # 기본 경로 설정
    base_path = file_path.split("result/")[1].split("/result_json")[0]  
    base_name = os.path.basename(base_path)  
    img_folder_path = f'result/{base_name}/{base_name}_images_output'

    # JSON 데이터 로드
    data = load_json(file_path)
    true_dict, summary_data = classfication_tf(data)

    # 이미지 선택 박스
    true_dict_keys = list(true_dict.keys())
    st.title("🕷️ 음주 장면 분석 결과")
    select_img = st.selectbox("📌 **음주 해당 이미지 선택**", ['summary'] + true_dict_keys, index=0)
    
    # 📌 **요약 정보 표시**
    if select_img == 'summary':
        # st.title("🕷️ 음주 장면 분석 결과")
        st.subheader(f"🎬 {base_name} 분석 요약")

        # 기본 정보
        total_scenes = summary_data['total_scenes']
        non_horror = summary_data['non-horror']
        horror_rate_true = summary_data['horror_rate_true']
        horror_rate_false = summary_data['horror_rate_false']
        horror_best_caption = summary_data['horror_best_caption']

        # 음주 장면 비율 탭
        tab1, tab2 = st.tabs(['📊 장면 비율', '📌 음주 장면 상세 분석'])

        with tab1:
            st.markdown("### 📊 **장면 비율 분석**")
            st.write(f"- **총 장면 수**: {total_scenes} 개")
            st.write(f"- **비음주 장면 수**: {non_horror} 개 (**{horror_rate_false * 100:.1f}%**)")
            st.write(f"- **음주 장면 수**: {total_scenes - non_horror} 개 (**{horror_rate_true * 100:.1f}%**)")

        with tab2:
            st.markdown("### 📌 **음주 장면 상세 분석**")
            for caption, count in horror_best_caption.items():
                st.write(f"- **{caption}**: {count} 건")

    # 📌 **개별 이미지 표시**
    else:
        img_path = os.path.join(img_folder_path, f"{select_img}.png").replace("\\", "/")
        
        st.title(f"📷 {select_img}")
        st.image(img_path, caption=f"🖼️ {select_img}")
        st.markdown(f"### **🔍 장면 분류**")
        st.write(f"💬 {true_dict[select_img]}")

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
    # elif select_category == '약물':  
    #     display_lines_summary(file_path='result/스파이/result_json/스파이_lines_json.json')   
if __name__ == "__main__":
    base_name='스파이'
    streamlit_summary_def(base_name)