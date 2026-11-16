from src.database.config import run_query, run_execute


def create_attendance(logs):
    """Insert a batch of attendance logs for students in a class session."""
    if not logs:
        return False

    for item in logs:
        subject_id = item.get("subject_id")
        student_id = item.get("student_id")
        is_present = bool(item.get("is_present", False))
        run_execute(
            "INSERT INTO attendance_logs (timestamp, subject_id, student_id, is_present) VALUES (NOW(), %s, %s, %s)",
            (subject_id, student_id, is_present),
        )
    return True


def get_student_attendance(student_id):
    """Fetch attendance records for a specific student across all enrolled subjects."""
    sql = """
        SELECT al.id, al.subject_id, s.name AS subject_name, s.subject_code, al.is_present, al.timestamp
        FROM attendance_logs al
        JOIN subjects s ON al.subject_id = s.subject_id
        WHERE al.student_id = %s
        ORDER BY al.timestamp DESC
    """
    rows = run_query(sql, (student_id,))
    records = []
    for r in rows:
        ts = r[5]
        records.append({
            "id": r[0],
            "subject_id": r[1],
            "subject_name": r[2],
            "subject_code": r[3],
            "is_present": r[4],
            "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts) if ts else None,
        })
    return records


def get_attendance_for_teacher(teacher_id):
    """Fetch all attendance records for subjects owned by a teacher (used for reports)."""
    sql = """
        SELECT 
            al.id, 
            al.timestamp, 
            al.is_present, 
            al.student_id,
            s.subject_id, 
            s.name AS subject_name, 
            s.subject_code
        FROM attendance_logs al
        JOIN subjects s ON al.subject_id = s.subject_id
        WHERE s.teacher_id = %s
        ORDER BY al.timestamp DESC
    """
    rows = run_query(sql, (teacher_id,))
    records = []
    for r in rows:
        ts = r[1]
        records.append({
            "id": r[0],
            "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts) if ts else None,
            "is_present": r[2],
            "student_id": r[3],
            "subject_id": r[4],
            "subject_name": r[5],
            "subject_code": r[6],
        })
    return records
