# modules/sefaz_connector.py
import tempfile
import requests
from OpenSSL import crypto

def carregar_certificado(pfx_bytes, senha):
    """Converte certificado .pfx em PEM temporário (para autenticação mTLS)"""
    pfx = crypto.load_pkcs12(pfx_bytes, senha.encode())
    chave_privada = crypto.dump_privatekey(crypto.FILETYPE_PEM, pfx.get_privatekey())
    cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, pfx.get_certificate())

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as cert_file:
        cert_file.write(cert_pem + chave_privada)
        return cert_file.name


def consultar_notas(cert_path, cnpj, ambiente="producao", uf="35"):
    """Consulta notas na SEFAZ via NFeDistribuicaoDFe.
    ambiente = 'producao' ou 'homologacao'
    uf = código da UF (35 = SP, 41 = PR, 33 = RJ, etc.)
    """
    urls = {
        "producao": "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx",
        "homologacao": "https://hom.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx",
    }
    url = urls.get(ambiente, urls["producao"])

    soap_xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                      xmlns:nfe="http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe">
        <soapenv:Body>
            <nfe:nfeDistDFeInteresse>
                <distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
                    <tpAmb>{"1" if ambiente == "producao" else "2"}</tpAmb>
                    <cUFAutor>{uf}</cUFAutor>
                    <CNPJ>{cnpj}</CNPJ>
                    <distNSU>
                        <ultNSU>000000000000000</ultNSU>
                    </distNSU>
                </distDFeInt>
            </nfe:nfeDistDFeInteresse>
        </soapenv:Body>
    </soapenv:Envelope>"""

    headers = {"Content-Type": "text/xml; charset=utf-8"}

    try:
        resp = requests.post(url, data=soap_xml, headers=headers, cert=(cert_path, cert_path))
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"Erro na consulta SEFAZ ({ambiente}): {e}"
