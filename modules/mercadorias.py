import streamlit as st
import pandas as pd
from modules import database

def render():
    st.title("📦 Cadastro de Mercadorias")

    conn = database.get_connection()
    cur = conn.cursor()

    with st.form("nova_mercadoria"):
        codigo = st.text_input("Código Interno")
        descricao = st.text_input("Descrição")
        ncm = st.text_input("NCM")
        unidade = st.text_input("Unidade (ex: UN, KG, CX)")
        valor_unit = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")
        submit = st.form_submit_button("Salvar Mercadoria")

        if submit:
            cur.execute(
                "INSERT OR IGNORE INTO mercadorias (codigo, descricao, ncm, unidade, valor_unit) VALUES (?, ?, ?, ?, ?)",
                (codigo, descricao, ncm, unidade, valor_unit)
            )
            conn.commit()
            st.success("Mercadoria cadastrada com sucesso!")

    st.subheader("🔍 Pesquisar Mercadorias")
    termo = st.text_input("Buscar por descrição ou código")
    if termo:
        query = "SELECT * FROM mercadorias WHERE descricao LIKE ? OR codigo LIKE ?"
        df = pd.read_sql_query(query, conn, params=(f"%{termo}%", f"%{termo}%"))
        st.dataframe(df)
    else:
        st.subheader("📋 Todas as Mercadorias")
        df = pd.read_sql_query("SELECT * FROM mercadorias", conn)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("Nenhuma mercadoria cadastrada ainda.")

    conn.close()
