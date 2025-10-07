import xmltodict

def ler_xml(conteudo):
    dados = xmltodict.parse(conteudo)
    
    if "nfeProc" in dados:
        return extrair_nfe(dados["nfeProc"])
    elif "cteProc" in dados:
        return extrair_cte(dados["cteProc"])
    else:
        return None

def extrair_nfe(nfe):
    ide = nfe["NFe"]["infNFe"]["ide"]
    emit = nfe["NFe"]["infNFe"]["emit"]
    dest = nfe["NFe"]["infNFe"]["dest"]
    produtos = nfe["NFe"]["infNFe"]["det"]

    return {
        "tipo": "NF-e",
        "emitente": emit.get("xNome"),
        "cnpj_emitente": emit.get("CNPJ"),
        "destinatario": dest.get("xNome"),
        "cnpj_dest": dest.get("CNPJ"),
        "itens": [
            {
                "descricao": item["prod"]["xProd"],
                "codigo": item["prod"]["cProd"],
                "valor_unit": float(item["prod"]["vUnCom"])
            }
            for item in (produtos if isinstance(produtos, list) else [produtos])
        ]
    }

def extrair_cte(cte):
    ide = cte["CTe"]["infCte"]["ide"]
    emit = cte["CTe"]["infCte"]["emit"]
    dest = cte["CTe"]["infCte"]["dest"]
    return {
        "tipo": "CT-e",
        "emitente": emit.get("xNome"),
        "cnpj_emitente": emit.get("CNPJ"),
        "destinatario": dest.get("xNome"),
        "cnpj_dest": dest.get("CNPJ"),
    }
