
from pathlib import Path
import pandas as pd


# ============================================================
# 1. CONFIGURACAO DO PROJETO
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_VIAGENS = PASTA_PROJETO / "2026_Viagem.csv"
PASTA_RESULTADOS = PASTA_PROJETO / "resultados"

COLUNA_ID = "Identificador do processo de viagem"
COLUNA_NOME = "Nome"
COLUNA_CARGO = "Cargo"
COLUNA_SITUACAO = "Situação"

COLUNAS_VALORES = [
    "Valor diárias",
    "Valor passagens",
    "Valor devolução",
    "Valor outros gastos",
]

CATEGORIAS_SEM_IDENTIFICACAO = {
    "",
    "sem informação",
    "informações protegidas por sigilo",
    "<na>",
    "nan",
}


# ============================================================
# 2. FUNCOES DE PREPARACAO DOS DADOS
# ============================================================

def converter_moeda(coluna):
    """
    Converte valores monetarios brasileiros para numeros.

    Exemplo:
    '5.927,18' -> 5927.18
    '107,83'   -> 107.83
    """

    texto = (
        coluna.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    # Remove o separador de milhar
    texto = texto.str.replace(".", "", regex=False)

    # Troca a virgula decimal por ponto
    texto = texto.str.replace(",", ".", regex=False)

    return pd.to_numeric(texto, errors="coerce")


def carregar_dados():
    """Carrega o CSV e prepara os campos para analise."""

    if not ARQUIVO_VIAGENS.is_file():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {ARQUIVO_VIAGENS}"
        )

    print("\nCarregando a base de viagens...")
    print("Isso pode levar alguns segundos.")

    df = pd.read_csv(
        ARQUIVO_VIAGENS,
        sep=";",
        encoding="Windows-1252",
        low_memory=False,
    )

    print("Arquivo carregado com sucesso!")

    # Confere se as colunas essenciais existem
    colunas_obrigatorias = [
        COLUNA_ID,
        COLUNA_NOME,
        COLUNA_CARGO,
        COLUNA_SITUACAO,
        "Período - Data de início",
        "Período - Data de fim",
        *COLUNAS_VALORES,
    ]

    faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Colunas nao encontradas: {faltantes}"
        )

    # Limpa espacos dos campos de texto
    colunas_texto = [
        COLUNA_NOME,
        COLUNA_CARGO,
        COLUNA_SITUACAO,
        "Nome órgão superior",
        "Nome órgão solicitante",
        "Destinos",
        "Motivo",
    ]

    for coluna in colunas_texto:
        if coluna in df.columns:
            df[coluna] = (
                df[coluna]
                .astype("string")
                .str.strip()
            )

    # Converte os campos monetarios
    for coluna in COLUNAS_VALORES:
        df[coluna] = converter_moeda(df[coluna])

    # Converte os campos de data
    for coluna in [
        "Período - Data de início",
        "Período - Data de fim",
    ]:
        df[coluna] = pd.to_datetime(
            df[coluna],
            dayfirst=True,
            errors="coerce",
        )

    return df


# ============================================================
# 3. FILTROS E INDICADORES
# ============================================================

