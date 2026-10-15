"""Leitura e validação de dados do terminal, sem algoritmos de contração."""

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, TypeVar

from colorama import Fore, Style
from z3 import Bool, BoolRef

from belief_bases.operacoes_conjuntos import remove_duplicados
from belief_bases.parser_formulas import (
    TOKENS_OPERADOR,
    VARIAVEL_REGEX,
    nome_variavel_valido,
    parse_formula,
    tokenizar,
    validar_nome_variavel,
)

PADRAO_VARIAVEL = VARIAVEL_REGEX
_T = TypeVar("_T")


def pedir_com_retry(
    funcao: Callable[..., _T],
    *args: Any,
    max_tentativas: int | None = 1,
    **kwargs: Any,
) -> _T:
    """Repete uma leitura que falhe por validação, sem esconder erros de código.

    A função recebida deve ler uma nova entrada em cada chamada. Erros de
    sintaxe do parser são ``ValueError`` e pertencem à mesma validação.
    ``None`` permite repetir até obter uma entrada válida ou terminar o input.
    """
    if max_tentativas is not None and max_tentativas < 1:
        raise ValueError("max_tentativas must be positive or None.")
    tentativas = 0
    while True:
        try:
            return funcao(*args, **kwargs)
        except ValueError as erro:
            tentativas += 1
            print(Fore.RED + f"Input error: {erro}")
            if max_tentativas is not None and tentativas >= max_tentativas:
                print(Fore.YELLOW + f"Too many invalid attempts ({max_tentativas}).")
                raise
            print(Fore.YELLOW + "Please try again.")


def ler_variaveis() -> list[str]:
    """Lê nomes distintos aceites pelo mesmo validador do parser."""
    entrada = input(
        Style.BRIGHT
        + "Propositional variables (separated by spaces, e.g.: p q r, or q1 q2 q3): "
    ).strip()
    nomes = entrada.split()
    if not nomes:
        raise ValueError("at least one variable must be defined.")
    for nome in nomes:
        validar_nome_variavel(nome)
    if len(set(nomes)) != len(nomes):
        raise ValueError("you cannot repeat a variable name.")
    return nomes


def inferir_variaveis(sentencas: Iterable[str]) -> list[str]:
    """Infere os identificadores das sentenças, preservando a sua ordem."""
    nomes: list[str] = []
    vistos: set[str] = set()
    for texto in sentencas:
        for token in tokenizar(texto):
            if token in TOKENS_OPERADOR or token in {"(", ")"}:
                continue
            if nome_variavel_valido(token) and token not in vistos:
                vistos.add(token)
                nomes.append(token)
    if not nomes:
        raise ValueError(
            "no propositional variables could be inferred from the sentences."
        )
    return nomes


def remover_sentencas_duplicadas(sentencas: Iterable[str]) -> list[str]:
    """Remove repetições textuais, preservando a primeira ocorrência."""
    return list(dict.fromkeys(texto.strip() for texto in sentencas))


def ler_conjunto_a() -> list[str]:
    """Lê a base A na sintaxe de lista de sentenças, mantendo o contrato legado."""
    entrada = input(
        Style.BRIGHT
        + "Enter set A as a list of sentences (for example: {p, p -> q, q, r}): "
    ).strip()
    if entrada.startswith("{") and entrada.endswith("}"):
        entrada = entrada[1:-1].strip()
    sentencas = [parte.strip() for parte in entrada.split(",") if parte.strip()]
    if not sentencas:
        raise ValueError("set A cannot be empty.")
    return remover_sentencas_duplicadas(sentencas)


def construir_contexto(nomes: Sequence[str]) -> dict[str, BoolRef]:
    """Cria as variáveis Z3 depois de validar os seus nomes."""
    if not nomes:
        raise ValueError("at least one variable must be defined.")
    for nome in nomes:
        validar_nome_variavel(nome)
    if len(set(nomes)) != len(nomes):
        raise ValueError("you cannot repeat a variable name.")
    return {nome: Bool(nome) for nome in nomes}


def ler_numero_premissas() -> int:
    """Lê o tamanho de uma base no modo de introdução individual legado."""
    texto = input(Style.BRIGHT + "Number of sentences: ").strip()
    try:
        numero = int(texto)
    except ValueError as erro:
        raise ValueError("the number of sentences only accepts integers.") from erro
    if numero < 0:
        raise ValueError("the number of sentences cannot be negative.")
    return numero


def ler_uma_premissa(contexto: Mapping[str, BoolRef], indice: int) -> BoolRef:
    """Lê e interpreta uma premissa numerada."""
    texto = input(Style.BRIGHT + f"  Sentence {indice}: ").strip()
    if not texto:
        raise ValueError("the sentence cannot be empty.")
    return parse_formula(texto, contexto)


def ler_premissas(contexto: Mapping[str, BoolRef]) -> list[BoolRef]:
    """Mantém disponível a introdução individual das premissas."""
    numero = pedir_com_retry(ler_numero_premissas)
    premissas = [
        pedir_com_retry(ler_uma_premissa, contexto, indice)
        for indice in range(1, numero + 1)
    ]
    return remove_duplicados(premissas)


def ler_formula_alvo(contexto: Mapping[str, BoolRef]) -> BoolRef:
    """Lê a fórmula a contrair no contexto da base atual."""
    texto = input(Style.BRIGHT + "Sentence to contract: ").strip()
    if not texto:
        raise ValueError("the target sentence cannot be empty.")
    return parse_formula(texto, contexto)


def ler_dados_iniciais() -> tuple[dict[str, BoolRef], list[BoolRef]]:
    """Lê, valida e normaliza uma base completa numa única tentativa."""
    sentencas = ler_conjunto_a()
    contexto = construir_contexto(inferir_variaveis(sentencas))
    premissas = remove_duplicados(
        [parse_formula(texto, contexto) for texto in sentencas]
    )
    return contexto, premissas


def pedir_dados_iniciais_com_retry() -> tuple[dict[str, BoolRef], list[BoolRef]]:
    """Volta a pedir a base inteira após uma entrada inválida."""
    return pedir_com_retry(ler_dados_iniciais, max_tentativas=None)


def ler_subconjunto_por_indices(
    premissas: Sequence[BoolRef], rotulo: str
) -> list[BoolRef]:
    """Seleciona um subconjunto por índices distintos; Enter representa vazio."""
    entrada = input(
        Style.BRIGHT
        + f"Select the lower-bound set {rotulo} to determine the possible outcome "
        + "of a bounded contraction (e.g., 1 3; press Enter to use the empty set): "
    )
    if not entrada.strip():
        return []
    try:
        indices = [int(token) for token in entrada.split()]
    except ValueError as erro:
        raise ValueError("sentence numbers only accept integers.") from erro
    if len(indices) > len(premissas):
        raise ValueError(
            f"set {rotulo} cannot have more elements ({len(indices)}) than the "
            f"initial set of sentences ({len(premissas)})."
        )
    if len(set(indices)) != len(indices):
        raise ValueError("you cannot select the same sentence number twice.")
    for indice in indices:
        if indice < 1 or indice > len(premissas):
            raise ValueError(f"there is no sentence number {indice}.")
    return [premissas[indice - 1] for indice in indices]
