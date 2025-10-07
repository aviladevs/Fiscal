# Fiscal

Sistema de processamento de documentos fiscais eletrônicos brasileiros (NF-e e CT-e).

## 🧠 Conceito

O Fiscal é uma aplicação para processar e gerenciar documentos fiscais eletrônicos:

1. O usuário envia o XML (NF-e ou CT-e)
2. O app extrai dados-chave (emitente, destinatário, produtos, valores, etc)
3. Os dados são armazenados no SQLite
4. É possível pesquisar clientes e mercadorias cadastrados

## 📋 Funcionalidades

- ✅ Importação de NF-e (Nota Fiscal Eletrônica)
- ✅ Importação de CT-e (Conhecimento de Transporte Eletrônico)
- ✅ Extração automática de dados dos XMLs
- ✅ Armazenamento em banco de dados SQLite
- ✅ Busca de clientes cadastrados
- ✅ Busca de produtos cadastrados
- ✅ Interface CLI (Command Line Interface)

## 🚀 Instalação

### Requisitos

- Python 3.6 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/aviladevs/Fiscal.git
cd Fiscal
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Inicialize o banco de dados:
```bash
python fiscal.py init
```

## 💻 Uso

### Processar um XML

Para processar um documento fiscal XML:

```bash
python fiscal.py process caminho/para/arquivo.xml
```

Exemplo:
```bash
python fiscal.py process samples/sample_nfe.xml
```

### Buscar Clientes

Para buscar clientes cadastrados:

```bash
python fiscal.py search-clients "nome ou CNPJ"
```

Exemplo:
```bash
python fiscal.py search-clients "CLIENTE"
```

### Buscar Produtos

Para buscar produtos cadastrados:

```bash
python fiscal.py search-products "descrição ou código"
```

Exemplo:
```bash
python fiscal.py search-products "NOTEBOOK"
```

## 📁 Estrutura do Projeto

```
Fiscal/
├── fiscal.py          # CLI principal
├── database.py        # Modelos e repositórios do banco de dados
├── xml_parser.py      # Parsers para NF-e e CT-e
├── service.py         # Camada de serviço
├── requirements.txt   # Dependências Python
├── samples/           # XMLs de exemplo
│   ├── sample_nfe.xml
│   └── sample_cte.xml
└── README.md
```

## 🗄️ Estrutura do Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

- **emitters**: Emitentes dos documentos
- **receivers**: Destinatários/Clientes
- **products**: Produtos/Mercadorias
- **documents**: Documentos fiscais (NF-e e CT-e)
- **document_items**: Itens dos documentos

## 🧪 Testando com Exemplos

O projeto inclui XMLs de exemplo na pasta `samples/`:

1. Teste com uma NF-e:
```bash
python fiscal.py process samples/sample_nfe.xml
```

2. Teste com um CT-e:
```bash
python fiscal.py process samples/sample_cte.xml
```

3. Busque os dados importados:
```bash
python fiscal.py search-clients "CLIENTE"
python fiscal.py search-products "NOTEBOOK"
```

## 📝 Tipos de Documentos Suportados

### NF-e (Nota Fiscal Eletrônica)
- Modelo 55
- Extrai: emitente, destinatário, produtos, valores, impostos

### CT-e (Conhecimento de Transporte Eletrônico)
- Modelo 57
- Extrai: transportadora, remetente, destinatário, valores de frete

## 🛠️ Tecnologias

- **Python 3**: Linguagem principal
- **lxml**: Parser XML robusto
- **SQLite**: Banco de dados embutido

## 📄 Licença

Este projeto está sob licença MIT.

## 👨‍💻 Autor

aviladevs