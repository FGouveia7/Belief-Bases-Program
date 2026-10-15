"""Partial meet e full meet a partir de remainders já calculados (§3.4)."""

from collections.abc import Sequence

from z3 import BoolRef

from ..modelos import ConjuntoFormulas, FamiliaConjuntos
from ..operacoes_conjuntos import (
    interseta_varios_conjuntos,
    remove_duplicados,
    todas_intersecoes_maximais,
)


def calcular_partial_meet(
    premissas: Sequence[BoolRef], remainders: Sequence[Sequence[BoolRef]]
) -> FamiliaConjuntos:
    """Interseções de todas as seleções não vazias; [A] sem remainders."""
    return sorted(
        todas_intersecoes_maximais(premissas, remainders), key=len, reverse=True
    )


def calcular_full_meet(
    premissas: Sequence[BoolRef], remainders: Sequence[Sequence[BoolRef]]
) -> ConjuntoFormulas:
    """Interseção de todos os remainders; A no caso sem remainders."""
    if not remainders:
        return remove_duplicados(premissas)
    return interseta_varios_conjuntos(remainders)
