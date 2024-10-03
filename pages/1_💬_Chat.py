import streamlit as st
from source.generate.streamlit_chat import display_conversation
from ui.sidebar import show_sidebar 

def main():
    show_sidebar()
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        username = st.session_state.username
        user_info = st.session_state.user_info
        container = st.container()
        display_conversation(user_name=username, container=container)

if __name__ == "__main__":
    main()