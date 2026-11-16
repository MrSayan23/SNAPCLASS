import streamlit as st
import time
from src.controllers.student_controller import handle_enroll_subject


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write("Enter the subject code provided by your teacher to enroll")
    join_code = st.text_input("Subject Code", placeholder="e.g. CS101")

    if st.button("Enroll now", type="primary", width="stretch"):
        student_id = st.session_state["student_data"]["student_id"]
        success, message = handle_enroll_subject(student_id, join_code)
        if success:
            st.success(message)
            time.sleep(1)
            st.rerun()
        else:
            st.warning(message)