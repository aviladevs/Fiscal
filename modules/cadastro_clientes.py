import streamlit as st
import pandas as pd
from modules import database

def render():
    st.title("👥 Cadastro de Clientes")

    conn = database.get_connection()
    cur = conn.cursor()

    with st.form("novo_cliente"):
        cnpj = st.text_input("CNPJ")
        nome = st.text_input("Nome / Razão Social")
        endereco = st.text_input("Endereço")
        submit = st.form_submit_button("Salvar Cliente")

        if submit:
            cur.execute("INSERT OR IGNORE INTO clientes (cnpj, nome, endereco) VALUES (?, ?, ?)", (cnpj, nome, endereco))
            conn.commit()
            st.success("Cliente cadastrado com sucesso!")

    st.subheader("🔍 Pesquisar Clientes")
    termo = st.text_input("Buscar por nome ou CNPJ")
    if termo:
        query = f"SELECT * FROM clientes WHERE nome LIKE ? OR cnpj LIKE ?"
        df = pd.read_sql_query(query, conn, params=(f"%{termo}%", f"%{termo}%"))
        st.dataframe(df)

    conn.close()
