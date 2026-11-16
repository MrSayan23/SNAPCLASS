import json
from src.database.config import run_query, run_execute


def create_subject(subject_code, name, section, teacher_id):
    """Insert a new subject into the subjects table."""
    run_execute(
        "INSERT INTO subjects (subject_code, name, section, teacher_id) VALUES (%s, %s, %s, %s)",
        (subject_code, name, section, teacher_id),
    )
    rows = run_query(
        "SELECT subject_id, subject_code, name, section, teacher_id FROM subjects WHERE subject_code = %s",
        (subject_code,),
    )
    if rows:
        return {
            "subject_id": rows[0][0],
            "subject_code": rows[0][1],
            "name": rows[0][2],
            "section": rows[0][3],
            "teacher_id": rows[0][4],
        }
    return None


def get_subject_by_code(subject_code):
    """Find a subject by its code (e.g. 'CS101')."""
    rows = run_query(
        "SELECT subject_id, subject_code, name, section, teacher_id FROM subjects WHERE subject_code = %s",
        (subject_code,),
    )
    if rows:
        return {
            "subject_id": rows[0][0],
            "subject_code": rows[0][1],
            "name": rows[0][2],
            "section": rows[0][3],
            "teacher_id": rows[0][4],
        }
    return None


def get_teacher_subjects(teacher_id):
    """Fetch all subjects created by a teacher, with student and class counts."""
    sql = """
        SELECT 
            s.subject_id, 
            s.subject_code, 
            s.name, 
            s.section, 
            s.teacher_id,
            COUNT(DISTINCT ss.student_id) AS total_students,
            COUNT(DISTINCT DATE(al.timestamp)) AS total_classes
        FROM subjects s
        LEFT JOIN subject_students ss ON s.subject_id = ss.subject_id
        LEFT JOIN attendance_logs al ON s.subject_id = al.subject_id
        WHERE s.teacher_id = %s
        GROUP BY s.subject_id, s.subject_code, s.name, s.section, s.teacher_id
        ORDER BY s.subject_id DESC
    """
    rows = run_query(sql, (teacher_id,))
    subjects = []
    for r in rows:
        subjects.append({
            "subject_id": r[0],
            "subject_code": r[1],
            "name": r[2],
            "section": r[3],
            "teacher_id": r[4],
            "total_students": r[5],
            "total_classes": r[6],
        })
    return subjects


def get_student_subjects(student_id):
    """Fetch all subjects a student is enrolled in."""
    sql = """
        SELECT s.subject_id, s.subject_code, s.name, s.section, s.teacher_id
        FROM subject_students ss
        JOIN subjects s ON ss.subject_id = s.subject_id
        WHERE ss.student_id = %s
        ORDER BY s.name ASC
    """
    rows = run_query(sql, (student_id,))
    subjects = []
    for r in rows:
        subjects.append({
            "subject_id": r[0],
            "subject_code": r[1],
            "name": r[2],
            "section": r[3],
            "teacher_id": r[4],
        })
    return subjects


def enroll_student_to_subject(student_id, subject_id):
    """Enroll a student into a subject if not already enrolled."""
    existing = run_query(
        "SELECT 1 FROM subject_students WHERE student_id = %s AND subject_id = %s",
        (student_id, subject_id),
    )
    if not existing:
        run_execute(
            "INSERT INTO subject_students (subject_id, student_id) VALUES (%s, %s)",
            (subject_id, student_id),
        )
    return True


def unenroll_student_to_subject(student_id, subject_id):
    """Remove student from a subject."""
    run_execute(
        "DELETE FROM subject_students WHERE student_id = %s AND subject_id = %s",
        (student_id, subject_id),
    )
    return True


def get_enrolled_students(subject_id):
    """Fetch all students enrolled in a subject with their biometric embeddings."""
    sql = """
        SELECT s.student_id, s.name, s.face_embedding, s.voice_embedding
        FROM subject_students ss
        JOIN students s ON ss.student_id = s.student_id
        WHERE ss.subject_id = %s
        ORDER BY s.name ASC
    """
    rows = run_query(sql, (subject_id,))
    students = []
    for r in rows:
        face_emb = r[2]
        if isinstance(face_emb, str):
            try:
                face_emb = json.loads(face_emb)
            except Exception:
                pass
        voice_emb = r[3]
        if isinstance(voice_emb, str):
            try:
                voice_emb = json.loads(voice_emb)
            except Exception:
                pass
        students.append({
            "student_id": r[0],
            "name": r[1],
            "face_embedding": face_emb,
            "voice_embedding": voice_emb,
        })
    return students
