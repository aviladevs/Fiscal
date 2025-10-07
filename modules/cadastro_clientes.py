import streamlit as st
import pandas as pd
from modules import database
from modules.cnpj_consulta import consultar_cnpj, validar_cnpj, formatar_cnpj

def render():
    st.title("👥 Cadastro de Clientes")

    conn = database.get_connection()
    cur = conn.cursor()

    # CSS para autocomplete
    st.markdown("""
    <style>
    .stTextInput > div > div > input {
        background-color: white;
    }
    .autocomplete-suggestions {
        border: 1px solid #ccc;
        max-height: 200px;
        overflow-y: auto;
        background: white;
        z-index: 1000;
    }
    .autocomplete-suggestion {
        padding: 8px 12px;
        cursor: pointer;
        border-bottom: 1px solid #eee;
    }
    .autocomplete-suggestion:hover {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("📝 Novo Cliente")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Campo CNPJ com consulta automática
        cnpj_input = st.text_input("CNPJ", placeholder="Digite o CNPJ para consulta automática")
        
        # Validação e consulta automática do CNPJ
        if cnpj_input and len(cnpj_input.replace(".", "").replace("/", "").replace("-", "")) >= 14:
            if validar_cnpj(cnpj_input):
                cnpj_formatado = formatar_cnpj(cnpj_input)
                
                # Consulta automática
                with st.spinner("🔍 Consultando dados na Receita Federal..."):
                    dados_cnpj = consultar_cnpj(cnpj_input)
                
                if dados_cnpj:
                    st.success(f"✅ CNPJ válido! Dados encontrados:")
                    
                    # Preenche automaticamente os campos
                    if 'dados_empresa' not in st.session_state:
                        st.session_state.dados_empresa = dados_cnpj
                else:
                    st.warning("⚠️ CNPJ válido, mas dados não encontrados na Receita Federal")
            else:
                st.error("❌ CNPJ inválido!")
    
    with col2:
        if cnpj_input and 'dados_empresa' in st.session_state:
            st.info(f"**Situação:** {st.session_state.dados_empresa.get('situacao', 'N/A')}")
            st.info(f"**Porte:** {st.session_state.dados_empresa.get('porte', 'N/A')}")

    # Formulário principal
    with st.form("novo_cliente", clear_on_submit=True):
        cnpj = st.text_input("CNPJ Confirmado", 
                            value=formatar_cnpj(cnpj_input) if cnpj_input and validar_cnpj(cnpj_input) else "",
                            disabled=True)
        
        nome_value = ""
        endereco_value = ""
        telefone_value = ""
        email_value = ""
        
        if 'dados_empresa' in st.session_state:
            dados = st.session_state.dados_empresa
            nome_value = dados.get('nome', '')
            endereco_value = dados.get('endereco', '')
            telefone_value = dados.get('telefone', '')
            email_value = dados.get('email', '')
        
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            nome = st.text_input("Nome / Razão Social", value=nome_value)
            telefone = st.text_input("Telefone", value=telefone_value)
        
        with col_form2:
            email = st.text_input("Email", value=email_value)
            endereco = st.text_area("Endereço Completo", value=endereco_value, height=100)
        
        submit = st.form_submit_button("💾 Salvar Cliente", type="primary")

        if submit:
            if cnpj and nome:
                try:
                    cur.execute("""
                        INSERT OR REPLACE INTO clientes 
                        (cnpj, nome, endereco, telefone, email) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (cnpj, nome, endereco, telefone, email))
                    conn.commit()
                    st.success("✅ Cliente cadastrado com sucesso!")
                    
                    # Limpa os dados da sessão
                    if 'dados_empresa' in st.session_state:
                        del st.session_state.dados_empresa
                        
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {e}")
            else:
                st.error("❌ Por favor, preencha pelo menos CNPJ e Nome!")

    st.markdown("---")
    st.subheader("� Clientes Cadastrados")
    
    # Autocomplete para pesquisa
    col_search1, col_search2 = st.columns([2, 1])
    
    with col_search1:
        termo = st.text_input("🔍 Buscar por nome, CNPJ, telefone ou email")
    
    with col_search2:
        filtro_tipo = st.selectbox("Filtrar por:", ["Todos", "Nome", "CNPJ", "Telefone", "Email"])
    
    # Query de busca com autocomplete
    if termo:
        if filtro_tipo == "Todos":
            query = """
                SELECT cnpj, nome, endereco, telefone, email 
                FROM clientes 
                WHERE nome LIKE ? OR cnpj LIKE ? OR telefone LIKE ? OR email LIKE ?
                ORDER BY nome
            """
            params = (f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%")
        else:
            campo_map = {
                "Nome": "nome",
                "CNPJ": "cnpj", 
                "Telefone": "telefone",
                "Email": "email"
            }
            campo = campo_map[filtro_tipo]
            query = f"SELECT cnpj, nome, endereco, telefone, email FROM clientes WHERE {campo} LIKE ? ORDER BY nome"
            params = (f"%{termo}%",)
        
        df = pd.read_sql_query(query, conn, params=params)
        
        if not df.empty:
            # Formatação da tabela
            df.columns = ['CNPJ', 'Nome/Razão Social', 'Endereço', 'Telefone', 'Email']
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            st.success(f"✅ {len(df)} cliente(s) encontrado(s)")
        else:
            st.info(f"📝 Nenhum cliente encontrado para '{termo}'")
    else:
        # Lista todos os clientes se não há termo de busca
        df_todos = pd.read_sql_query(
            "SELECT cnpj, nome, endereco, telefone, email FROM clientes ORDER BY nome", 
            conn
        )
        
        if not df_todos.empty:
            df_todos.columns = ['CNPJ', 'Nome/Razão Social', 'Endereço', 'Telefone', 'Email']
            
            st.dataframe(
                df_todos,
                use_container_width=True,
                hide_index=True
            )
            
            st.info(f"📊 Total de clientes cadastrados: {len(df_todos)}")
        else:
            st.info("📝 Nenhum cliente cadastrado ainda.")

    conn.close()
