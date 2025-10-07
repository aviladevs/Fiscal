# 🏛️ Fiscal - Sistema de Leitura de NF-e e CT-e

**Fiscal** é uma plataforma web desenvolvida em **Python + Streamlit**, modular e moderna, para:  

- Leitura e extração de informações de **Notas Fiscais Eletrônicas (NF-e)** e **Conhecimentos de Transporte Eletrônico (CT-e)** via XML.  
- Cadastro e pesquisa de **clientes** e **mercadorias**.  
- Integração segura com a **SEFAZ** usando **certificado digital A1 (.pfx)**.  
- Layout moderno inspirado em **iOS 18**, com interface fluida e minimalista.

O sistema é ideal para empresas que precisam automatizar a gestão fiscal, mantendo dados estruturados localmente e permitindo sincronização controlada com a SEFAZ.

---

## 🚀 Funcionalidades

1. **Leitura de XML**
   - Upload de arquivos NF-e e CT-e.
   - Extração automática de informações de emitente, valores e mercadorias.
   - Armazenamento no banco **SQLite** local (`data/db.sqlite3`).

2. **Cadastro de Clientes**
   - Inserção, pesquisa e atualização de clientes.
   - Campos: **CNPJ**, **Nome/Razão Social**, **Endereço**.

3. **Cadastro de Mercadorias**
   - Inserção e listagem de produtos.
   - Campos: **Código interno**, **Descrição**, **NCM**, **Unidade**, **Preço**.

4. **Integração SEFAZ**
   - Upload seguro de certificado A1 (.pfx).
   - Botão moderno de sincronização (🔄) com controle de **1 hora** entre consultas.
   - Visual estilo iOS, com glassmorphism e feedback de status.

5. **Banco de Dados Local**
   - SQLite para armazenar clientes, mercadorias e notas fiscais.
   - Estrutura modular e escalável.

---

## 📂 Estrutura do Repositório
Fiscal/
│
├── app.py                     # Arquivo principal Streamlit
├── requirements.txt           # Dependências Python
├── modules/                   # Módulos Python
│   ├── init.py
│   ├── xml_reader.py
│   ├── cadastro_clientes.py
│   ├── mercadorias.py
│   ├── sefaz_integration.py
│   └── database.py
└── data/                      # Pastas de armazenamento
├── xmls/                  # XMLs carregados
└── certificados/          # Certificados A1

---

## ⚙️ Instalação e Deploy Local

1. Clone o repositório:

```bash
git clone https://github.com/aviladevs/Fiscal.git
cd Fiscal
