"""Kernel como contração limitada pelo full meet (Observação 3, §3.7)."""

from collections.abc import Sequence

from z3 import BoolRef

from ..modelos import FamiliaConjuntos
from .limitada import filtrar_por_limite


def calcular_kernel(
    premissas: Sequence[BoolRef],
    full_meet: Sequence[BoolRef],
    partes_remainders: Sequence[Sequence[BoolRef]],
) -> FamiliaConjuntos:
    """Candidatos que contêm o full meet, sem recalcular partes."""
    return filtrar_por_limite(premissas, full_meet, partes_remainders)
