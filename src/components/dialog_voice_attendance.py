import streamlit as st
import pandas as pd
from src.controllers.attendance_controller import process_voice_attendance
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write("Record audio of students saying 'I am present'. Then AI will recognize the students.")

    audio_data = st.audio_input("Record classroom audio")

    if st.button("Analyze Audio", width="stretch", type="primary"):
        if audio_data:
            with st.spinner("Processing audio data with Voice AI..."):
                audio_bytes = audio_data.read()
                success, msg, table_data, logs = process_voice_attendance(
                    audio_bytes, selected_subject_id
                )
                if success:
                    st.toast(msg)
                    st.session_state["voice_attendance_results"] = (
                        pd.DataFrame(table_data),
                        logs,
                    )
                else:
                    st.error(msg)
        else:
            st.warning("Please record some audio first!")

    if st.session_state.get("voice_attendance_results"):
        st.divider()
        df_results, logs = st.session_state["voice_attendance_results"]
        show_attendance_result(df_results, logs)
