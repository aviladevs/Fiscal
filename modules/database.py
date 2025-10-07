import sqlite3
import os

DB_PATH = "data/db.sqlite3"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Alias para compatibilidade com código existente
def conectar():
    return get_connection()

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT UNIQUE,
            nome TEXT,
            endereco TEXT,
            telefone TEXT,
            email TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mercadorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            descricao TEXT,
            ncm TEXT,
            unidade TEXT,
            valor_unit REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            numero TEXT,
            cnpj_emitente TEXT,
            nome_emitente TEXT,
            valor_total REAL,
            data_sincronizacao TEXT
        )
    """)

    # Migration: Add data_sincronizacao column if it doesn't exist
    try:
        cur.execute("SELECT data_sincronizacao FROM notas LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        cur.execute("ALTER TABLE notas ADD COLUMN data_sincronizacao TEXT")
        print("Migration: Added data_sincronizacao column to notas table")

    conn.commit()
    conn.close()