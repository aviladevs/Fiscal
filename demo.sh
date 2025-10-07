#!/bin/bash
# Demonstration script for Fiscal application

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          FISCAL - Brazilian Fiscal Document Processor          ║"
echo "║                      Complete Demonstration                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Clean start
echo "🗑️  Cleaning previous database..."
rm -f fiscal.db
echo ""

# Initialize database
echo "🔧 Initializing database..."
python fiscal.py init
echo ""

# Process NF-e
echo "📄 Processing NF-e (Nota Fiscal Eletrônica)..."
python fiscal.py process samples/sample_nfe.xml
echo ""

# Process CT-e
echo "🚚 Processing CT-e (Conhecimento de Transporte)..."
python fiscal.py process samples/sample_cte.xml
echo ""

# Search operations
echo "🔍 Searching for clients containing 'CLIENTE'..."
python fiscal.py search-clients "CLIENTE"
echo ""

echo "🔍 Searching for clients containing 'DESTINATARIO'..."
python fiscal.py search-clients "DESTINATARIO"
echo ""

echo "🔍 Searching for products containing 'NOTEBOOK'..."
python fiscal.py search-products "NOTEBOOK"
echo ""

echo "🔍 Searching for products containing 'MOUSE'..."
python fiscal.py search-products "MOUSE"
echo ""

# Show database statistics
echo "📊 Database Statistics:"
echo "   Emitters: $(sqlite3 fiscal.db 'SELECT COUNT(*) FROM emitters;')"
echo "   Receivers: $(sqlite3 fiscal.db 'SELECT COUNT(*) FROM receivers;')"
echo "   Products: $(sqlite3 fiscal.db 'SELECT COUNT(*) FROM products;')"
echo "   Documents: $(sqlite3 fiscal.db 'SELECT COUNT(*) FROM documents;')"
echo "   Document Items: $(sqlite3 fiscal.db 'SELECT COUNT(*) FROM document_items;')"
echo ""

echo "✅ Demonstration completed successfully!"
