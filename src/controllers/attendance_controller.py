import numpy as np
from PIL import Image

from src.database.subject_db import get_enrolled_students
from src.database.attendance_db import create_attendance
from src.pipelines.face_pipeline import predict_attendance
from src.pipelines.voice_pipeline import process_bulk_audio


def process_face_attendance(images, selected_subject_id):
    """Scans classroom photos and generates present/absent logs for enrolled students."""
    if not images:
        return False, "No photos provided for analysis.", [], []

    enrolled_students = get_enrolled_students(selected_subject_id)
    if not enrolled_students:
        return False, "No students are enrolled in this course yet.", [], []

    all_detected_ids = {}
    total_faces = 0

    for idx, img in enumerate(images):
        if not isinstance(img, np.ndarray):
            img_np = np.array(img.convert("RGB"))
        else:
            img_np = img

        detected, _, num_faces = predict_attendance(img_np)
        total_faces += num_faces

        if detected:
            for sid in detected.keys():
                student_id = int(sid)
                all_detected_ids.setdefault(student_id, []).append(f"Photo {idx + 1}")

    table_data = []
    logs_to_save = []

    for student in enrolled_students:
        sid = student["student_id"]
        is_present = sid in all_detected_ids
        detections = all_detected_ids.get(sid, [])

        table_data.append({
            "Student ID": sid,
            "Name": student["name"],
            "Status": "✅ Present" if is_present else "❌ Absent",
            "Matched In": ", ".join(detections) if is_present else "None",
        })

        logs_to_save.append({
            "subject_id": selected_subject_id,
            "student_id": sid,
            "is_present": is_present,
        })

    return True, f"Scan complete! Found {total_faces} faces.", table_data, logs_to_save


def process_voice_attendance(audio_bytes, selected_subject_id):
    """Processes bulk classroom audio to detect student voices."""
    if not audio_bytes:
        return False, "No audio recorded.", [], []

    enrolled_students = get_enrolled_students(selected_subject_id)
    if not enrolled_students:
        return False, "No students enrolled in this course.", [], []

    candidates_dict = {
        s["student_id"]: s["voice_embedding"]
        for s in enrolled_students
        if s.get("voice_embedding")
    }

    if not candidates_dict:
        return False, "No enrolled students have voice embeddings registered.", [], []

    detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

    table_data = []
    logs_to_save = []

    for student in enrolled_students:
        sid = student["student_id"]
        score = detected_scores.get(sid, 0.0)
        is_present = bool(score > 0)

        table_data.append({
            "Student ID": sid,
            "Name": student["name"],
            "Status": "✅ Present" if is_present else "❌ Absent",
            "Match Confidence": f"{score:.2f}" if is_present else "N/A",
        })

        logs_to_save.append({
            "subject_id": selected_subject_id,
            "student_id": sid,
            "is_present": is_present,
        })

    return True, "Voice analysis complete!", table_data, logs_to_save


def confirm_and_save_attendance(logs):
    """Commits attendance logs to the database."""
    if not logs:
        return False, "No attendance records to save."

    try:
        create_attendance(logs)
        return True, "Attendance confirmed and saved successfully!"
    except Exception as e:
        return False, f"Database error saving attendance: {str(e)}"
