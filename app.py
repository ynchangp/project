import streamlit as st
import pandas as pd
from googletrans import Translator
import io

# 번역기 초기화
translator = Translator()

# 페이지 설정
st.set_page_config(page_title="KDI 대학원 원격수업운영위원회 앱", layout="wide")

# 데이터 로드 함수
@st.cache_data
def load_faculty_db():
    return pd.read_excel("faculty_db.xlsx")

@st.cache_data
def load_course_db():
    return pd.read_excel("course_modality_db.xlsx")

faculty_db = load_faculty_db()
course_db = load_course_db()

# 엑셀 다운로드 함수
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["Faculty Email Finder", "Course Modality DB"])

# ---------------- Faculty Email Finder ----------------
if menu == "Faculty Email Finder":
    st.header("📧 Faculty Email Finder")

    uploaded_file = st.file_uploader("교원 리스트 업로드", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        merged = pd.merge(df, faculty_db, on=["국문명", "영문명"], how="left")
        st.dataframe(merged)
        st.download_button(
            label="📥 이메일 포함 엑셀 다운로드",
            data=to_excel(merged),
            file_name="faculty_with_email.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.subheader("🔍 개별 검색")
    name_search = st.text_input("교원 이름 입력 (국문 또는 영문)")
    if name_search:
        result = faculty_db[(faculty_db["국문명"] == name_search) | (faculty_db["영문명"] == name_search)]
        if not result.empty:
            st.dataframe(result)
        else:
            st.warning("검색 결과가 없습니다.")

# ---------------- Course Modality DB ----------------
elif menu == "Course Modality DB":
    st.header("📚 Course Modality DB")

    uploaded_course = st.file_uploader("Course Modality DB 업로드", type=["xlsx"])
    if uploaded_course:
        new_data = pd.read_excel(uploaded_course)
        course_db = pd.concat([course_db, new_data], ignore_index=True)
        st.success("데이터가 추가되었습니다.")
        st.dataframe(course_db)

    st.subheader("🔍 검색")
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("Name 검색")
    with col2:
        search_format = st.text_input("Course format 검색")

    filtered = course_db.copy()
    if search_name:
        filtered = filtered[filtered["Name"].str.contains(search_name, na=False)]
    if search_format:
        filtered = filtered[filtered["Course format"].str.contains(search_format, na=False)]

    if not filtered.empty:
        # Reason for Applying 번역 추가
        if "Reason for Applying" in filtered.columns:
            filtered["Reason for Applying (EN)"] = filtered["Reason for Applying"].apply(
                lambda x: translator.translate(str(x), src='ko', dest='en').text if pd.notna(x) else None
            )
        st.dataframe(filtered)
    else:
        st.info("검색 결과가 없습니다.")

    st.subheader("📥 전체 다운로드 (국문명+영문명 포함)")
    merged_course = pd.merge(course_db, faculty_db[["국문명", "영문명"]], left_on="Name", right_on="국문명", how="left")
    st.download_button(
        label="전체 엑셀 다운로드",
        data=to_excel(merged_course),
        file_name="course_modality_full.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.subheader("📥 Year Semester별 다운로드")
    year_semester = st.text_input("Year Semester 입력 (예: 2025-1)")
    if year_semester:
        ys_filtered = course_db[course_db["Year Semester"] == year_semester]
        st.download_button(
            label=f"{year_semester} 데이터 다운로드",
            data=to_excel(ys_filtered),
            file_name=f"course_modality_{year_semester}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
