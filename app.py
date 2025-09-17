import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="DLC Operation", layout="wide")
st.title("📘 DLC Operation")

# Session state 초기화
if "faculty_db" not in st.session_state:
    st.session_state.faculty_db = pd.DataFrame(columns=["Korean_name", "English_name", "Category", "Email"])
if "course_modality_db" not in st.session_state:
    st.session_state.course_modality_db = pd.DataFrame(columns=[
        "Name", "Year Semester", "Language", "Course Title", "Time Slot", "Day", "Time", "Frequency",
        "Course format", "Reason for Applying", "Modified", "Apply this semester", "password"
    ])

# ✅ 초기 엑셀 파일 자동 로딩
if st.session_state.faculty_db.empty:
    try:
        st.session_state.faculty_db = pd.read_excel("faculty_db.xlsx")
    except:
        st.warning("faculty_db.xlsx 파일을 찾을 수 없습니다.")

if st.session_state.course_modality_db.empty:
    try:
        st.session_state.course_modality_db = pd.read_excel("course_modality_db.xlsx")
    except:
        st.warning("course_modality_db.xlsx 파일을 찾을 수 없습니다.")

# 📧 Faculty Email Finder
def faculty_email_finder():
    st.header("📧 Faculty Email Finder")

    uploaded_file = st.file_uploader("Korean_name만 있는 엑셀 업로드", type=["xlsx"])
    if uploaded_file:
        input_df = pd.read_excel(uploaded_file)
        merged_df = input_df.merge(st.session_state.faculty_db, on="Korean_name", how="left")
        st.success("병합 완료! 아래에서 다운로드하세요.")
        st.dataframe(merged_df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            merged_df.to_excel(writer, index=False)
        st.download_button("📥 엑셀 다운로드", data=output.getvalue(), file_name="faculty_email_result.xlsx")

    st.subheader("🔍 이름으로 정보 검색")
    name_query = st.text_input("Korean_name 입력")
    if name_query:
        result = st.session_state.faculty_db[st.session_state.faculty_db["Korean_name"] == name_query]
        if not result.empty:
            row = result.iloc[0]
            st.write(f"**English_name**: {row['English_name']}")
            st.write(f"**Category**: {row['Category']}")
            st.write("**Email**:")
            st.text_input("📋 Ctrl+V를 클릭하여 이메일정보를 복사하세요", value=row['Email'], disabled=False)

        else:
            st.warning("해당 이름이 데이터베이스에 없습니다.")

# 📚 Course Modality DB
def course_modality_db():
    st.header("📚 Course Modality DB")

    name_query = st.text_input("🔍 Name 입력")
    if name_query:
        results = st.session_state.course_modality_db[st.session_state.course_modality_db["Name"] == name_query]
        if not results.empty:
            st.dataframe(results.drop(columns=["Apply this semester", "password"]))
            password = st.text_input("🔐 4자리 숫자 비밀번호 입력", type="password")
            if password and len(password) == 4:
                for idx, row in results.iterrows():
                    if row["password"] == password:
                        if row["Apply this semester"] != "YES":
                            if st.button(f"📌 Apply this semester - {row['Course Title']}", key=f"apply_{idx}"):
                                st.session_state.course_modality_db.at[idx, "Apply this semester"] = "YES"
                                st.success("신청 완료!")
                        else:
                            st.write(f"✅ 이미 신청됨: {row['Course Title']}")
                            if st.button(f"🗑️ Delete 신청 - {row['Course Title']}", key=f"delete_{idx}"):
                                st.session_state.course_modality_db.at[idx, "Apply this semester"] = ""
                                st.success("삭제 완료!")
        else:
            st.warning("해당 이름이 데이터베이스에 없습니다.")

    st.divider()
    st.subheader("(관리자용) 최종 정보 보기")
    admin_pw = st.text_input("관리자 비밀번호 입력", type="password")
    if admin_pw == "7777":
        st.dataframe(st.session_state.course_modality_db)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state.course_modality_db.to_excel(writer, index=False)
        st.download_button("📥 전체 엑셀 다운로드", data=output.getvalue(), file_name="course_modality_db.xlsx")

# 🔀 메뉴 선택
menu = st.sidebar.radio("기능 선택", ["Faculty Email Finder", "Course Modality DB"])
if menu == "Faculty Email Finder":
    faculty_email_finder()
else:
    course_modality_db()
