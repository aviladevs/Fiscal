# modules/sefaz_connector.py
import tempfile
import requests
import xml.etree.ElementTree as ET
from OpenSSL import crypto
import base64
import os
from datetime import datetime
from modules import database

def carregar_certificado(pfx_bytes, senha):
    """Converte certificado .pfx em PEM temporário (para autenticação mTLS)"""
    try:
        pfx = crypto.load_pkcs12(pfx_bytes, senha.encode())
        chave_privada = crypto.dump_privatekey(crypto.FILETYPE_PEM, pfx.get_privatekey())
        cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, pfx.get_certificate())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as cert_file:
            cert_file.write(cert_pem + chave_privada)
            return cert_file.name, pfx.get_certificate()
    except Exception as e:
        raise Exception(f"Erro ao carregar certificado: {e}")

def extrair_cnpj_certificado(certificado):
    """Extrai o CNPJ do certificado digital"""
    try:
        subject = certificado.get_subject()
        # O CNPJ geralmente está no campo CN (Common Name) do certificado
        cn = subject.CN
        
        # Procura por padrão de CNPJ no CN
        import re
        cnpj_pattern = r'(\d{14})'
        match = re.search(cnpj_pattern, cn)
        
        if match:
            cnpj = match.group(1)
            # Formata CNPJ
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
        
        return None
    except Exception as e:
        print(f"Erro ao extrair CNPJ: {e}")
        return None

def consultar_notas_distribuicao_dfe(cert_path, cnpj, ambiente="homologacao", uf="35", ultimo_nsu="000000000000000"):
    """
    Consulta notas na SEFAZ via NFeDistribuicaoDFe.
    Esta é a forma oficial de consultar NFes destinadas ao CNPJ
    """
    urls = {
        "producao": "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx",
        "homologacao": "https://hom.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx",
    }
    
    url = urls.get(ambiente, urls["homologacao"])
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

    soap_xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                      xmlns:nfe="http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe">
        <soapenv:Header/>
        <soapenv:Body>
            <nfe:nfeDistDFeInteresse>
                <nfeDadosMsg>
                    <distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
                        <tpAmb>{"1" if ambiente == "producao" else "2"}</tpAmb>
                        <cUFAutor>{uf}</cUFAutor>
                        <CNPJ>{cnpj_limpo}</CNPJ>
                        <distNSU>
                            <ultNSU>{ultimo_nsu}</ultNSU>
                        </distNSU>
                    </distDFeInt>
                </nfeDadosMsg>
            </nfe:nfeDistDFeInteresse>
        </soapenv:Body>
    </soapenv:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse"
    }

    try:
        resp = requests.post(url, data=soap_xml, headers=headers, cert=cert_path, timeout=30)
        resp.raise_for_status()
        
        return processar_resposta_distribuicao_dfe(resp.text)
        
    except requests.exceptions.RequestException as e:
        return {"erro": f"Erro na requisição: {e}", "sucesso": False}
    except Exception as e:
        return {"erro": f"Erro inesperado: {e}", "sucesso": False}

def processar_resposta_distribuicao_dfe(xml_response):
    """Processa a resposta XML da consulta DistribuicaoDFe"""
    try:
        # Parse do XML de resposta
        root = ET.fromstring(xml_response)
        
        # Namespaces comuns da NFe
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'nfe': 'http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe',
            'ns': 'http://www.portalfiscal.inf.br/nfe'
        }
        
        # Procura por elementos de retorno
        ret_dist_dfe = root.find('.//ns:retDistDFeInt', namespaces)
        
        if ret_dist_dfe is None:
            # Tenta sem namespace
            ret_dist_dfe = root.find('.//retDistDFeInt')
        
        if ret_dist_dfe is None:
            return {"erro": "Resposta inválida da SEFAZ", "sucesso": False, "xml_completo": xml_response}
        
        # Extrai informações básicas
        codigo_status = ret_dist_dfe.find('.//cStat')
        motivo = ret_dist_dfe.find('.//xMotivo')
        ultimo_nsu = ret_dist_dfe.find('.//ultNSU')
        max_nsu = ret_dist_dfe.find('.//maxNSU')
        
        resultado = {
            "sucesso": True,
            "codigo_status": codigo_status.text if codigo_status is not None else "N/A",
            "motivo": motivo.text if motivo is not None else "N/A",
            "ultimo_nsu": ultimo_nsu.text if ultimo_nsu is not None else "000000000000000",
            "max_nsu": max_nsu.text if max_nsu is not None else "000000000000000",
            "documentos": []
        }
        
        # Processa documentos encontrados
        documentos = ret_dist_dfe.findall('.//loteDistDFeInt/docZip')
        
        for doc in documentos:
            nsu = doc.get('NSU', 'N/A')
            schema = doc.get('schema', 'N/A')
            
            # Decodifica o conteúdo base64
            try:
                conteudo_b64 = doc.text
                if conteudo_b64:
                    conteudo_xml = base64.b64decode(conteudo_b64).decode('utf-8')
                    
                    # Processa diferentes tipos de documento
                    if 'resNFe' in schema:
                        doc_info = processar_resumo_nfe(conteudo_xml)
                    elif 'procNFe' in schema:
                        doc_info = processar_nfe_completa(conteudo_xml)
                    elif 'resEvento' in schema:
                        doc_info = processar_evento_nfe(conteudo_xml)
                    else:
                        doc_info = {"tipo": schema, "processado": False}
                    
                    doc_info.update({
                        "nsu": nsu,
                        "schema": schema,
                        "xml_original": conteudo_xml
                    })
                    
                    resultado["documentos"].append(doc_info)
                    
            except Exception as e:
                resultado["documentos"].append({
                    "nsu": nsu,
                    "schema": schema,
                    "erro": f"Erro ao processar documento: {e}"
                })
        
        return resultado
        
    except ET.ParseError as e:
        return {"erro": f"Erro ao fazer parse do XML: {e}", "sucesso": False, "xml_completo": xml_response}
    except Exception as e:
        return {"erro": f"Erro ao processar resposta: {e}", "sucesso": False}

