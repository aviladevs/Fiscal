import streamlit as st
import os
import time
import json
from datetime import datetime, timedelta

SYNC_FILE = "data/ultima_sincronizacao.json"
CERT_FILE = "data/certificados/certificado_a1.pfx"

def get_last_sync():
    if os.path.exists(SYNC_FILE):
        with open(SYNC_FILE, "r") as f:
            data = json.load(f)
        return datetime.fromisoformat(data.get("ultima_execucao"))
    return None

def set_last_sync():
    os.makedirs("data", exist_ok=True)
    with open(SYNC_FILE, "w") as f:
        json.dump({"ultima_execucao": datetime.now().isoformat()}, f)

def save_cert(cert_bytes):
    os.makedirs("data/certificados", exist_ok=True)
    with open(CERT_FILE, "wb") as f:
        f.write(cert_bytes)

def render():
    # Estilo global
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, rgba(250,250,255,1) 0%, rgba(240,242,255,1) 100%);
            color: #111111;
        }
        .glass {
            background: rgba(255, 255, 255, 0.65);
            border-radius: 20px;
            padding: 1.8rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            backdrop-filter: blur(12px);
            margin-bottom: 1rem;
        }
        .refresh-button {
            font-size: 24px !important;
            padding: 0.4rem 0.9rem !important;
            border-radius: 100px !important;
            border: none !important;
            background-color: #007AFF !important;
            color: white !important;
            transition: 0.3s;
        }
        .refresh-button:hover {
            background-color: #005BEA !important;
            transform: scale(1.1);
        }
        .sync-time {
            color: #666;
            font-size: 14px;
            margin-top: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Cabeçalho com botão à direita
    col1, col2 = st.columns([8, 1])
    with col1:
        st.markdown("<h2 style='font-weight:600; margin-bottom:0;'>🏛️ Integração SEFAZ</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666; margin-top:0;'>Gerencie suas notas fiscais com conexão segura e automática.</p>", unsafe_allow_html=True)
    with col2:
        btn_html = """
        <button class="refresh-button" title="Atualizar SEFAZ" id="refresh-btn">🔄</button>
        <script>
        const btn = document.getElementById("refresh-btn");
        btn.onclick = function() {
            window.location.href = window.location.href + "?sync=1";
        }
        </script>
        """
        st.markdown(btn_html, unsafe_allow_html=True)

    # Cartão principal
    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    # Upload certificado A1
    st.subheader("🔐 Certificado Digital A1")
    uploaded_cert = st.file_uploader("Selecione seu arquivo .pfx", type=["pfx"], key="upload_cert")
    senha = st.text_input("Senha do certificado", type="password", key="senha_cert")
    if uploaded_cert and senha:
        save_cert(uploaded_cert.getvalue())
        st.success("✅ Certificado armazenado com sucesso.")
        st.info("Mantenha seu certificado em local seguro.")

    # Sincronização com controle de 1 hora
    last_sync = get_last_sync()
    if "sync=1" in st.query_params:
        if not os.path.exists(CERT_FILE):
            st.error("❌ Nenhum certificado encontrado. Faça o upload primeiro.")
        elif not last_sync or datetime.now() - last_sync >= timedelta(hours=1):
            set_last_sync()
            st.success("✅ Sincronização iniciada com sucesso!")
            time.sleep(0.5)
            st.info("Conectando à SEFAZ e puxando notas...")
            # Simulação de integração
            time.sleep(2)
            st.success("✅ Notas atualizadas com sucesso!")
        else:
            restante = timedelta(hours=1) - (datetime.now() - last_sync)
            minutos = int(restante.total_seconds() // 60)
            st.warning(f"⚠️ Você já sincronizou há menos de 1 hora. Tente novamente em {minutos} minutos.")

    last_sync = get_last_sync()
    if last_sync:
        st.markdown(f"<div class='sync-time'>🕒 Última sincronização: <b>{last_sync.strftime('%d/%m/%Y %H:%M:%S')}</b></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='sync-time'>Nenhuma sincronização realizada ainda.</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#ddd; margin-top:2rem;'>", unsafe_allow_html=True)
    st.markdown("💡 **Dica:** mantenha seu certificado digital A1 atualizado para garantir a comunicação com a SEFAZ.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)