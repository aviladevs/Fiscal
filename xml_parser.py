"""
XML parser for Brazilian fiscal documents (NF-e and CT-e).
"""
from lxml import etree
from typing import Dict, Any, List, Optional


class NFeParser:
    """Parser for NF-e (Nota Fiscal Eletrônica) XML documents."""
    
    # NF-e namespace
    NFE_NS = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = None
        self.root = None
        
    def parse(self) -> Dict[str, Any]:
        """Parse NF-e XML and extract data."""
        try:
            self.tree = etree.parse(self.xml_path)
            self.root = self.tree.getroot()
            
            # Try with namespace
            inf_nfe = self.root.find('.//nfe:infNFe', self.NFE_NS)
            
            # Try without namespace if not found
            if inf_nfe is None:
                inf_nfe = self.root.find('.//{*}infNFe')
            
            if inf_nfe is None:
                raise ValueError("Invalid NF-e XML structure")
            
            return {
                'doc_type': 'NF-e',
                'access_key': self._get_access_key(inf_nfe),
                'doc_number': self._get_text(inf_nfe, './/{*}ide/{*}nNF'),
                'series': self._get_text(inf_nfe, './/{*}ide/{*}serie'),
                'issue_date': self._get_text(inf_nfe, './/{*}ide/{*}dhEmi'),
                'total_value': self._get_float(inf_nfe, './/{*}total/{*}ICMSTot/{*}vNF'),
                'emitter': self._extract_emitter(inf_nfe),
                'receiver': self._extract_receiver(inf_nfe),
                'products': self._extract_products(inf_nfe)
            }
        except Exception as e:
            raise ValueError(f"Error parsing NF-e: {str(e)}")
    
    def _get_access_key(self, element) -> str:
        """Extract access key from infNFe Id attribute."""
        id_attr = element.get('Id', '')
        # Remove 'NFe' prefix if present
        return id_attr.replace('NFe', '') if id_attr else ''
    
    def _get_text(self, element, xpath: str, default: str = '') -> str:
        """Get text from element using XPath."""
        found = element.find(xpath)
        return found.text if found is not None and found.text else default
    
    def _get_float(self, element, xpath: str, default: float = 0.0) -> float:
        """Get float value from element using XPath."""
        text = self._get_text(element, xpath)
        try:
            return float(text) if text else default
        except ValueError:
            return default
    
    def _extract_emitter(self, inf_nfe) -> Dict[str, Any]:
        """Extract emitter data."""
        emit = inf_nfe.find('.//{*}emit')
        if emit is None:
            return {}
        
        return {
            'cnpj': self._get_text(emit, './/{*}CNPJ'),
            'name': self._get_text(emit, './/{*}xNome'),
            'fantasy_name': self._get_text(emit, './/{*}xFant'),
            'address': self._get_text(emit, './/{*}enderEmit/{*}xLgr'),
            'city': self._get_text(emit, './/{*}enderEmit/{*}xMun'),
            'state': self._get_text(emit, './/{*}enderEmit/{*}UF'),
            'cep': self._get_text(emit, './/{*}enderEmit/{*}CEP')
        }
    
    def _extract_receiver(self, inf_nfe) -> Dict[str, Any]:
        """Extract receiver data."""
        dest = inf_nfe.find('.//{*}dest')
        if dest is None:
            return {}
        
        # Try both CNPJ and CPF
        cnpj_cpf = self._get_text(dest, './/{*}CNPJ')
        if not cnpj_cpf:
            cnpj_cpf = self._get_text(dest, './/{*}CPF')
        
        return {
            'cnpj_cpf': cnpj_cpf,
            'name': self._get_text(dest, './/{*}xNome'),
            'fantasy_name': self._get_text(dest, './/{*}xFant'),
            'address': self._get_text(dest, './/{*}enderDest/{*}xLgr'),
            'city': self._get_text(dest, './/{*}enderDest/{*}xMun'),
            'state': self._get_text(dest, './/{*}enderDest/{*}UF'),
            'cep': self._get_text(dest, './/{*}enderDest/{*}CEP')
        }
    
    def _extract_products(self, inf_nfe) -> List[Dict[str, Any]]:
        """Extract product data."""
        products = []
        
        for det in inf_nfe.findall('.//{*}det'):
            prod = det.find('.//{*}prod')
            if prod is None:
                continue
            
            products.append({
                'code': self._get_text(prod, './/{*}cProd'),
                'description': self._get_text(prod, './/{*}xProd'),
                'ncm': self._get_text(prod, './/{*}NCM'),
                'unit': self._get_text(prod, './/{*}uCom'),
                'quantity': self._get_float(prod, './/{*}qCom'),
                'unit_value': self._get_float(prod, './/{*}vUnCom'),
                'total_value': self._get_float(prod, './/{*}vProd')
            })
        
        return products


