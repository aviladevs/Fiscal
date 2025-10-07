#!/usr/bin/env python3
"""
CLI interface for Fiscal document processor.
"""
import sys
import argparse
from pathlib import Path
from database import Database
from service import FiscalService


def init_database():
    """Initialize database tables."""
    db = Database()
    db.init_db()
    print("✓ Database initialized successfully!")


def process_xml(xml_path: str):
    """Process XML file and store data."""
    if not Path(xml_path).exists():
        print(f"✗ File not found: {xml_path}")
        return 1
    
    try:
        service = FiscalService()
        result = service.process_xml(xml_path)
        
        if result['success']:
            print(f"✓ Document processed successfully!")
            print(f"  Type: {result['doc_type']}")
            print(f"  Number: {result['doc_number']}")
            print(f"  Access Key: {result['access_key']}")
            print(f"  Products: {result['products_count']}")
        else:
            print("✗ Failed to process document")
            return 1
            
    except Exception as e:
        print(f"✗ Error processing XML: {str(e)}")
        return 1
    
    return 0


def search_clients(query: str):
    """Search for clients."""
    try:
        service = FiscalService()
        results = service.search_clients(query)
        
        if not results:
            print(f"No clients found for query: '{query}'")
            return 0
        
        print(f"\n{len(results)} client(s) found:\n")
        for client in results:
            print(f"ID: {client['id']}")
            print(f"Name: {client['name']}")
            if client.get('fantasy_name'):
                print(f"Fantasy Name: {client['fantasy_name']}")
            print(f"CNPJ/CPF: {client['cnpj_cpf']}")
            if client.get('city'):
                print(f"City: {client['city']}/{client.get('state', '')}")
            print("-" * 50)
            
    except Exception as e:
        print(f"✗ Error searching clients: {str(e)}")
        return 1
    
    return 0


def search_products(query: str):
    """Search for products."""
    try:
        service = FiscalService()
        results = service.search_products(query)
        
        if not results:
            print(f"No products found for query: '{query}'")
            return 0
        
        print(f"\n{len(results)} product(s) found:\n")
        for product in results:
            print(f"ID: {product['id']}")
            print(f"Code: {product['code']}")
            print(f"Description: {product['description']}")
            if product.get('ncm'):
                print(f"NCM: {product['ncm']}")
            if product.get('unit'):
                print(f"Unit: {product['unit']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"✗ Error searching products: {str(e)}")
        return 1
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Fiscal - Process Brazilian fiscal documents (NF-e and CT-e)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize database')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process XML file')
    process_parser.add_argument('xml_file', help='Path to XML file')
    
    # Search clients command
    search_clients_parser = subparsers.add_parser('search-clients', help='Search for clients')
    search_clients_parser.add_argument('query', help='Search query (name or CNPJ/CPF)')
    
    # Search products command
    search_products_parser = subparsers.add_parser('search-products', help='Search for products')
    search_products_parser.add_argument('query', help='Search query (description or code)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == 'init':
        init_database()
        return 0
    elif args.command == 'process':
        return process_xml(args.xml_file)
    elif args.command == 'search-clients':
        return search_clients(args.query)
    elif args.command == 'search-products':
        return search_products(args.query)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
