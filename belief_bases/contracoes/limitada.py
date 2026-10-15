"""Contração limitada: B ⊆ C ⊆ X para algum remainder X (§3.5)."""

from collections.abc import Sequence

from z3 import BoolRef

from ..modelos import FamiliaConjuntos
from ..operacoes_conjuntos import esta_contido, remove_duplicados
from ..subconjuntos import calcula_partes_dos_maximais, encontrar_remainders


def filtrar_por_limite(
    premissas: Sequence[BoolRef],
    limite_inferior: Sequence[BoolRef],
    partes_remainders: Sequence[Sequence[BoolRef]],
) -> FamiliaConjuntos:
    """Filtra candidatos existentes, sem inferência; recebe [A] na tautologia."""
    if not esta_contido(limite_inferior, premissas):
        raise ValueError(
            "O subconjunto introduzido tem de ser um subconjunto do conjunto inicial."
        )
    return [
        list(candidato)
        for candidato in partes_remainders
        if esta_contido(limite_inferior, candidato)
    ]


def encontrar_contracoes_limitadas(
    conjunto_inicial: Sequence[BoolRef],
    subconjunto_utilizador: Sequence[BoolRef],
    formula: BoolRef,
) -> FamiliaConjuntos:
    """Calcula resultados limitados por B; nenhum se B implica alvo não tautológico."""
    if not esta_contido(subconjunto_utilizador, conjunto_inicial):
        raise ValueError(
            "O subconjunto introduzido tem de ser um subconjunto do conjunto inicial."
        )
    remainders = encontrar_remainders(conjunto_inicial, formula)
    partes = (
        calcula_partes_dos_maximais(remainders)
        if remainders
        else [remove_duplicados(conjunto_inicial)]
    )
    return filtrar_por_limite(conjunto_inicial, subconjunto_utilizador, partes)


def encontra_subconjuntos_maximais_com_subconjunto(
    conjunto_inicial: Sequence[BoolRef],
    subconjunto_utilizador: Sequence[BoolRef],
    formula: BoolRef,
) -> FamiliaConjuntos:
    """Nome legado de encontrar_contracoes_limitadas; não calcula maximais."""
    return encontrar_contracoes_limitadas(
        conjunto_inicial, subconjunto_utilizador, formula
    )
