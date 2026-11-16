import streamlit as st
import time
from src.controllers.student_controller import handle_enroll_subject
from src.database.subject_db import get_subject_by_code


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state["student_data"]["student_id"]

    subject = get_subject_by_code(subject_code)
    if not subject:
        st.error(f"Subject Code '{subject_code}' not found!")
        if st.button("Close"):
            st.query_params.clear()
            st.rerun()
        return

    st.markdown(f"Would you like to enroll in **{subject['name']}** ({subject['subject_code']})?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("No thanks"):
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.button("Yes, enroll now!", type="primary", width="stretch"):
            success, msg = handle_enroll_subject(student_id, subject_code)
            if success:
                st.success(msg)
                st.query_params.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.info(msg)
