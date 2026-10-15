"""Tipos partilhados e resultados de uma análise."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TypeAlias

from z3 import BoolRef

ConjuntoFormulas: TypeAlias = list[BoolRef]
FamiliaConjuntos: TypeAlias = list[ConjuntoFormulas]
VerificadorDeducao: TypeAlias = Callable[[Sequence[BoolRef], BoolRef], bool]


@dataclass(eq=False)
class ResultadoAnalise:
    """Resultados para um par base/alvo, sem igualdade automática de BoolRef.

    Listas representam conjuntos estruturais, sem duplicados. A igualdade
    automática de dataclasses seria inadequada para expressões simbólicas.
    """

    premissas: ConjuntoFormulas
    formula_alvo: BoolRef
    deduz: bool
    eh_tautologia: bool
    kernels: FamiliaConjuntos
    remainders: FamiliaConjuntos
    partial_meet: FamiliaConjuntos
    full_meet: ConjuntoFormulas
    contracoes_base: FamiliaConjuntos
    kernel: FamiliaConjuntos
    smooth_kernel: FamiliaConjuntos
    agm: FamiliaConjuntos
