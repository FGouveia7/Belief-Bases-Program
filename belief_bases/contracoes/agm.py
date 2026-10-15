"""Basic AGM-generated base contraction (Observação 5 e §3.9)."""

from collections.abc import Sequence

from z3 import BoolRef, Or

from ..deducao import verifica_deducao
from ..modelos import FamiliaConjuntos, VerificadorDeducao
from ..operacoes_conjuntos import pertence, remove_duplicados


def verifica_condicao_AGM(
    conjunto_inicial: Sequence[BoolRef],
    conjunto_b: Sequence[BoolRef],
    formula_inicial: BoolRef,
    *,
    verificar: VerificadorDeducao = verifica_deducao,
) -> bool:
    """Eliminação disjuntiva; este predicado isolado não impõe vacuidade."""
    return all(
        pertence(elemento, conjunto_b)
        or not verificar(conjunto_b, Or(formula_inicial, elemento))
        for elemento in conjunto_inicial
    )


def calcula_AGM(
    conjunto_inicial: Sequence[BoolRef],
    partes_pre_kernel: Sequence[Sequence[BoolRef]],
    formula_inicial: BoolRef,
    *,
    verificar: VerificadorDeducao = verifica_deducao,
) -> FamiliaConjuntos:
    """Aplica vacuidade e filtra candidatos por eliminação disjuntiva.

    Observação 5 (p. 8): se A não implica α, só A é possível. O §3.9
    omitia este caso e aceitava remoções arbitrárias, como ∅ para A={p}, α=q.
    """
    if not verificar(conjunto_inicial, formula_inicial):
        return [remove_duplicados(conjunto_inicial)]
    return [
        list(candidato)
        for candidato in partes_pre_kernel
        if verifica_condicao_AGM(
            conjunto_inicial, candidato, formula_inicial, verificar=verificar
        )
    ]
