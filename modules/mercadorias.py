import pandas as pd
from modules.database import conectar

def adicionar_mercadoria(descricao, codigo, valor_unit):
    conn = conectar()
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO mercadorias (descricao, codigo, valor_unit) VALUES (?, ?, ?)",
        (descricao, codigo, valor_unit)
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
        "SELECT * FROM mercadorias WHERE descricao LIKE ? OR codigo LIKE ?",
        conn,
        params=(f"%{termo}%", f"%{termo}%")
    )
    conn.close()
    return df
