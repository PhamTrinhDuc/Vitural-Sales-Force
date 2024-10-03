import streamlit as st
from ui.authenticate import register, login
from ui.sidebar import show_sidebar
from configs import SYSTEM_CONFIG

def main():
    show_sidebar()

    if "logged_in" not in st.session_state:
        with st.expander(label="ARMY SALES CHATBOT", expanded=True):
            login_tab, create_tab = st.tabs(
                [
                    "Đăng nhập",
                    "Tạo tài khoản",
                ]
            )

            with login_tab:
                login()
            with create_tab:
                register()
    else:
        col = st.columns(1)
        with col[0]:
            st.image(SYSTEM_CONFIG.LOGO_DIRECTORY, use_column_width=True)
            if st.button("Hỏi đáp với chatbot"):
                st.switch_page("pages/1_💬_Chat.py", )
            
        st.success("Chatbot đã sẵn sàng để trò chuyện với bạn !!")


if __name__ == "__main__":
    main()