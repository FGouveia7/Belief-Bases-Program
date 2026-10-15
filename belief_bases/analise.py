"""Coordenação dos algoritmos sem entrada ou saída de terminal."""

from collections.abc import Sequence

from z3 import BoolRef

from .contracoes.agm import calcula_AGM
from .contracoes.kernel import calcular_kernel
from .contracoes.limitada import filtrar_por_limite
from .contracoes.partial_meet import calcular_full_meet, calcular_partial_meet
from .contracoes.smooth_kernel import calcula_smooth_kernel
from .deducao import criar_verificador_deducao
from .modelos import FamiliaConjuntos, ResultadoAnalise
from .operacoes_conjuntos import remove_duplicados
from .subconjuntos import calcula_partes_dos_maximais, classificar_subconjuntos


def analisar_contracao(
    premissas: Sequence[BoolRef], formula_alvo: BoolRef
) -> ResultadoAnalise:
    """Calcula famílias reutilizando partes, classificação e inferência.

    Uma consulta por parte classifica o alvo. A cache dura só esta análise;
    apresentação e seleção posterior de B usam os resultados calculados.
    """
    base = remove_duplicados(premissas)
    verificar = criar_verificador_deducao()
    kernels, remainders = classificar_subconjuntos(base, formula_alvo, verificar)
    deduz = verificar(base, formula_alvo)
    eh_tautologia = verificar([], formula_alvo)
    partial_meet = calcular_partial_meet(base, remainders)
    full_meet = calcular_full_meet(base, remainders)
    partes = calcula_partes_dos_maximais(remainders) if remainders else [list(base)]
    kernel = calcular_kernel(base, full_meet, partes)
    smooth_kernel = calcula_smooth_kernel(base, kernel, verificar=verificar)
    agm = calcula_AGM(base, partes, formula_alvo, verificar=verificar)
    return ResultadoAnalise(
        premissas=base,
        formula_alvo=formula_alvo,
        deduz=deduz,
        eh_tautologia=eh_tautologia,
        kernels=kernels,
        remainders=remainders,
        partial_meet=partial_meet,
        full_meet=full_meet,
        contracoes_base=partes,
        kernel=kernel,
        smooth_kernel=smooth_kernel,
        agm=agm,
    )


def analisar_limite(
    resultado: ResultadoAnalise, limite_inferior: Sequence[BoolRef]
) -> FamiliaConjuntos:
    """Resultados limitados por B usando apenas as partes já calculadas."""
    return filtrar_por_limite(
        resultado.premissas, limite_inferior, resultado.contracoes_base
    )
