import pandas as pd
from modules.database import conectar

def adicionar_cliente(nome, cnpj_cpf):
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO clientes (nome, cnpj_cpf) VALUES (?, ?)", (nome, cnpj_cpf))
    conn.commit()
    conn.close()

def listar_clientes():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    return df

def pesquisar_cliente(termo):
    conn = conectar()
    df = pd.read_sql_query(
        "SELECT * FROM clientes WHERE nome LIKE ? OR cnpj_cpf LIKE ?",
        conn,
        params=(f"%{termo}%", f"%{termo}%")
    )
    conn.close()
    return df
