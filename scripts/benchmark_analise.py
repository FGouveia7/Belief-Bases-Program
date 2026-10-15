"""Mede uma análise reproduzível: python -m scripts.benchmark_analise.

Tempos são indicativos; o número de consultas evita depender da máquina.
Não se altera a inferência: apenas se contam as chamadas reais a Solver.check.
"""

import json
from time import perf_counter
from unittest.mock import patch

from z3 import Bools, Implies, Solver

from belief_bases.analise import analisar_contracao, analisar_limite


def main() -> None:
    """Analisa a mesma base de seis fórmulas usada na medição original."""
    p, q, r, s, t = Bools("p q r s t")
    premissas = [p, Implies(p, q), q, r, s, t]
    original = Solver.check
    chamadas = 0

    def contar(solver: Solver, *args, **kwargs):
        nonlocal chamadas
        chamadas += 1
        return original(solver, *args, **kwargs)

    with patch.object(Solver, "check", contar):
        inicio = perf_counter()
        resultado = analisar_contracao(premissas, q)
        duracao_analise = perf_counter() - inicio
        chamadas_analise = chamadas
        inicio = perf_counter()
        analisar_limite(resultado, [r])
        duracao_limite = perf_counter() - inicio
    print(
        json.dumps(
            {
                "premissas": len(premissas),
                "analise_chamadas_solver": chamadas_analise,
                "analise_segundos": duracao_analise,
                "limite_chamadas_solver": chamadas - chamadas_analise,
                "limite_segundos": duracao_limite,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
