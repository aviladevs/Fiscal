"""
Service layer for processing fiscal documents.
"""
from typing import Dict, Any
from database import (
    Database, EmitterRepository, ReceiverRepository, 
    ProductRepository, DocumentRepository, DocumentItemRepository
)
from xml_parser import parse_xml


class FiscalService:
    """Service for processing fiscal documents."""
    
    def __init__(self, db_path: str = "fiscal.db"):
        self.db = Database(db_path)
        self.emitter_repo = EmitterRepository(self.db)
        self.receiver_repo = ReceiverRepository(self.db)
        self.product_repo = ProductRepository(self.db)
        self.document_repo = DocumentRepository(self.db)
        self.document_item_repo = DocumentItemRepository(self.db)
        
    def process_xml(self, xml_path: str) -> Dict[str, Any]:
        """
        Process XML file and store data in database.
        
        Args:
            xml_path: Path to XML file
            
        Returns:
            Dictionary with processing results
        """
        # Parse XML
        data = parse_xml(xml_path)
        
        # Save emitter
        emitter_id = None
        if data.get('emitter') and data['emitter'].get('cnpj'):
            emitter_id = self.emitter_repo.save(data['emitter'])
        
        # Save receiver
        receiver_id = None
        if data.get('receiver') and data['receiver'].get('cnpj_cpf'):
            receiver_id = self.receiver_repo.save(data['receiver'])
        
        # Save document
        doc_data = {
            'doc_type': data.get('doc_type'),
            'doc_number': data.get('doc_number'),
            'series': data.get('series'),
            'access_key': data.get('access_key'),
            'issue_date': data.get('issue_date'),
            'emitter_id': emitter_id,
            'receiver_id': receiver_id,
            'total_value': data.get('total_value')
        }
        document_id = self.document_repo.save(doc_data)
        
        # Save products and items
        products_saved = 0
        for product_data in data.get('products', []):
            # Save product
            product_id = self.product_repo.save({
                'code': product_data.get('code'),
                'description': product_data.get('description'),
                'ncm': product_data.get('ncm'),
                'unit': product_data.get('unit')
            })
            
            # Save document item
            if product_id and document_id:
                self.document_item_repo.save({
                    'document_id': document_id,
                    'product_id': product_id,
                    'quantity': product_data.get('quantity'),
                    'unit_value': product_data.get('unit_value'),
                    'total_value': product_data.get('total_value')
                })
                products_saved += 1
        
        return {
            'success': True,
            'document_id': document_id,
            'doc_type': data.get('doc_type'),
            'doc_number': data.get('doc_number'),
            'access_key': data.get('access_key'),
            'products_count': products_saved
        }
    
    def search_clients(self, query: str):
        """Search for clients (receivers)."""
        return self.receiver_repo.search(query)
    
    def search_products(self, query: str):
        """Search for products."""
        return self.product_repo.search(query)
