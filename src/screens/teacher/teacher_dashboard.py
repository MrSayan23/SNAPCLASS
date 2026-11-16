import streamlit as st
import pandas as pd
from datetime import datetime

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.ui.base_layout import style_background_dashboard

from src.controllers.teacher_controller import (
    handle_teacher_logout,
    get_teacher_dashboard_data,
)
from src.controllers.attendance_controller import process_face_attendance
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog


def render_teacher_dashboard():
    # Auth guard — redirect if not logged in
    if "teacher_data" not in st.session_state or not st.session_state.get("is_logged_in"):
        try:
            st.switch_page("src/screens/teacher/teacher_login.py")
        except Exception:
            pass
        return

    style_background_dashboard()

    teacher_data = st.session_state["teacher_data"]
    teacher_id = teacher_data["teacher_id"]

    # Header + Logout
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}")
        if st.button("Logout", type="secondary", key="logoutbtn", shortcut="control+backspace"):
            handle_teacher_logout()
            st.switch_page("src/screens/home_screen.py")

    st.space()

    # Tabs
    if "current_teacher_tab" not in st.session_state:
        st.session_state["current_teacher_tab"] = "take_attendance"

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state["current_teacher_tab"] == "take_attendance" else "tertiary"
        if st.button("Take Attendance", type=type1, width="stretch", icon=":material/ar_on_you:"):
            st.session_state["current_teacher_tab"] = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state["current_teacher_tab"] == "manage_subjects" else "tertiary"
        if st.button("Manage Subjects", type=type2, width="stretch", icon=":material/book_ribbon:"):
            st.session_state["current_teacher_tab"] = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state["current_teacher_tab"] == "attendance_records" else "tertiary"
        if st.button("Attendance Records", type=type3, width="stretch", icon=":material/cards_stack:"):
            st.session_state["current_teacher_tab"] = "attendance_records"
            st.rerun()

    st.divider()

    # TAB 1: TAKE ATTENDANCE
    if st.session_state["current_teacher_tab"] == "take_attendance":
        st.header("Take AI Attendance")

        if "attendance_images" not in st.session_state:
            st.session_state["attendance_images"] = []

        dash_data = get_teacher_dashboard_data(teacher_id)
        subjects = dash_data["subjects"]

        if not subjects:
            st.warning("You haven't created any subjects yet! Please go to 'Manage Subjects' to create one.")
        else:
            subject_options = {f"{s['name']} - {s['subject_code']}": s["subject_id"] for s in subjects}

            col1, col2, col3 = st.columns([3, 1, 1], vertical_alignment="bottom")

            with col1:
                selected_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
                selected_subject_id = subject_options[selected_label]

            with col2:
                if st.button("Add Photos", type="primary", icon=":material/photo_prints:", width="stretch"):
                    add_photos_dialog()

            with col3:
                if st.button("Voice Roll Call", type="secondary", icon=":material/mic:", width="stretch"):
                    voice_attendance_dialog(selected_subject_id)

            st.divider()

            # Display uploaded photos gallery
            if st.session_state["attendance_images"]:
                st.header("Classroom Photos")
                gallery_cols = st.columns(4)
                for idx, img in enumerate(st.session_state["attendance_images"]):
                    with gallery_cols[idx % 4]:
                        st.image(img, width="stretch", caption=f"Photo {idx + 1}")

            has_photos = bool(st.session_state["attendance_images"])
            c1, c2 = st.columns(2)

            with c1:
                if st.button("Clear Photos", width="stretch", type="tertiary", icon=":material/delete:", disabled=not has_photos):
                    st.session_state["attendance_images"] = []
                    st.rerun()

            with c2:
                if st.button("Run Face Analysis", width="stretch", type="secondary", icon=":material/analytics:", disabled=not has_photos):
                    with st.spinner("Deep scanning classroom photos with Face AI..."):
                        success, msg, table_data, logs = process_face_attendance(
                            st.session_state["attendance_images"], selected_subject_id
                        )
                        if success:
                            st.toast(msg)
                            df = pd.DataFrame(table_data)
                            attendance_result_dialog(df, logs)
                        else:
                            st.error(msg)

    # TAB 2: MANAGE SUBJECTS
    elif st.session_state["current_teacher_tab"] == "manage_subjects":
        col1, col2 = st.columns(2)
        with col1:
            st.header("Manage Subjects")
        with col2:
            if st.button("Create New Subject", type="primary", width="stretch"):
                create_subject_dialog(teacher_id)

        dash_data = get_teacher_dashboard_data(teacher_id)
        subjects = dash_data["subjects"]

        if subjects:
            cols = st.columns(2)
            for i, sub in enumerate(subjects):
                stats = [
                    ("👥", "Students", sub["total_students"]),
                    ("📅", "Classes", sub["total_classes"]),
                ]

                def make_share_btn(s=sub):
                    def share_fn():
                        if st.button(f"Share Code: {s['subject_code']}", key=f"share_{s['subject_id']}", icon=":material/share:"):
                            share_subject_dialog(s["name"], s["subject_code"])
                    return share_fn

                with cols[i % 2]:
                    subject_card(
                        name=sub["name"],
                        code=sub["subject_code"],
                        section=sub["section"],
                        stats=stats,
                        footer_callback=make_share_btn(sub),
                    )
        else:
            st.info("No subjects found. Click 'Create New Subject' above to get started!")

    # TAB 3: ATTENDANCE RECORDS
    elif st.session_state["current_teacher_tab"] == "attendance_records":
        st.header("Attendance Records")

        dash_data = get_teacher_dashboard_data(teacher_id)
        records = dash_data["records"]

        if not records:
            st.info("No attendance sessions recorded yet.")
        else:
            data = []
            for r in records:
                ts = r.get("timestamp")
                data.append({
                    "ts_group": ts.split("T")[0] if ts else None,
                    "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
                    "Subject": r["subject_name"],
                    "Subject Code": r["subject_code"],
                    "is_present": bool(r.get("is_present", False)),
                })

            df = pd.DataFrame(data)
            summary = (
                df.groupby(["ts_group", "Time", "Subject", "Subject Code"])
                .agg(
                    Present_Count=("is_present", "sum"),
                    Total_Count=("is_present", "count"),
                )
                .reset_index()
            )
            summary["Attendance Stats"] = (
                "✅ " + summary["Present_Count"].astype(str) + " / "
                + summary["Total_Count"].astype(str) + " Students"
            )
            display_df = summary.sort_values(by="ts_group", ascending=False)[
                ["Time", "Subject", "Subject Code", "Attendance Stats"]
            ]
            st.dataframe(display_df, width="stretch", hide_index=True)

    footer_dashboard()


render_teacher_dashboard()
