import sqlite3
import os

DB_PATH = "data/db.sqlite3"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT UNIQUE,
            nome TEXT,
            endereco TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mercadorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            descricao TEXT,
            ncm TEXT,
            unidade TEXT,
            preco REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            numero TEXT,
            cnpj_emitente TEXT,
            nome_emitente TEXT,
            valor_total REAL
        )
    """)

    conn.commit()
    conn.close()