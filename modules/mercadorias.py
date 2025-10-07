import streamlit as st
import pandas as pd
from modules.database import conectar

def adicionar_mercadoria(descricao, codigo, valor_unit, ncm="", unidade="UN"):
    conn = conectar()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO mercadorias (descricao, codigo, valor_unit, ncm, unidade) VALUES (?, ?, ?, ?, ?)",
        (descricao, codigo, valor_unit, ncm, unidade)
    )
    conn.commit()
    conn.close()

def listar_mercadorias():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM mercadorias", conn)
    conn.close()
    return df

def pesquisar_mercadoria(termo):
    conn = conectar()
    df = pd.read_sql_query(
        "SELECT * FROM mercadorias WHERE descricao LIKE ? OR codigo LIKE ? OR ncm LIKE ? ORDER BY descricao",
        conn,
        params=(f"%{termo}%", f"%{termo}%", f"%{termo}%")
    )
    conn.close()
    return df

def render():
    st.title("📦 Gestão de Mercadorias")
    
    # CSS para melhorar a interface
    st.markdown("""
    <style>
    .stTextInput > div > div > input {
        background-color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Cadastrar", "📋 Listar", "🔍 Pesquisar"])
    
    with tab1:
        st.subheader("📝 Cadastrar Nova Mercadoria")
        
        with st.form("nova_mercadoria", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                descricao = st.text_input("📄 Descrição da Mercadoria", placeholder="Ex: Notebook Dell Inspiron")
                codigo = st.text_input("🏷️ Código da Mercadoria", placeholder="Ex: PROD001")
                ncm = st.text_input("📊 NCM (Opcional)", placeholder="Ex: 8471.30.12")
            
            with col2:
                valor_unit = st.number_input("💰 Valor Unitário (R$)", min_value=0.0, step=0.01, format="%.2f")
                unidade = st.selectbox("📏 Unidade", ["UN", "KG", "M", "M²", "M³", "L", "PC", "CX", "PT"])
            
            col_form1, col_form2, col_form3 = st.columns([1, 1, 2])
            
            with col_form2:
                submit = st.form_submit_button("💾 Cadastrar Mercadoria", type="primary", use_container_width=True)
            
            if submit:
                if descricao and codigo:
                    try:
                        conn = conectar()
                        c = conn.cursor()
                        c.execute("""
                            INSERT OR REPLACE INTO mercadorias 
                            (descricao, codigo, valor_unit, ncm, unidade) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (descricao, codigo, valor_unit, ncm, unidade))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Mercadoria '{descricao}' cadastrada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao cadastrar: {e}")
                else:
                    st.error("❌ Por favor, preencha pelo menos Descrição e Código!")
    
    with tab2:
        st.subheader("📋 Lista de Mercadorias Cadastradas")
        
        df = listar_mercadorias()
        
        if not df.empty:
            # Estatísticas rápidas
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("📦 Total de Mercadorias", len(df))
            
            with col_stats2:
                valor_medio = df['valor_unit'].mean()
                st.metric("💰 Valor Médio", f"R$ {valor_medio:.2f}")
            
            with col_stats3:
                valor_total = df['valor_unit'].sum()
                st.metric("💸 Valor Total Estoque", f"R$ {valor_total:.2f}")
            
            # Formatando a tabela
            df_display = df.copy()
            df_display['valor_unit'] = df_display['valor_unit'].apply(lambda x: f"R$ {x:.2f}")
            df_display.columns = ['ID', 'Descrição', 'Código', 'NCM', 'Unidade', 'Valor Unitário']
            
            # Filtros
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                filtro_unidade = st.selectbox("Filtrar por Unidade:", ["Todas"] + list(df['unidade'].unique()))
            
            with col_filter2:
                ordenar_por = st.selectbox("Ordenar por:", ["Descrição", "Código", "Valor", "NCM"])
            
            # Aplicar filtros
            df_filtrado = df_display.copy()
            if filtro_unidade != "Todas":
                df_filtrado = df_filtrado[df_filtrado['Unidade'] == filtro_unidade]
            
            # Aplicar ordenação
            if ordenar_por == "Valor":
                df_original_filtrado = df[df['unidade'] == filtro_unidade] if filtro_unidade != "Todas" else df
                df_original_filtrado = df_original_filtrado.sort_values('valor_unit', ascending=False)
                df_filtrado = df_original_filtrado.copy()
                df_filtrado['valor_unit'] = df_filtrado['valor_unit'].apply(lambda x: f"R$ {x:.2f}")
                df_filtrado.columns = ['ID', 'Descrição', 'Código', 'NCM', 'Unidade', 'Valor Unitário']
            else:
                campo_ordenacao = {"Descrição": "Descrição", "Código": "Código", "NCM": "NCM"}[ordenar_por]
                df_filtrado = df_filtrado.sort_values(campo_ordenacao)
            
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.info("📦 Nenhuma mercadoria cadastrada ainda.")
            st.markdown("👆 Use a aba **Cadastrar** para adicionar sua primeira mercadoria!")
    
    with tab3:
        st.subheader("🔍 Pesquisar Mercadorias")
        
        # Opções de pesquisa avançada
        col_search1, col_search2 = st.columns([2, 1])
        
        with col_search1:
            termo_pesquisa = st.text_input("🔍 Digite o termo de pesquisa", placeholder="Busque por descrição, código ou NCM")
        
        with col_search2:
            tipo_busca = st.selectbox("Buscar em:", ["Todos os campos", "Descrição", "Código", "NCM"])
        
        if termo_pesquisa:
            if tipo_busca == "Todos os campos":
                df_resultado = pesquisar_mercadoria(termo_pesquisa)
            else:
                # Busca específica por campo
                conn = conectar()
                campo_map = {"Descrição": "descricao", "Código": "codigo", "NCM": "ncm"}
                campo = campo_map[tipo_busca]
                df_resultado = pd.read_sql_query(
                    f"SELECT * FROM mercadorias WHERE {campo} LIKE ? ORDER BY descricao",
                    conn,
                    params=(f"%{termo_pesquisa}%",)
                )
                conn.close()
            
            if not df_resultado.empty:
                # Destacar termo pesquisado
                st.success(f"✅ Encontradas {len(df_resultado)} mercadoria(s) para '{termo_pesquisa}'")
                
                # Formatando a tabela de resultados
                df_resultado_display = df_resultado.copy()
                df_resultado_display['valor_unit'] = df_resultado_display['valor_unit'].apply(lambda x: f"R$ {x:.2f}")
                df_resultado_display.columns = ['ID', 'Descrição', 'Código', 'NCM', 'Unidade', 'Valor Unitário']
                
                st.dataframe(
                    df_resultado_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Estatísticas da pesquisa
                if len(df_resultado) > 1:
                    col_stats_search1, col_stats_search2 = st.columns(2)
                    with col_stats_search1:
                        valor_medio_search = df_resultado['valor_unit'].mean()
                        st.info(f"💰 Valor médio dos resultados: R$ {valor_medio_search:.2f}")
                    with col_stats_search2:
                        valor_total_search = df_resultado['valor_unit'].sum()
                        st.info(f"💸 Valor total dos resultados: R$ {valor_total_search:.2f}")
                        
            else:
                st.warning(f"❌ Nenhuma mercadoria encontrada para '{termo_pesquisa}'")
                st.info("💡 Dicas de pesquisa:")
                st.markdown("""
                - Tente termos mais gerais
                - Verifique a ortografia
                - Use apenas parte do nome do produto
                - Experimente buscar pelo código ou NCM
                """)
        else:
            st.info("💡 Digite um termo acima para iniciar a pesquisa")
            
            # Sugestões de pesquisa
            conn = conectar()
            df_sugestoes = pd.read_sql_query(
                "SELECT DISTINCT descricao FROM mercadorias ORDER BY descricao LIMIT 5", 
                conn
            )
            conn.close()
            
            if not df_sugestoes.empty:
                st.markdown("**🔍 Sugestões de pesquisa:**")
                for _, row in df_sugestoes.iterrows():
                    if st.button(f"🔍 {row['descricao']}", key=f"sugestao_{row['descricao']}"):
                        st.session_state.termo_pesquisa = row['descricao']
                        st.rerun()
