import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="DLC Operation", layout="wide")
st.title("📘 Distance Learning Committee Operation")

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

    uploaded_file = st.file_uploader("국문 이름만 있는 엑셀파일을 업로드하세요. 외국인 교원일 경우에도 국문으로 입력하세요. 이메일 정보와 영문 이름 정보가 통합된 엑셀파일을 다운받으실 수 있습니다.", type=["xlsx"])
    if uploaded_file:
        input_df = pd.read_excel(uploaded_file)
        merged_df = input_df.merge(st.session_state.faculty_db, on="Korean_name", how="left")
        st.success("병합 완료! 아래에서 다운로드하세요.")
        st.dataframe(merged_df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            merged_df.to_excel(writer, index=False)
        st.download_button("📥 엑셀 다운로드", data=output.getvalue(), file_name="faculty_email_result.xlsx")

    st.subheader("🔍 국문 이름으로 정보 검색")
    name_query = st.text_input("외국인 교원일 경우에도 국문으로 입력하세요.")
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

    name_query = st.text_input("🔍 Please input your Name. 한국일일 경우 국문이름을 입력해주세요.")
    if name_query:
        results = st.session_state.course_modality_db[
            st.session_state.course_modality_db["Name"] == name_query
        ]
        if not results.empty:
            # ✅ 신청 여부 표시 (비밀번호 없이도)
            for idx, row in results.iterrows():
                course_title = row["Course Title"]
                apply_status = row["Apply this semester"]
                if apply_status == "YES":
                    st.write(f"✅ 신청됨: {course_title}")
                else:
                    st.write(f"🕒 미신청: {course_title}")

            # ✅ 기본 정보 테이블 표시
            st.dataframe(results.drop(columns=["Apply this semester", "password"]))

            # ✅ 비밀번호 입력 후 신청/삭제/Reason 처리
            password = st.text_input("🔐 4자리 숫자 비밀번호 입력", type="password")
            if password and len(password) == 4:
                found = False
                for _, row in results.iterrows():
                    if str(row["password"]) == str(password):
                        found = True
                        original_idx = row.name  # ✅ 원본 인덱스 확보
                        current_status = st.session_state.course_modality_db.at[original_idx, "Apply this semester"]
                        reason = st.session_state.course_modality_db.at[original_idx, "Reason for Applying"]

                        if current_status != "YES":
                            reason_input = st.text_area(
                                f"✍️ Reason for Applying - {row['Course Title']}",
                                value=reason if pd.notna(reason) else "",
                                key=f"reason_{original_idx}"
                            )
                            if st.button(f"📌 Apply this semester - {row['Course Title']}", key=f"apply_{original_idx}"):
                                st.session_state.course_modality_db.at[original_idx, "Apply this semester"] = "YES"
                                st.session_state.course_modality_db.at[original_idx, "Reason for Applying"] = reason_input
                                st.success("신청 완료! Reason이 저장되었습니다.")
                        else:
                            st.write(f"✅ 이미 신청됨: {row['Course Title']}")
                            st.text_area(
                                f"📄 저장된 Reason for Applying - {row['Course Title']}",
                                value=reason if pd.notna(reason) else "",
                                disabled=True,
                                key=f"reason_view_{original_idx}"
                            )
                            if st.button(f"🗑️ 신청 취소 - {row['Course Title']}", key=f"delete_{original_idx}"):
                                st.session_state.course_modality_db.at[original_idx, "Apply this semester"] = ""
                                st.session_state.course_modality_db.at[original_idx, "Reason for Applying"] = ""
                                st.success("신청이 취소되었습니다.")
                if not found:
                    st.warning("입력한 비밀번호와 일치하는 항목이 없습니다.")

        else:
            st.warning("해당 이름이 데이터베이스에 없습니다.")

    st.divider()
    st.subheader("(관리자용) 최종 온라인 수업 신청 사유 정보 보기")
    admin_pw = st.text_input("관리자 PW 입력", type="password")
    if admin_pw == "7777":
        st.dataframe(st.session_state.course_modality_db)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state.course_modality_db.to_excel(writer, index=False)
        st.download_button("📥 전체 엑셀 다운로드", data=output.getvalue(), file_name="course_modality_db.xlsx")


# 🔀 메뉴 선택
menu = st.sidebar.radio("원하시는 기능을 선택하세요", ["Faculty Email Finder", "Course Modality DB"])
if menu == "Faculty Email Finder":
    faculty_email_finder()
else:
    course_modality_db()