class CTeParser:
    """Parser for CT-e (Conhecimento de Transporte Eletrônico) XML documents."""
    
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = None
        self.root = None
        
    def parse(self) -> Dict[str, Any]:
        """Parse CT-e XML and extract data."""
        try:
            self.tree = etree.parse(self.xml_path)
            self.root = self.tree.getroot()
            
            # Find infCte element
            inf_cte = self.root.find('.//{*}infCte')
            
            if inf_cte is None:
                raise ValueError("Invalid CT-e XML structure")
            
            return {
                'doc_type': 'CT-e',
                'access_key': self._get_access_key(inf_cte),
                'doc_number': self._get_text(inf_cte, './/{*}ide/{*}nCT'),
                'series': self._get_text(inf_cte, './/{*}ide/{*}serie'),
                'issue_date': self._get_text(inf_cte, './/{*}ide/{*}dhEmi'),
                'total_value': self._get_float(inf_cte, './/{*}vPrest/{*}vTPrest'),
                'emitter': self._extract_emitter(inf_cte),
                'receiver': self._extract_receiver(inf_cte),
                'products': []  # CT-e doesn't have products, only transport info
            }
        except Exception as e:
            raise ValueError(f"Error parsing CT-e: {str(e)}")
    
    def _get_access_key(self, element) -> str:
        """Extract access key from infCte Id attribute."""
        id_attr = element.get('Id', '')
        # Remove 'CTe' prefix if present
        return id_attr.replace('CTe', '') if id_attr else ''
    
    def _get_text(self, element, xpath: str, default: str = '') -> str:
        """Get text from element using XPath."""
        found = element.find(xpath)
        return found.text if found is not None and found.text else default
    
    def _get_float(self, element, xpath: str, default: float = 0.0) -> float:
        """Get float value from element using XPath."""
        text = self._get_text(element, xpath)
        try:
            return float(text) if text else default
        except ValueError:
            return default
    
    def _extract_emitter(self, inf_cte) -> Dict[str, Any]:
        """Extract emitter data."""
        emit = inf_cte.find('.//{*}emit')
        if emit is None:
            return {}
        
        return {
            'cnpj': self._get_text(emit, './/{*}CNPJ'),
            'name': self._get_text(emit, './/{*}xNome'),
            'fantasy_name': self._get_text(emit, './/{*}xFant'),
            'address': self._get_text(emit, './/{*}enderEmit/{*}xLgr'),
            'city': self._get_text(emit, './/{*}enderEmit/{*}xMun'),
            'state': self._get_text(emit, './/{*}enderEmit/{*}UF'),
            'cep': self._get_text(emit, './/{*}enderEmit/{*}CEP')
        }
    
    def _extract_receiver(self, inf_cte) -> Dict[str, Any]:
        """Extract receiver data."""
        dest = inf_cte.find('.//{*}dest')
        if dest is None:
            # Try rem (remetente) or receb (recebedor)
            dest = inf_cte.find('.//{*}rem')
        if dest is None:
            dest = inf_cte.find('.//{*}receb')
        if dest is None:
            return {}
        
        # Try both CNPJ and CPF
        cnpj_cpf = self._get_text(dest, './/{*}CNPJ')
        if not cnpj_cpf:
            cnpj_cpf = self._get_text(dest, './/{*}CPF')
        
        return {
            'cnpj_cpf': cnpj_cpf,
            'name': self._get_text(dest, './/{*}xNome'),
            'fantasy_name': self._get_text(dest, './/{*}xFant'),
            'address': self._get_text(dest, './/{*}enderDest/{*}xLgr') or self._get_text(dest, './/{*}ender/{*}xLgr'),
            'city': self._get_text(dest, './/{*}enderDest/{*}xMun') or self._get_text(dest, './/{*}ender/{*}xMun'),
            'state': self._get_text(dest, './/{*}enderDest/{*}UF') or self._get_text(dest, './/{*}ender/{*}UF'),
            'cep': self._get_text(dest, './/{*}enderDest/{*}CEP') or self._get_text(dest, './/{*}ender/{*}CEP')
        }


def parse_xml(xml_path: str) -> Dict[str, Any]:
    """
    Auto-detect and parse XML file (NF-e or CT-e).
    """
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()
        
        # Check if it's NF-e
        if root.find('.//{*}infNFe') is not None:
            parser = NFeParser(xml_path)
            return parser.parse()
        
        # Check if it's CT-e
        elif root.find('.//{*}infCte') is not None:
            parser = CTeParser(xml_path)
            return parser.parse()
        
        else:
            raise ValueError("Unknown XML document type. Expected NF-e or CT-e.")
            
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")
