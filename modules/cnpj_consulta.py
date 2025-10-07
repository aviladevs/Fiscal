import requests
import streamlit as st
import json

def consultar_cnpj(cnpj):
    """
    Consulta dados do CNPJ na API da ReceitaWS (gratuita)
    """
    # Remove caracteres especiais do CNPJ
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj_limpo) != 14:
        return None
    
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'OK':
                return {
                    'cnpj': data.get('cnpj', ''),
                    'nome': data.get('nome', ''),
                    'fantasia': data.get('fantasia', ''),
                    'endereco': f"{data.get('logradouro', '')}, {data.get('numero', '')} - {data.get('bairro', '')} - {data.get('municipio', '')}/{data.get('uf', '')} - CEP: {data.get('cep', '')}",
                    'situacao': data.get('situacao', ''),
                    'porte': data.get('porte', ''),
                    'atividade_principal': data.get('atividade_principal', [{}])[0].get('text', '') if data.get('atividade_principal') else '',
                    'telefone': data.get('telefone', ''),
                    'email': data.get('email', '')
                }
            else:
                st.error(f"❌ Erro na consulta: {data.get('message', 'CNPJ não encontrado')}")
                return None
                
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout na consulta. Tente novamente.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro na consulta: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
        return None

def validar_cnpj(cnpj):
    """
    Valida se o CNPJ tem formato válido
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj_limpo) != 14:
        return False
    
    # Algoritmo de validação do CNPJ
    def calcular_digito(cnpj_base, multiplicadores):
        soma = sum(int(digito) * mult for digito, mult in zip(cnpj_base, multiplicadores))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    cnpj_base = cnpj_limpo[:12]
    
    # Primeiro dígito verificador
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    primeiro_digito = calcular_digito(cnpj_base, multiplicadores1)
    
    # Segundo dígito verificador
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    segundo_digito = calcular_digito(cnpj_base + str(primeiro_digito), multiplicadores2)
    
    return cnpj_limpo == cnpj_base + str(primeiro_digito) + str(segundo_digito)

def formatar_cnpj(cnpj):
    """
    Formata CNPJ para o padrão XX.XXX.XXX/XXXX-XX
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj_limpo) == 14:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:14]}"
    
    return cnpj