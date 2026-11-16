import streamlit as st
import numpy as np
from PIL import Image

from src.database.student_db import get_all_students, create_student
from src.database.subject_db import (
    get_subject_by_code,
    get_student_subjects,
    enroll_student_to_subject,
    unenroll_student_to_subject,
)
from src.database.attendance_db import get_student_attendance
from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    train_classifier,
)
from src.pipelines.voice_pipeline import get_voice_embedding


def handle_student_face_login(camera_photo):
    """Processes webcam image and identifies the student using FaceID."""
    if not camera_photo:
        return False, "Please take a photo.", None

    img = np.array(Image.open(camera_photo).convert("RGB"))
    detected, all_ids, num_faces = predict_attendance(img)

    if num_faces == 0:
        return False, "No face found! Position your face in the center.", None
    elif num_faces > 1:
        return False, "Multiple faces detected! Make sure only 1 person is in frame.", None

    if detected:
        student_id = list(detected.keys())[0]
        all_students = get_all_students()
        student = next((s for s in all_students if s["student_id"] == student_id), None)

        if student:
            st.session_state["is_logged_in"] = True
            st.session_state["user_role"] = "student"
            st.session_state["student_data"] = student
            return True, f"Welcome back, {student['name']}!", student

    return False, "Face not recognized. You might be a new student!", None


def handle_student_register(name, camera_photo, audio_bytes=None):
    """Enrolls a new student with face and optional voice embeddings."""
    name = (name or "").strip()
    if not name:
        return False, "Please enter your name."

    if not camera_photo:
        return False, "Please capture your face photo."

    img = np.array(Image.open(camera_photo).convert("RGB"))
    encodings = get_face_embeddings(img)

    if not encodings:
        return False, "Could not capture facial features. Please try again with good lighting."

    face_emb = encodings[0].tolist()

    # Optional voice enrollment
    voice_emb = None
    if audio_bytes:
        try:
            voice_emb = get_voice_embedding(audio_bytes)
        except Exception:
            pass

    created_student = create_student(name, face_embedding=face_emb, voice_embedding=voice_emb)

    if created_student:
        # Retrain SVM classifier with the new student
        train_classifier()

        st.session_state["is_logged_in"] = True
        st.session_state["user_role"] = "student"
        st.session_state["student_data"] = created_student
        return True, f"Profile created successfully! Welcome, {name}!"

    return False, "Failed to create student profile in database."


def handle_student_logout():
    """Logs out the student and clears session state."""
    st.session_state["is_logged_in"] = False
    st.session_state.pop("student_data", None)
    st.session_state.pop("user_role", None)


def handle_enroll_subject(student_id, subject_code):
    """Validates subject code and enrolls the student."""
    subject_code = (subject_code or "").strip().upper()
    if not subject_code:
        return False, "Please enter a subject code."

    subject = get_subject_by_code(subject_code)
    if not subject:
        return False, f"Subject code '{subject_code}' not found!"

    # Check if already enrolled
    enrolled_subjects = get_student_subjects(student_id)
    enrolled_ids = [s["subject_id"] for s in enrolled_subjects]
    if subject["subject_id"] in enrolled_ids:
        return False, f"You are already enrolled in {subject['name']}!"

    enroll_student_to_subject(student_id, subject["subject_id"])
    return True, f"Successfully enrolled in {subject['name']}!"


def handle_unenroll_subject(student_id, subject_id):
    """Unenrolls a student from a subject."""
    unenroll_student_to_subject(student_id, subject_id)
    return True, "Successfully unenrolled from course."


def get_student_dashboard_data(student_id):
    """Gathers enrolled subjects and attendance stats for a student."""
    subjects = get_student_subjects(student_id)
    logs = get_student_attendance(student_id)

    # Compute attendance statistics per subject
    stats_map = {}
    for log in logs:
        sid = log.get("subject_id")
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]["total"] += 1
        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    return {
        "subjects": subjects,
        "stats_map": stats_map,
    }
