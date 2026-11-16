import streamlit as st
from src.controllers.attendance_controller import confirm_and_save_attendance


def show_attendance_result(df, logs):
    st.write("Please review attendance before confirming.")
    st.dataframe(df, hide_index=True, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Discard", width="stretch"):
            st.session_state["voice_attendance_results"] = None
            st.session_state["attendance_images"] = []
            st.rerun()

    with col2:
        if st.button("Confirm & Save", width="stretch", type="primary"):
            success, message = confirm_and_save_attendance(logs)
            if success:
                st.toast(message, icon="✅")
                st.session_state["attendance_images"] = []
                st.session_state["voice_attendance_results"] = None
                st.rerun()
            else:
                st.error(message)


@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)
