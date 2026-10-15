"""Partes e extremos por inclusão de bases finitas."""

from collections.abc import Iterator, Sequence
from itertools import combinations

from z3 import BoolRef

from .deducao import verifica_deducao
from .modelos import ConjuntoFormulas, FamiliaConjuntos, VerificadorDeducao
from .operacoes_conjuntos import (
    esta_contido,
    remove_conjuntos_duplicados,
    remove_duplicados,
)


def gerar_subconjuntos(conjunto: Sequence[BoolRef]) -> Iterator[ConjuntoFormulas]:
    """Gera partes por tamanho crescente, incluindo ∅ e A."""
    base = remove_duplicados(conjunto)
    for tamanho in range(len(base) + 1):
        for combinacao in combinations(base, tamanho):
            yield list(combinacao)


def cria_partes_do_conjunto(conjunto: Sequence[BoolRef]) -> FamiliaConjuntos:
    """Materializa as 2**n partes de uma base sem repetições."""
    return list(gerar_subconjuntos(conjunto))


def _validar_modo(modo: str) -> None:
    if modo not in {"maximais", "minimais"}:
        raise ValueError("Modo inválido! Usa 'maximais' ou 'minimais'.")


def tem_subconjunto(
    subconjunto_atual: Sequence[BoolRef],
    partes_do_conjunto: Sequence[Sequence[BoolRef]],
    modo: str,
) -> bool:
    """Existe candidato maior/menor que impede ser maximal/minimal?"""
    _validar_modo(modo)
    atual = remove_duplicados(subconjunto_atual)
    for candidato in partes_do_conjunto:
        outro = remove_duplicados(candidato)
        if modo == "maximais":
            if len(outro) > len(atual) and esta_contido(atual, outro):
                return True
        elif len(outro) < len(atual) and esta_contido(outro, atual):
            return True
    return False


def filtra_conjuntos(
    subconjuntos: Sequence[Sequence[BoolRef]], modo: str = "maximais"
) -> FamiliaConjuntos:
    """Mantém extremos por inclusão, normalizando as entradas."""
    _validar_modo(modo)
    candidatos = remove_conjuntos_duplicados(subconjuntos)
    return [
        candidato
        for candidato in candidatos
        if not tem_subconjunto(candidato, candidatos, modo)
    ]


def classificar_subconjuntos(
    conjunto_premissas: Sequence[BoolRef],
    formula: BoolRef,
    verificar: VerificadorDeducao = verifica_deducao,
) -> tuple[FamiliaConjuntos, FamiliaConjuntos]:
    """Kernels e remainders com uma consulta por parte (definições 1 e 5)."""
    implicam: FamiliaConjuntos = []
    nao_implicam: FamiliaConjuntos = []
    for subconjunto in gerar_subconjuntos(conjunto_premissas):
        destino = implicam if verificar(subconjunto, formula) else nao_implicam
        destino.append(subconjunto)
    return filtra_conjuntos(implicam, "minimais"), filtra_conjuntos(nao_implicam)


def encontrar_kernels(
    conjunto_premissas: Sequence[BoolRef], formula: BoolRef
) -> FamiliaConjuntos:
    """Subconjuntos minimais que implicam o alvo (α-kernels)."""
    return classificar_subconjuntos(conjunto_premissas, formula)[0]


def encontrar_remainders(
    conjunto_premissas: Sequence[BoolRef], formula: BoolRef
) -> FamiliaConjuntos:
    """Subconjuntos maximais que não implicam o alvo."""
    return classificar_subconjuntos(conjunto_premissas, formula)[1]


def encontra_subconjuntos(
    conjunto_premissas: Sequence[BoolRef],
    formula: BoolRef,
    modo: str = "minimais_implicam",
) -> FamiliaConjuntos:
    """Compatibilidade com a API original parametrizada por modo."""
    if modo == "minimais_implicam":
        return encontrar_kernels(conjunto_premissas, formula)
    if modo == "maximais_nao_implicam":
        return encontrar_remainders(conjunto_premissas, formula)
    raise ValueError(
        "Modo inválido! Usa 'minimais_implicam' ou 'maximais_nao_implicam'."
    )


def calcula_partes_dos_maximais(
    maximais: Sequence[Sequence[BoolRef]],
) -> FamiliaConjuntos:
    """União das partes dos remainders, sem repetições."""
    return remove_conjuntos_duplicados(
        parte for maximal in maximais for parte in gerar_subconjuntos(maximal)
    )
