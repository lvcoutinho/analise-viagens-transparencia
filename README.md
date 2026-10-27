# Análise de Viagens — Portal da Transparência

Projeto desenvolvido em Python para analisar dados públicos de viagens, utilizando Pandas para tratamento, organização e análise dos dados.

## Objetivo

Explorar informações sobre viagens registradas no Portal da Transparência, identificando padrões e gerando indicadores que facilitem a consulta e a análise dos gastos públicos.

## Funcionalidades

- Leitura de arquivos CSV com Pandas.
- Tratamento e conversão de valores monetários.
- Conversão e organização de datas.
- Análise das situações das viagens.
- Ranking de cargos com maior número de registros.
- Ranking de pessoas com maior número de viagens.
- Pesquisa por nome.
- Cálculo de despesas registradas nas colunas de valores.
- Exportação de rankings para arquivos, conforme as opções disponíveis no programa.

## Tecnologias utilizadas

- Python
- Pandas
- CSV
- Git e GitHub

## Estrutura do projeto

```text
analise-viagens-transparencia/
├── srv/
│   └── analise.py
├── .gitignore
└── README.md
```

O arquivo `2026_Viagem.csv` deve ficar na pasta principal do projeto durante a execução local, mas não precisa ser enviado ao GitHub.

## Como executar

### 1. Pré-requisitos

Instale o Python e o Git.

### 2. Clone o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
cd analise-viagens-transparencia
```

### 3. Crie um ambiente virtual

No Windows:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Disponibilize o arquivo CSV

Obtenha o arquivo de dados na fonte oficial utilizada no projeto e coloque-o na pasta principal, respeitando o nome esperado pelo código:

`2026_Viagem.csv`

Confira as regras de uso e redistribuição da fonte antes de compartilhar os dados.

### 6. Execute a análise

```bash
python srv/analise.py
```

Siga as opções apresentadas no menu do programa.

## Fonte dos dados

Os dados são referentes a registros públicos de viagens e despesas governamentais. Consulte o Portal da Transparência para localizar a base correspondente ao período analisado.

## Aprendizados

Este projeto faz parte dos meus estudos de Python e análise de dados, com foco em:

- Manipulação de dados com Pandas.
- Limpeza e padronização de informações.
- Análise exploratória de dados.
- Filtros, agrupamentos e ordenação.
- Tratamento de valores monetários.
- Organização de projetos e versionamento com Git.

## Autor

Levi Coutinho Santos

Projeto desenvolvido para fins de estudo e portfólio profissional.
