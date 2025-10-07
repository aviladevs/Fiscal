import streamlit as st
import xmltodict
import pandas as pd
import os
from modules import database

def render():
    st.title("📂 Leitor de XML - NF-e & CT-e")

    uploaded_file = st.file_uploader("Selecione o arquivo XML", type=["xml"])

    if uploaded_file:
        os.makedirs("data/xmls", exist_ok=True)
        xml_path = os.path.join("data/xmls", uploaded_file.name)
        with open(xml_path, "wb") as f:
            f.write(uploaded_file.read())

        with open(xml_path, "r", encoding="utf-8") as f:
            xml_content = xmltodict.parse(f.read())

        if "nfeProc" in xml_content:
            st.success("Arquivo identificado como NF-e ✅")
            parse_nfe(xml_content)
        elif "cteProc" in xml_content:
            st.success("Arquivo identificado como CT-e ✅")
            parse_cte(xml_content)
        else:
            st.error("Não foi possível identificar o tipo de XML.")

def parse_nfe(xml_content):
    nfe = xml_content["nfeProc"]["NFe"]["infNFe"]
    emit = nfe["emit"]
    total = nfe["total"]["ICMSTot"]

    cnpj = emit.get("CNPJ", "N/A")
    nome = emit.get("xNome", "N/A")
    valor_total = float(total.get("vNF", 0))

    st.subheader("🧾 Dados da NF-e")
    st.write(f"**Emitente:** {nome}")
    st.write(f"**CNPJ:** {cnpj}")
    st.write(f"**Valor Total:** R$ {valor_total:.2f}")

    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO notas (tipo, numero, cnpj_emitente, nome_emitente, valor_total) VALUES (?, ?, ?, ?, ?)",
                ("NFe", nfe["@Id"], cnpj, nome, valor_total))
    conn.commit()
    conn.close()

def parse_cte(xml_content):
    cte = xml_content["cteProc"]["CTe"]["infCte"]
    emit = cte["emit"]
    vPrest = cte["vPrest"]

    cnpj = emit.get("CNPJ", "N/A")
    nome = emit.get("xNome", "N/A")
    valor_total = float(vPrest.get("vTPrest", 0))

    st.subheader("🚚 Dados do CT-e")
    st.write(f"**Emitente:** {nome}")
    st.write(f"**CNPJ:** {cnpj}")
    st.write(f"**Valor Total:** R$ {valor_total:.2f}")

    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO notas (tipo, numero, cnpj_emitente, nome_emitente, valor_total) VALUES (?, ?, ?, ?, ?)",
                ("CTe", cte["@Id"], cnpj, nome, valor_total))
    conn.commit()
    conn.close()