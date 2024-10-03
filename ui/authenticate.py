import os
import streamlit as st
from typing import List, Dict
import hashlib
from configs import SYSTEM_CONFIG
from utils.user_helper import UserHelper

# ma hoa mat khau
def hash_password(password: str) -> str:
    """
    Hàm để mã hóa mật khẩu
    """
    return hashlib.sha256(password.encode()).hexdigest()

# kiem tra mat khau
def verify_password(provided_password: str, hashed_password: str) -> bool:
    """
    Hàm để kiểm tra mật khẩu đã mã hóa có khớp với mật khẩu chưa mã hóa
    """
    return hash_password(provided_password) == hashed_password

# tao giao dien dang ky
def register():
    with st.form(key="register"):
        st.subheader("Register")
        username = st.text_input("Tên tài khoản")
        email = st.text_input("Email")
        name = st.text_input("Họ tên")
        password = st.text_input("Mật khẩu", type="password")
        confirm_password = st.text_input("Xác nhận mật khẩu", type="password")

        if st.form_submit_button("Đăng ký"):
            users = UserHelper().load_user_data(user_name=username)
            if len(os.listdir(SYSTEM_CONFIG.INFO_USER_DIRECTORY)) >= 5:
                st.error("Số lượng người dùng đạt mức giới hạn đăng kí!!")
            elif not username or not password:
                st.error("Tên tài khoản và mật khẩu không được để trống")
            elif password == confirm_password:
                if username in users['username']:
                    st.error("Tên tài khoản đã tồn tại")
                else:
                    hashed_password = hash_password(password)
                    users['username'][username] = {
                        'email': email,
                        'name': name,
                        'password': hashed_password
                    }
                    UserHelper().save_users(user_name=username, users=users)

                    st.session_state.username = username
                    st.session_state.logged_in = True
                    st.session_state.user_info = f"username: {username} "
                    for key, val in users["username"][username].items():
                        st.session_state.user_info += f"{key}: {val} "
                    st.rerun()

# Tạo giao diện đăng nhập
def login():
    with st.form(key="login"):
        username = st.text_input("Tên tài khoản")
        password = st.text_input("Mật khẩu", type="password")

        if st.form_submit_button("Đăng nhập"):
            users = UserHelper().load_user_data(user_name=username)
            if username in users['username']:
                stored_password = users['username'][username]['password']
                if verify_password(password, stored_password):
                    st.session_state.username = username
                    st.session_state.logged_in = True
                    st.session_state.user_info = f"username: {username} "
                    for key, val in users["username"][username].items():
                        st.session_state.user_info += f"{key}: {val} "
                    st.rerun()
                else:
                    st.error("Sai mật khẩu")
            else:
                st.error("Tài khoản không tồn tại")

if __name__ == "__main__":

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        with st.expander('AIO MENTAL HEALTH', expanded=True):
            login_tab, create_tab = st.tabs(
                [
                    "Đăng nhập",
                    "Tạo tài khoản",
                ]
            )
            with create_tab:
                register()
            with login_tab:
                login()
    else:
        st.write(f"Welcome, {st.session_state.username}!")