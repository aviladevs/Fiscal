import streamlit as st
from modules import xml_reader, cadastro_clientes, mercadorias, sefaz_integration, database

st.set_page_config(page_title="Leitor NF-e & CT-e", page_icon="📦", layout="wide")

database.init_db()

menu = st.sidebar.radio("📋 Menu", ["Leitor XML", "Cadastro de Clientes", "Mercadorias", "Integração SEFAZ"])

if menu == "Leitor XML":
    xml_reader.render()

elif menu == "Cadastro de Clientes":
    cadastro_clientes.render()

elif menu == "Mercadorias":
    mercadorias.render()

elif menu == "Integração SEFAZ":
    sefaz_integration.render()

st.sidebar.markdown("---")
st.sidebar.caption("🧠 Sistema desenvolvido em Python + Streamlit")
