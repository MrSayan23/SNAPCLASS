import json
from src.database.config import run_query, run_execute


def get_all_students():
    """Fetch all students with face and voice embeddings (used by face_pipeline)."""
    rows = run_query(
        "SELECT student_id, name, face_embedding, voice_embedding FROM students ORDER BY student_id ASC"
    )
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


def create_student(name, face_embedding=None, voice_embedding=None):
    """Insert a new student with face and voice embeddings."""
    face_json = json.dumps(face_embedding) if face_embedding is not None else None
    voice_json = json.dumps(voice_embedding) if voice_embedding is not None else None

    run_execute(
        "INSERT INTO students (name, face_embedding, voice_embedding) VALUES (%s, %s, %s)",
        (name, face_json, voice_json),
    )

    # Return the newly created student record
    rows = run_query(
        "SELECT student_id, name, face_embedding, voice_embedding FROM students WHERE name = %s ORDER BY student_id DESC LIMIT 1",
        (name,),
    )
    if rows:
        return {
            "student_id": rows[0][0],
            "name": rows[0][1],
            "face_embedding": rows[0][2],
            "voice_embedding": rows[0][3],
        }
    return None
