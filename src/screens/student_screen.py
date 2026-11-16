import streamlit as st
import time

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.components.dialog_enroll import enroll_dialog

from src.controllers.student_controller import (
    handle_student_face_login,
    handle_student_register,
    handle_student_logout,
    handle_unenroll_subject,
    get_student_dashboard_data,
)


def student_dashboard():
    student_data = st.session_state["student_data"]
    student_id = student_data["student_id"]

    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}")
        if st.button("Logout", type="secondary", key="student_logout_btn", shortcut="control+backspace"):
            handle_student_logout()
            st.rerun()

    st.space()

    c1, c2 = st.columns(2)
    with c1:
        st.header("Your Enrolled Subjects")
    with c2:
        if st.button("Enroll in Subject", type="primary", width="stretch"):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading your enrolled subjects..."):
        dash_data = get_student_dashboard_data(student_id)
        subjects = dash_data["subjects"]
        stats_map = dash_data["stats_map"]

    if not subjects:
        st.info("You haven't enrolled in any subjects yet. Click 'Enroll in Subject' above!")
    else:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node["subjects"]
            sid = sub["subject_id"]
            stats = stats_map.get(sid, {"total": 0, "attended": 0})

            def make_unenroll_btn(subject_id=sid, subject_name=sub["name"]):
                def unenroll_fn():
                    if st.button("Unenroll from this course", key=f"unenroll_{subject_id}", type="tertiary", width="stretch", icon=":material/delete_forever:"):
                        success, msg = handle_unenroll_subject(student_id, subject_id)
                        if success:
                            st.toast(f"Unenrolled from {subject_name} successfully!")
                            st.rerun()
                        else:
                            st.error(msg)
                return unenroll_fn

            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=[
                        ("📅", "Total Classes", stats["total"]),
                        ("✅", "Attended", stats["attended"]),
                    ],
                    footer_callback=make_unenroll_btn(sid, sub["name"]),
                )

    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    # If student is already logged in, show dashboard
    if "student_data" in st.session_state and st.session_state.get("is_logged_in"):
        student_dashboard()
        return

    # Login / Register View
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type="secondary", key="loginbackbtn", shortcut="control+backspace"):
            st.switch_page("src/screens/home_screen.py")

    st.header("Login using FaceID", text_alignment="center")
    st.space()
    st.space()

    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        with st.spinner("AI is scanning face..."):
            success, msg, student = handle_student_face_login(photo_source)
            if success:
                st.toast(msg, icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.info(msg)
                # Show Registration Form if not recognized
                with st.container(border=True):
                    st.header("Register New Student Profile")
                    new_name = st.text_input("Enter your name", placeholder="e.g. Sayan Biswas")

                    st.subheader("Optional: Voice Enrollment")
                    st.info("Record a short voice phrase to enable Voice Attendance")

                    audio_data = None
                    try:
                        audio_data = st.audio_input("Record: 'I am present'")
                    except Exception:
                        pass

                    if st.button("Create Student Account", type="primary"):
                        if new_name:
                            with st.spinner("Creating profile & training AI..."):
                                audio_bytes = audio_data.read() if audio_data else None
                                reg_success, reg_msg = handle_student_register(
                                    new_name, photo_source, audio_bytes
                                )
                                if reg_success:
                                    st.toast(reg_msg, icon="🎉")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(reg_msg)
                        else:
                            st.warning("Please enter your name!")

    footer_dashboard()


# Direct execution for Streamlit page routing
student_screen()