def selecionar_realizadas(df):
    """Seleciona registros cuja situacao e Realizada."""

    situacao = (
        df[COLUNA_SITUACAO]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    return df.loc[situacao.eq("realizada").fillna(False)].copy()


def nome_identificado(serie):
    """Identifica nomes que nao sao descricoes genericas."""

    normalizado = (
        serie.astype("string")
        .str.strip()
        .str.casefold()
    )

    return (
        normalizado.notna()
        & ~normalizado.isin(CATEGORIAS_SEM_IDENTIFICACAO)
    )


def mostrar_resumo(df):
    """Exibe indicadores gerais da base."""

    realizadas = selecionar_realizadas(df)

    print("\n" + "=" * 60)
    print("RESUMO DA BASE DE VIAGENS")
    print("=" * 60)

    print(f"Total de registros: {len(df):,}")
    print(
        "Processos distintos na base:",
        df[COLUNA_ID].nunique(),
    )
    print(
        "Registros com situacao Realizada:",
        len(realizadas),
    )

    print("\nRegistros por situacao:")
    print(df[COLUNA_SITUACAO].value_counts(dropna=False).to_string())

    inicio = df["Período - Data de início"].min()
    fim = df["Período - Data de fim"].max()

    print("\nPeriodo encontrado nos dados:")
    print(f"Data inicial: {inicio}")
    print(f"Data final:   {fim}")


# ============================================================
# 4. RANKING DE CARGOS
# ============================================================

def ranking_cargos(df, limite=10):
    realizadas = selecionar_realizadas(df)

    # Exclui cargos vazios ou genericos
    filtro = nome_identificado(realizadas[COLUNA_CARGO])

    base = realizadas.loc[filtro]

    ranking = (
        base.groupby(COLUNA_CARGO)[COLUNA_ID]
        .nunique()
        .sort_values(ascending=False)
        .head(limite)
    )

    print("\nTOP CARGOS COM MAIS PROCESSOS REALIZADOS")
    print(ranking.to_string())

    return ranking


# ============================================================
# 5. RANKING DE PESSOAS
# ============================================================

def ranking_pessoas(df, limite=10):
    realizadas = selecionar_realizadas(df)

    filtro_nome = nome_identificado(realizadas[COLUNA_NOME])
    filtro_cargo = nome_identificado(realizadas[COLUNA_CARGO])

    base = realizadas.loc[filtro_nome & filtro_cargo]

    ranking = (
        base.groupby([COLUNA_NOME, COLUNA_CARGO])[COLUNA_ID]
        .nunique()
        .sort_values(ascending=False)
        .head(limite)
    )

    print("\nTOP PESSOAS COM MAIS PROCESSOS REALIZADOS")
    print(ranking.to_string())

    return ranking


# ============================================================
# 6. PESQUISA DE UMA PESSOA
# ============================================================

def pesquisar_pessoa(df):
    termo = input(
        "\nDigite o nome completo ou parte do nome: "
    ).strip()

    if not termo:
        print("Digite algum nome para pesquisar.")
        return

    # Busca parcial, ignorando maiusculas e minusculas
    nomes = df[COLUNA_NOME].astype("string")

    encontrados = df.loc[
        nomes.str.contains(
            termo,
            case=False,
            na=False,
            regex=False,
        )
    ].copy()

    if encontrados.empty:
        print("Nenhuma pessoa encontrada.")
        return

    # Nao considera descricoes genericas como pessoas
    filtro = nome_identificado(encontrados[COLUNA_NOME])
    encontrados = encontrados.loc[filtro]

    if encontrados.empty:
        print("A busca retornou apenas nomes nao identificados.")
        return

    print("\nPessoas encontradas:")
    pessoas = (
        encontrados[[COLUNA_NOME, COLUNA_CARGO]]
        .drop_duplicates()
        .head(30)
    )
    print(pessoas.to_string(index=False))

    # Mantem somente registros de situacao Realizada
    realizadas = selecionar_realizadas(encontrados)

    print(
        "\nQuantidade de registros encontrados:",
        len(encontrados),
    )
    print(
        "Processos distintos realizados:",
        realizadas[COLUNA_ID].nunique(),
    )

    print("\nValores registrados nos processos realizados:")

    for coluna in COLUNAS_VALORES:
        total = realizadas[coluna].sum(min_count=1)

        if pd.isna(total):
            total = 0.0

        print(f"{coluna}: R$ {total:,.2f}")

    # Exibe os detalhes sem mostrar CPF
    colunas_exibicao = [
        COLUNA_ID,
        "Número da Proposta (PCDP)",
        COLUNA_NOME,
        COLUNA_CARGO,
        "Nome órgão solicitante",
        "Período - Data de início",
        "Período - Data de fim",
        "Destinos",
        "Motivo",
        *COLUNAS_VALORES,
        COLUNA_SITUACAO,
    ]

    colunas_exibicao = [
        coluna
        for coluna in colunas_exibicao
        if coluna in realizadas.columns
    ]

    print("\nDetalhes dos processos realizados:")

    print(
        realizadas[colunas_exibicao]
        .sort_values("Período - Data de início")
        .tail(30)
        .to_string(index=False)
    )

    print(
        "\nExibindo ate 30 registros. "
        "Os totais consideram todos os registros encontrados."
    )


# ============================================================
# 7. EXPORTACAO DOS RANKINGS
# ============================================================

def exportar_rankings(df):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    cargos = ranking_cargos(df, limite=100)
    pessoas = ranking_pessoas(df, limite=100)

    # Exporta somente dados agregados, sem CPF
    cargos.rename("Quantidade de processos").to_csv(
        PASTA_RESULTADOS / "ranking_cargos.csv",
        encoding="utf-8-sig",
    )

    pessoas.rename("Quantidade de processos").to_csv(
        PASTA_RESULTADOS / "ranking_pessoas.csv",
        encoding="utf-8-sig",
    )

    print("\nRankings exportados para:")
    print(PASTA_RESULTADOS)


# ============================================================
# 8. MENU PRINCIPAL
# ============================================================

def main():
    try:
        df = carregar_dados()
    except (FileNotFoundError, ValueError, UnicodeDecodeError) as erro:
        print(f"\nErro ao carregar os dados: {erro}")
        return

    while True:
        print("\n" + "=" * 60)
        print("ANALISE DE VIAGENS PUBLICAS - PORTAL DA TRANSPARENCIA")
        print("=" * 60)
        print("1 - Resumo da base")
        print("2 - Ranking de cargos")
        print("3 - Ranking de pessoas")
        print("4 - Pesquisar pessoa e consultar gastos")
        print("5 - Exportar rankings para CSV")
        print("0 - Sair")

        opcao = input("\nEscolha uma opcao: ").strip()

        if opcao == "1":
            mostrar_resumo(df)

        elif opcao == "2":
            ranking_cargos(df)

        elif opcao == "3":
            ranking_pessoas(df)

        elif opcao == "4":
            pesquisar_pessoa(df)

        elif opcao == "5":
            exportar_rankings(df)

        elif opcao == "0":
            print("Programa encerrado.")
            break

        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    main()