def processar_resumo_nfe(xml_content):
    """Processa resumo de NFe e salva no banco"""
    try:
        root = ET.fromstring(xml_content)
        
        # Extrai dados do resumo
        dados = {
            "tipo": "NFe_Resumo",
            "chave": root.get('chNFe', 'N/A'),
            "cnpj_emitente": root.get('CNPJ', 'N/A'),
            "nome_emitente": root.get('xNome', 'N/A'),
            "data_emissao": root.get('dhEmi', 'N/A'),
            "valor_total": float(root.get('vNF', 0)),
            "situacao": root.get('cSitNFe', 'N/A'),
            "processado": True
        }
        
        # Salva no banco de dados
        salvar_documento_no_banco(dados)
        
        return dados
        
    except Exception as e:
        return {"tipo": "NFe_Resumo", "erro": f"Erro ao processar resumo: {e}", "processado": False}

def processar_nfe_completa(xml_content):
    """Processa NFe completa"""
    try:
        root = ET.fromstring(xml_content)
        
        # Busca dados da NFe
        inf_nfe = root.find('.//infNFe')
        emit = root.find('.//emit')
        total = root.find('.//total/ICMSTot')
        
        dados = {
            "tipo": "NFe_Completa",
            "chave": inf_nfe.get('Id', 'N/A').replace('NFe', '') if inf_nfe is not None else 'N/A',
            "cnpj_emitente": emit.find('CNPJ').text if emit is not None and emit.find('CNPJ') is not None else 'N/A',
            "nome_emitente": emit.find('xNome').text if emit is not None and emit.find('xNome') is not None else 'N/A',
            "valor_total": float(total.find('vNF').text) if total is not None and total.find('vNF') is not None else 0,
            "processado": True
        }
        
        # Salva no banco de dados
        salvar_documento_no_banco(dados)
        
        return dados
        
    except Exception as e:
        return {"tipo": "NFe_Completa", "erro": f"Erro ao processar NFe: {e}", "processado": False}

def processar_evento_nfe(xml_content):
    """Processa eventos de NFe (cancelamento, carta de correção, etc.)"""
    try:
        root = ET.fromstring(xml_content)
        
        dados = {
            "tipo": "Evento_NFe",
            "chave": root.get('chNFe', 'N/A'),
            "tipo_evento": root.get('tpEvento', 'N/A'),
            "descricao": root.get('xEvento', 'N/A'),
            "processado": True
        }
        
        return dados
        
    except Exception as e:
        return {"tipo": "Evento_NFe", "erro": f"Erro ao processar evento: {e}", "processado": False}

def salvar_documento_no_banco(dados):
    """Salva documento no banco de dados"""
    try:
        conn = database.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT OR REPLACE INTO notas 
            (tipo, numero, cnpj_emitente, nome_emitente, valor_total, data_sincronizacao) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dados.get('tipo', 'N/A'),
            dados.get('chave', 'N/A'),
            dados.get('cnpj_emitente', 'N/A'),
            dados.get('nome_emitente', 'N/A'),
            dados.get('valor_total', 0),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao salvar no banco: {e}")

def consultar_e_sincronizar_nfes(cert_path, senha, ambiente="homologacao"):
    """Função principal para consultar e sincronizar NFes"""
    try:
        # Carrega certificado e extrai CNPJ
        with open(cert_path, 'rb') as f:
            cert_bytes = f.read()
        
        cert_pem_path, certificado = carregar_certificado(cert_bytes, senha)
        cnpj = extrair_cnpj_certificado(certificado)
        
        if not cnpj:
            return {"erro": "Não foi possível extrair CNPJ do certificado", "sucesso": False}
        
        # Consulta documentos na SEFAZ
        resultado = consultar_notas_distribuicao_dfe(cert_pem_path, cnpj, ambiente)
        
        # Remove arquivo temporário
        if os.path.exists(cert_pem_path):
            os.unlink(cert_pem_path)
        
        return resultado
        
    except Exception as e:
        return {"erro": f"Erro na sincronização: {e}", "sucesso": False}
