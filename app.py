import streamlit as st
from src.ui.base_layout import style_base_layout

style_base_layout()

home = st.Page("src/screens/home_screen.py", title="Home", default=True)
student = st.Page("src/screens/student_screen.py", title="Student Portal", url_path="student-portal")
teacher_login = st.Page("src/screens/teacher/teacher_login.py", title="Teacher Login", url_path="teacher-login")
teacher_register = st.Page("src/screens/teacher/teacher_register.py", title="Teacher Register", url_path="teacher-register")
teacher_dashboard = st.Page("src/screens/teacher/teacher_dashboard.py", title="Teacher Dashboard", url_path="teacher-dashboard")

pg = st.navigation(
    [home, student, teacher_login, teacher_register, teacher_dashboard],
    position="hidden",
)
pg.run()
