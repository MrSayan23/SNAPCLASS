import streamlit as st
from src.controllers.teacher_controller import handle_create_subject


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of the new subject")
    sub_code = st.text_input("Subject Code", placeholder="CS101")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")

    if st.button("Create Subject Now", type="primary", width="stretch"):
        success, message = handle_create_subject(sub_code, sub_name, sub_section, teacher_id)
        if success:
            st.toast(message)
            st.rerun()
        else:
            st.warning(message)
