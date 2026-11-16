import streamlit as st
from src.database.teacher_db import (
    check_teacher_exists,
    create_teacher,
    login_teacher,
)
from src.database.subject_db import (
    create_subject,
    get_teacher_subjects,
)
from src.database.attendance_db import (
    get_attendance_for_teacher,
)


def handle_teacher_register(username, name, password, confirm_password):
    """Business logic for teacher registration."""
    username = (username or "").strip()
    name = (name or "").strip()

    if not username or not name or not password:
        return False, "All fields are required!"

    if password != confirm_password:
        return False, "Passwords do not match!"

    if check_teacher_exists(username):
        return False, "Username already taken! Please choose another."

    try:
        teacher = create_teacher(username, name, password)
        if teacher:
            return True, "Successfully registered! Please login."
        return False, "Failed to create account. Please try again."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def handle_teacher_login(username, password):
    """Business logic for teacher login."""
    username = (username or "").strip()

    if not username or not password:
        return False, "Please enter both username and password."

    teacher = login_teacher(username, password)
    if teacher:
        st.session_state["teacher_data"] = teacher
        st.session_state["is_logged_in"] = True
        st.session_state["user_role"] = "teacher"
        return True, f"Welcome back, {teacher['name']}!"

    return False, "Invalid username or password combo."


def handle_teacher_logout():
    """Logs out the teacher and clears session state."""
    st.session_state["is_logged_in"] = False
    st.session_state.pop("teacher_data", None)
    st.session_state.pop("user_role", None)


def handle_create_subject(subject_code, name, section, teacher_id):
    """Validates and creates a new subject for a teacher."""
    subject_code = (subject_code or "").strip().upper()
    name = (name or "").strip()
    section = (section or "").strip().upper()

    if not subject_code or not name or not section:
        return False, "All subject fields (code, name, section) are required!"

    try:
        created = create_subject(subject_code, name, section, teacher_id)
        if created:
            return True, f"Subject '{name}' created successfully!"
        return False, "Could not create subject. Please try again."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_teacher_dashboard_data(teacher_id):
    """Fetches subjects and attendance records for the teacher dashboard."""
    subjects = get_teacher_subjects(teacher_id)
    records = get_attendance_for_teacher(teacher_id)
    return {
        "subjects": subjects,
        "records": records,
    }
