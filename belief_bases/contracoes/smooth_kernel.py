"""Smooth kernel por fecho relativo: A ∩ Cn(C) ⊆ C (§3.8)."""

from collections.abc import Sequence

from z3 import BoolRef

from ..deducao import verifica_deducao
from ..modelos import FamiliaConjuntos, VerificadorDeducao
from ..operacoes_conjuntos import pertence


def verifica_condicao_smooth(
    conjunto_inicial: Sequence[BoolRef],
    subconjunto: Sequence[BoolRef],
    *,
    verificar: VerificadorDeducao = verifica_deducao,
) -> bool:
    """Rejeita candidatos que ainda deduzem uma crença removida de A."""
    return all(
        pertence(formula, subconjunto) or not verificar(subconjunto, formula)
        for formula in conjunto_inicial
    )


def calcula_smooth_kernel(
    conjunto_inicial: Sequence[BoolRef],
    kernel: Sequence[Sequence[BoolRef]],
    *,
    verificar: VerificadorDeducao = verifica_deducao,
) -> FamiliaConjuntos:
    """Filtra resultados kernel pelo postulado de fecho relativo."""
    return [
        list(candidato)
        for candidato in kernel
        if verifica_condicao_smooth(conjunto_inicial, candidato, verificar=verificar)
    ]
