import streamlit as st
import time
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import style_background_dashboard
from src.controllers.teacher_controller import handle_teacher_register

style_background_dashboard()

c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
with c1:
    header_dashboard()
with c2:
    if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
        st.switch_page("src/screens/home_screen.py")

st.header('Register your teacher profile')

st.space()
st.space()

teacher_username = st.text_input("Enter username", placeholder='ananyaroy')
teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')
teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")
teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

st.divider()

btnc1, btnc2 = st.columns(2)

with btnc1:
    if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
        success, message = handle_teacher_register(
            teacher_username, teacher_name, teacher_pass, teacher_pass_confirm
        )
        if success:
            st.success(message)
            time.sleep(2)
            st.switch_page("src/screens/teacher/teacher_login.py")
        else:
            st.error(message)

with btnc2:
    if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
        st.switch_page("src/screens/teacher/teacher_login.py")

footer_dashboard()
