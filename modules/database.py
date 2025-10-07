import sqlite3

def conectar():
    return sqlite3.connect("data/base.db")

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cnpj_cpf TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS mercadorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT,
            codigo TEXT UNIQUE,
            valor_unit REAL
        )
    ''')

    conn.commit()
    conn.close()
