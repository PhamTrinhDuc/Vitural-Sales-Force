import streamlit as st
from configs import SYSTEM_CONFIG


def show_sidebar():
    st.sidebar.image(SYSTEM_CONFIG.LOGO_DIRECTORY, use_column_width=True)
    st.markdown("### 🧠 Ứng dụng AI chăm sóc tư vấn khách hàng")
    st.sidebar.markdown('Hướng dẫn sử dụng:')
    st.sidebar.markdown('1. 🟢 **Đăng nhập tài khoản.**')
    st.sidebar.markdown('2. 💬 **Sử dụng chức năng chat - "Nói chuyện với chuyên gia tư vấn Bot VCC"**')
    st.sidebar.markdown('3. 📝 **Product by Duc and Hao VCC**')