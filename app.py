import streamlit as st
from tabs import show_explore_sidebar, show_tagging_tab
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Cargar la configuración de autenticación
with open('data/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Colocar el login en la sidebar
with st.sidebar:
    st.title("Login")
    authenticator.login()

if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout('Logout', 'main')
        st.write(f'Etiquetando: **{st.session_state["name"]}**')
    show_explore_sidebar()
    show_tagging_tab()
    
elif st.session_state["authentication_status"] is False:
    st.sidebar.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password')
