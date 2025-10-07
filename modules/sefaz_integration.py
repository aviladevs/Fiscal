import streamlit as st
import os
import time
import json
from datetime import datetime, timedelta
from modules.sefaz_connector import consultar_e_sincronizar_nfes
from modules import database

SYNC_FILE = "data/ultima_sincronizacao.json"
CERT_FILE = "data/certificados/certificado_a1.pfx"

# Recupera variáveis de ambiente
CERT_PASSWORD_ENV = os.environ.get("CERT_PASSWORD")
CNPJ = os.environ.get("CNPJ")

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

    # Cabeçalho
    st.markdown("<h2 style='font-weight:600; margin-bottom:0;'>🏛️ Integração SEFAZ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666; margin-top:0;'>Gerencie suas notas fiscais com conexão segura e automática.</p>", unsafe_allow_html=True)

    # Cartão principal
    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    # Upload certificado A1
    st.subheader("🔐 Certificado Digital A1")
    uploaded_cert = st.file_uploader("Selecione seu arquivo .pfx", type=["pfx"], key="upload_cert")
    
    # Prioriza senha do certificado via variável de ambiente
    senha = CERT_PASSWORD_ENV if CERT_PASSWORD_ENV else st.text_input("Senha do certificado", type="password", key="senha_cert")

    if uploaded_cert and senha:
        save_cert(uploaded_cert.getvalue())
        st.success("✅ Certificado armazenado com sucesso.")
        st.info("Mantenha seu certificado em local seguro.")

    # Sincronização com controle de 1 hora
    last_sync = get_last_sync()
    
    # Sempre usar ambiente de produção
    ambiente = "producao"
    st.info("🌐 **Ambiente:** Produção (dados reais da SEFAZ)")
    
    col_sync1, col_sync2 = st.columns([1, 1])
    
    with col_sync1:
        sync_button = st.button("🔄 Sincronizar com SEFAZ", type="primary", use_container_width=True)
    
    with col_sync2:
        if st.button("📊 Ver Notas Sincronizadas", use_container_width=True):
            st.session_state.show_notas = True
    
    if sync_button:
        if not os.path.exists(CERT_FILE):
            st.error("❌ Nenhum certificado encontrado. Faça o upload primeiro.")
        elif not last_sync or datetime.now() - last_sync >= timedelta(hours=1):
            if not senha:
                st.error("❌ Não foi possível obter a senha do certificado.")
            else:
                with st.spinner("🔍 Consultando SEFAZ... Isso pode levar alguns minutos."):
                    # Chama a integração real
                    resultado = consultar_e_sincronizar_nfes(CERT_FILE, senha, ambiente)
                    
                    if resultado.get("sucesso"):
                        set_last_sync()
                        
                        st.success("✅ Sincronização concluída com sucesso!")
                        
                        # Estatísticas
                        documentos = resultado.get("documentos", [])
                        total_docs = len(documentos)
                        processados = len([d for d in documentos if d.get("processado", False)])
                        
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("📄 Documentos Encontrados", total_docs)
                        with col_stat2:
                            st.metric("✅ Processados", processados)
                        with col_stat3:
                            st.metric("⚠️ Erros", total_docs - processados)
                        
                        # Detalhes dos documentos
                        if documentos:
                            st.subheader("📋 Documentos Sincronizados")
                            for i, doc in enumerate(documentos[:10]):  # Mostra apenas os primeiros 10
                                with st.expander(f"📄 {doc.get('tipo', 'N/A')} - NSU: {doc.get('nsu', 'N/A')}"):
                                    if doc.get("processado"):
                                        st.write(f"**Chave:** {doc.get('chave', 'N/A')}")
                                        st.write(f"**Emitente:** {doc.get('nome_emitente', 'N/A')}")
                                        st.write(f"**CNPJ:** {doc.get('cnpj_emitente', 'N/A')}")
                                        if doc.get('valor_total'):
                                            st.write(f"**Valor:** R$ {doc.get('valor_total', 0):.2f}")
                                    else:
                                        st.error(f"Erro: {doc.get('erro', 'Não especificado')}")
                                        
                            if len(documentos) > 10:
                                st.info(f"... e mais {len(documentos) - 10} documentos")
                        
                        # Informações da consulta
                        st.info(f"📊 Status SEFAZ: {resultado.get('codigo_status')} - {resultado.get('motivo')}")
                        st.info(f"🔢 Último NSU processado: {resultado.get('ultimo_nsu')}")
                        
                    else:
                        st.error(f"❌ Erro na sincronização: {resultado.get('erro', 'Erro desconhecido')}")
                        
                        # Debug information
                        if st.checkbox("🔧 Mostrar detalhes técnicos"):
                            st.text_area("XML de resposta:", resultado.get('xml_completo', 'N/A'), height=200)
        else:
            restante = timedelta(hours=1) - (datetime.now() - last_sync)
            minutos = int(restante.total_seconds() // 60)
            st.warning(f"⚠️ Você já sincronizou há menos de 1 hora. Tente novamente em {minutos} minutos.")
    
    # Mostrar notas sincronizadas
    if st.session_state.get('show_notas', False):
        st.markdown("---")
        st.subheader("📊 Notas Fiscais Sincronizadas")
        
        conn = database.get_connection()
        
        try:
            import pandas as pd
            df = pd.read_sql_query("""
                SELECT tipo, numero, cnpj_emitente, nome_emitente, valor_total, data_sincronizacao
                FROM notas 
                WHERE data_sincronizacao IS NOT NULL
                ORDER BY data_sincronizacao DESC
                LIMIT 50
            """, conn)
            
            if not df.empty:
                # Formatar valores
                df['valor_total'] = df['valor_total'].apply(lambda x: f"R$ {x:.2f}" if x > 0 else "N/A")
                df['data_sincronizacao'] = pd.to_datetime(df['data_sincronizacao']).dt.strftime('%d/%m/%Y %H:%M')
                
                df.columns = ['Tipo', 'Número/Chave', 'CNPJ Emitente', 'Nome Emitente', 'Valor Total', 'Data Sincronização']
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"📊 Total de {len(df)} notas sincronizadas")
                
                # Botão para limpar visualização
                if st.button("❌ Fechar lista"):
                    st.session_state.show_notas = False
                    st.rerun()
            else:
                st.info("📝 Nenhuma nota sincronizada ainda. Use o botão 'Sincronizar com SEFAZ' para buscar notas.")
                
        except Exception as e:
            st.error(f"Erro ao carregar notas: {e}")
        finally:
            conn.close()

    last_sync = get_last_sync()
    if last_sync:
        st.markdown(f"<div class='sync-time'>🕒 Última sincronização: <b>{last_sync.strftime('%d/%m/%Y %H:%M:%S')}</b></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='sync-time'>Nenhuma sincronização realizada ainda.</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#ddd; margin-top:2rem;'>", unsafe_allow_html=True)
    st.markdown("💡 **Dica:** mantenha seu certificado digital A1 atualizado para garantir a comunicação com a SEFAZ.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
