import streamlit as st
import time
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import style_background_dashboard
from src.controllers.teacher_controller import handle_teacher_login

style_background_dashboard()

c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
with c1:
    header_dashboard()
with c2:
    if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
        st.switch_page("src/screens/home_screen.py")

st.header('Login using password', text_alignment='center')
st.space()
st.space()

teacher_username = st.text_input("Enter username", placeholder='ananyaroy')
teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

st.divider()

btnc1, btnc2 = st.columns(2)

with btnc1:
    if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
        success, message = handle_teacher_login(teacher_username, teacher_pass)
        if success:
            st.toast(message, icon="👋")
            time.sleep(1)
            st.switch_page("src/screens/teacher/teacher_dashboard.py")
        else:
            st.error(message)

with btnc2:
    if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
        st.switch_page("src/screens/teacher/teacher_register.py")

footer_dashboard()
