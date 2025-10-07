"""
Database models for storing fiscal document data.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class Database:
    """Database connection and table management."""
    
    def __init__(self, db_path: str = "fiscal.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            
    def init_db(self):
        """Initialize database schema."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Table for emitters (emitentes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emitters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cnpj TEXT NOT NULL,
                name TEXT NOT NULL,
                fantasy_name TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                cep TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cnpj)
            )
        ''')
        
        # Table for receivers (destinatários/clientes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cnpj_cpf TEXT NOT NULL,
                name TEXT NOT NULL,
                fantasy_name TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                cep TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cnpj_cpf)
            )
        ''')
        
        # Table for products (mercadorias)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                description TEXT NOT NULL,
                ncm TEXT,
                unit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(code)
            )
        ''')
        
        # Table for documents (NF-e or CT-e)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT NOT NULL,
                doc_number TEXT NOT NULL,
                series TEXT,
                access_key TEXT NOT NULL,
                issue_date TEXT,
                emitter_id INTEGER,
                receiver_id INTEGER,
                total_value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (emitter_id) REFERENCES emitters (id),
                FOREIGN KEY (receiver_id) REFERENCES receivers (id),
                UNIQUE(access_key)
            )
        ''')
        
        # Table for document items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity REAL,
                unit_value REAL,
                total_value REAL,
                FOREIGN KEY (document_id) REFERENCES documents (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        self.close()


class EmitterRepository:
    """Repository for managing emitters."""
    
    def __init__(self, db: Database):
        self.db = db
        
    def save(self, data: Dict[str, Any]) -> int:
        """Save or update an emitter."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO emitters (cnpj, name, fantasy_name, address, city, state, cep)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cnpj) DO UPDATE SET
                    name=excluded.name,
                    fantasy_name=excluded.fantasy_name,
                    address=excluded.address,
                    city=excluded.city,
                    state=excluded.state,
                    cep=excluded.cep
            ''', (
                data.get('cnpj'),
                data.get('name'),
                data.get('fantasy_name'),
                data.get('address'),
                data.get('city'),
                data.get('state'),
                data.get('cep')
            ))
            conn.commit()
            
            # Get the ID
            cursor.execute('SELECT id FROM emitters WHERE cnpj = ?', (data.get('cnpj'),))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            self.db.close()


class ReceiverRepository:
    """Repository for managing receivers/clients."""
    
    def __init__(self, db: Database):
        self.db = db
        
    def save(self, data: Dict[str, Any]) -> int:
        """Save or update a receiver."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO receivers (cnpj_cpf, name, fantasy_name, address, city, state, cep)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cnpj_cpf) DO UPDATE SET
                    name=excluded.name,
                    fantasy_name=excluded.fantasy_name,
                    address=excluded.address,
                    city=excluded.city,
                    state=excluded.state,
                    cep=excluded.cep
            ''', (
                data.get('cnpj_cpf'),
                data.get('name'),
                data.get('fantasy_name'),
                data.get('address'),
                data.get('city'),
                data.get('state'),
                data.get('cep')
            ))
            conn.commit()
            
            # Get the ID
            cursor.execute('SELECT id FROM receivers WHERE cnpj_cpf = ?', (data.get('cnpj_cpf'),))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            self.db.close()
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search receivers by name or CNPJ/CPF."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM receivers 
                WHERE name LIKE ? OR cnpj_cpf LIKE ? OR fantasy_name LIKE ?
                ORDER BY name
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self.db.close()


class ProductRepository:
    """Repository for managing products."""
    
    def __init__(self, db: Database):
        self.db = db
        
    def save(self, data: Dict[str, Any]) -> int:
        """Save or update a product."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (code, description, ncm, unit)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    description=excluded.description,
                    ncm=excluded.ncm,
                    unit=excluded.unit
            ''', (
                data.get('code'),
                data.get('description'),
                data.get('ncm'),
                data.get('unit')
            ))
            conn.commit()
            
            # Get the ID
            cursor.execute('SELECT id FROM products WHERE code = ?', (data.get('code'),))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            self.db.close()
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search products by description or code."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM products 
                WHERE description LIKE ? OR code LIKE ?
                ORDER BY description
            ''', (f'%{query}%', f'%{query}%'))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self.db.close()


class DocumentRepository:
    """Repository for managing documents."""
    
    def __init__(self, db: Database):
        self.db = db
        
    def save(self, data: Dict[str, Any]) -> int:
        """Save a document."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO documents (doc_type, doc_number, series, access_key, 
                                      issue_date, emitter_id, receiver_id, total_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(access_key) DO UPDATE SET
                    doc_number=excluded.doc_number,
                    series=excluded.series,
                    issue_date=excluded.issue_date,
                    total_value=excluded.total_value
            ''', (
                data.get('doc_type'),
                data.get('doc_number'),
                data.get('series'),
                data.get('access_key'),
                data.get('issue_date'),
                data.get('emitter_id'),
                data.get('receiver_id'),
                data.get('total_value')
            ))
            conn.commit()
            
            # Get the ID
            cursor.execute('SELECT id FROM documents WHERE access_key = ?', (data.get('access_key'),))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            self.db.close()


class DocumentItemRepository:
    """Repository for managing document items."""
    
    def __init__(self, db: Database):
        self.db = db
        
    def save(self, data: Dict[str, Any]) -> int:
        """Save a document item."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO document_items (document_id, product_id, quantity, unit_value, total_value)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('document_id'),
                data.get('product_id'),
                data.get('quantity'),
                data.get('unit_value'),
                data.get('total_value')
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            self.db.close()
