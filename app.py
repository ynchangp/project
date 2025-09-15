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
        "Name", "Year Semester", "Language", "Course Title", "Time Slot", "Day", "Time",
        "Frequency", "Course format", "Reason for Applying", "Modified", "Apply this semester", "password"
    ])

tab1, tab2 = st.tabs(["📧 Faculty Email Finder", "📚 Course Modality DB"])

# -------------------------------
# 📧 Faculty Email Finder
# -------------------------------
with tab1:
    st.subheader("기능 1: Faculty Email List 엑셀 업로드")
    uploaded_file = st.file_uploader("엑셀 파일 업로드 (Korean_name 컬럼 포함)", type=["xlsx"])
    if uploaded_file:
        input_df = pd.read_excel(uploaded_file)
        merged_df = pd.merge(input_df, st.session_state.faculty_db, on="Korean_name", how="left")
        st.dataframe(merged_df)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            merged_df.to_excel(writer, index=False)
        st.download_button("📥 결과 엑셀 다운로드", data=buffer.getvalue(), file_name="faculty_email_result.xlsx")

    st.divider()
    st.subheader("기능 2: 교원명 검색")
    name_input = st.text_input("국문 교원명 입력")
    if name_input:
        result = st.session_state.faculty_db[st.session_state.faculty_db["Korean_name"] == name_input]
        if not result.empty:
            st.write(result[["English_name", "Category", "Email"]])
            email = result.iloc[0]["Email"]
            st.code(email, language="text")
            st.button("📋 이메일 복사", on_click=lambda: st.toast("이메일 복사됨: " + email))
        else:
            st.warning("해당 교원 정보를 찾을 수 없습니다.")

# -------------------------------
# 📚 Course Modality DB
# -------------------------------
with tab2:
    st.subheader("기능 1: 강의 정보 검색")
    name_query = st.text_input("국문 이름 입력")
    course_results = pd.DataFrame()
    if name_query:
        course_results = st.session_state.course_modality_db[st.session_state.course_modality_db["Name"] == name_query]
        if not course_results.empty:
            st.dataframe(course_results.drop(columns=["Apply this semester", "password"]))
        else:
            st.warning("해당 이름의 강의 정보가 없습니다.")

    st.divider()
    st.subheader("기능 2 & 3: Apply this semester 설정 및 삭제")
    if not course_results.empty:
        pw_input = st.text_input("비밀번호 (4자리 숫자)", type="password")
        if pw_input and len(pw_input) == 4:
            for idx, row in course_results.iterrows():
                if row["password"] == pw_input:
                    if row["Apply this semester"] != "YES":
                        if st.button(f"✅ Apply this semester 설정 - {row['Course Title']}", key=f"apply_{idx}"):
                            st.session_state.course_modality_db.at[idx, "Apply this semester"] = "YES"
                            st.success(f"{row['Course Title']}에 대해 Apply 설정 완료")
                    else:
                        st.write(f"✔️ 이미 Apply됨: {row['Course Title']}")
                        if st.button(f"🗑️ Apply 삭제 - {row['Course Title']}", key=f"delete_{idx}"):
                            st.session_state.course_modality_db.at[idx, "Apply this semester"] = ""
                            st.success(f"{row['Course Title']}의 Apply 삭제 완료")

    st.divider()
    st.subheader("🔐 (관리자용) 최종 정보 보기")
    admin_pw = st.text_input("관리자 비밀번호 (4자리)", type="password", key="admin_pw")
    if admin_pw and len(admin_pw) == 4:
        admin_view = st.session_state.course_modality_db[st.session_state.course_modality_db["password"] == admin_pw]
        if not admin_view.empty:
            st.dataframe(admin_view)
            buffer2 = io.BytesIO()
            with pd.ExcelWriter(buffer2, engine="xlsxwriter") as writer:
                admin_view.to_excel(writer, index=False)
            st.download_button("📥 전체 엑셀 다운로드", data=buffer2.getvalue(), file_name="course_modality_full.xlsx")
        else:
            st.warning("비밀번호가 일치하는 정보가 없습니다.")
