from src.database.config import run_query, run_execute
from src.database.security import hash_password, check_password


def check_teacher_exists(username):
    """Check if a username already exists in the teachers table."""
    rows = run_query("SELECT teacher_id FROM teachers WHERE username = %s", (username,))
    return len(rows) > 0


def create_teacher(username, name, password):
    """Hash password with bcrypt and insert a new teacher."""
    hashed_password = hash_password(password)
    run_execute(
        "INSERT INTO teachers (username, name, password) VALUES (%s, %s, %s)",
        (username, name, hashed_password),
    )
    # Return the created teacher record
    rows = run_query(
        "SELECT teacher_id, username, name FROM teachers WHERE username = %s",
        (username,),
    )
    if rows:
        return {
            "teacher_id": rows[0][0],
            "username": rows[0][1],
            "name": rows[0][2],
        }
    return None


def login_teacher(username, password):
    """Verify username and password; returns teacher dict if valid, else None."""
    rows = run_query(
        "SELECT teacher_id, username, password, name FROM teachers WHERE username = %s",
        (username,),
    )
    if not rows:
        return None

    teacher_id, db_username, stored_hash, name = rows[0]

    # Verify password against bcrypt hash
    if check_password(password, stored_hash):
        return {
            "teacher_id": teacher_id,
            "username": db_username,
            "name": name,
        }
    return None
