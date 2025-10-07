import streamlit as st
from modules import xml_reader, clientes, mercadorias, database

database.criar_tabelas()
st.set_page_config(page_title="Leitor de XML - NF/CT-e", layout="wide")

st.title("📄 Leitor de XML de NF-e e CT-e")

aba = st.sidebar.radio("Menu", ["📤 Importar XML", "👥 Clientes", "📦 Mercadorias"])

if aba == "📤 Importar XML":
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

elif aba == "👥 Clientes":
    termo = st.text_input("Pesquisar cliente:")
    df = clientes.pesquisar_cliente(termo) if termo else clientes.listar_clientes()
    st.dataframe(df)

elif aba == "📦 Mercadorias":
    termo = st.text_input("Pesquisar mercadoria:")
    df = mercadorias.pesquisar_mercadoria(termo) if termo else mercadorias.listar_mercadorias()
    st.dataframe(df)
