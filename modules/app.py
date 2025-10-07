# app.py
import streamlit as st
from modules import database, xml_reader, clientes, mercadorias, sefaz_connector

database.criar_tabelas()
st.set_page_config(page_title="Leitor de XML - NF/CT-e", layout="wide")

st.title("📄 Leitor de XML de NF-e e CT-e")

menu = st.sidebar.radio("Menu", ["📤 Importar XML", "👥 Clientes", "📦 Mercadorias", "⚙️ Administração"])

# ==================================================
# 📤 Importação de XML
# ==================================================
if menu == "📤 Importar XML":
    xml_file = st.file_uploader("Envie um arquivo XML", type=["xml"])
    if xml_file:
        conteudo = xml_file.read()
        dados = xml_reader.ler_xml(conteudo)
        if dados:
            st.success(f"Arquivo {dados['tipo']} lido com sucesso!")

            clientes.adicionar_cliente(dados["emitente"], dados["cnpj_emitente"])
            clientes.adicionar_cliente(dados["destinatario"], dados["cnpj_dest"])

            if "itens" in dados:
                for item in dados["itens"]:
                    mercadorias.adicionar_mercadoria(
                        item["descricao"], item["codigo"], item["valor_unit"]
                    )

            st.write("### Emitente:", dados["emitente"])
            st.write("### Destinatário:", dados["destinatario"])
            st.write("### Itens:", dados.get("itens", []))
        else:
            st.error("Arquivo XML inválido ou não reconhecido.")

# ==================================================
# 👥 Clientes
# ==================================================
elif menu == "👥 Clientes":
    termo = st.text_input("Pesquisar cliente:")
    df = clientes.pesquisar_cliente(termo) if termo else clientes.listar_clientes()
    st.dataframe(df)

# ==================================================
# 📦 Mercadorias
# ==================================================
elif menu == "📦 Mercadorias":
    termo = st.text_input("Pesquisar mercadoria:")
    df = mercadorias.pesquisar_mercadoria(termo) if termo else mercadorias.listar_mercadorias()
    st.dataframe(df)

# ==================================================
# ⚙️ Administração - Certificado Digital e SEFAZ
# ==================================================
elif menu == "⚙️ Administração":
    st.subheader("⚙️ Administração - Integração com SEFAZ")

    cert_file = st.file_uploader("Certificado Digital (.pfx)", type=["pfx"])
    senha = st.text_input("Senha do Certificado", type="password")
    cnpj = st.text_input("CNPJ vinculado", placeholder="Somente números")

    if cert_file and senha and cnpj:
        cert_path = sefaz_connector.carregar_certificado(cert_file.getvalue(), senha)
        st.success("Certificado carregado com sucesso.")

        if st.button("🔍 Consultar Notas na SEFAZ"):
            with st.spinner("Consultando SEFAZ..."):
                resultado = sefaz_connector.consultar_notas(cert_path, cnpj)
            st.code(resultado[:3000], language="xml")  # mostra parte do XML retornado
