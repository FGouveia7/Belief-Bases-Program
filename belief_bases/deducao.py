"""Consequência clássica por refutação e cache local de consultas."""

from collections.abc import Sequence

from z3 import BoolRef, Not, Solver, unknown, unsat

from .modelos import ConjuntoFormulas, VerificadorDeducao


class ErroDeducao(RuntimeError):
    """O solver não decidiu uma consulta; não significa falsidade."""


def verifica_deducao(
    conjunto_premissas: Sequence[BoolRef], formula_alvo: BoolRef
) -> bool:
    """Testa A ⊢ α pela insatisfazibilidade de A ∪ {¬α} (§3.2)."""
    solver = Solver(ctx=formula_alvo.ctx)
    solver.add(*conjunto_premissas, Not(formula_alvo))
    resultado = solver.check()
    if resultado == unknown:
        raise ErroDeducao(f"Z3 could not decide the query: {solver.reason_unknown()}")
    return resultado == unsat


def elementos_deduziveis(
    conjunto_a: Sequence[BoolRef], conjunto_b: Sequence[BoolRef]
) -> ConjuntoFormulas:
    """Elementos de A dedutíveis de B, pela ordem original de A."""
    return [formula for formula in conjunto_a if verifica_deducao(conjunto_b, formula)]


def criar_verificador_deducao() -> VerificadorDeducao:
    """Cache privada de uma análise, sem estado global ou aproximação.

    IDs de AST são estruturais dentro de um contexto Z3. Retêm-se as
    referências para impedir a reutilização de IDs de fórmulas temporárias.
    """
    cache: dict[tuple, bool] = {}
    referencias: list[tuple[tuple[BoolRef, ...], BoolRef]] = []

    def verificar(premissas: Sequence[BoolRef], alvo: BoolRef) -> bool:
        chave = (
            id(alvo.ctx),
            alvo.get_id(),
            frozenset((id(formula.ctx), formula.get_id()) for formula in premissas),
        )
        if chave not in cache:
            cache[chave] = verifica_deducao(premissas, alvo)
            referencias.append((tuple(premissas), alvo))
        return cache[chave]

    return verificar
