"""Coordenação da sessão e das ações de menu, sem algoritmos matemáticos."""

from collections.abc import Mapping, Sequence

from colorama import Fore, Style
from z3 import BoolRef

from belief_bases.analise import analisar_contracao, analisar_limite
from belief_bases.cli.apresentacao import (
    formata_conjunto,
    formata_conjunto_a,
    mostrar_conjunto_a,
    mostrar_lista_conjuntos,
    mostrar_premissas,
    mostrar_resultados,
    mostrar_sintaxe,
)
from belief_bases.cli.entrada import (
    ler_formula_alvo,
    ler_subconjunto_por_indices,
    pedir_com_retry,
    pedir_dados_iniciais_com_retry,
)
from belief_bases.modelos import ResultadoAnalise


def perguntar_proximo_passo(
    premissas: Sequence[BoolRef], permitir_opcao_b: bool = True
) -> str:
    """Lê uma ação válida, respeitando o caso especial de tautologias."""
    print()
    while True:
        texto = (
            Style.BRIGHT
            + "Choose an option:\n"
            + "  (1) Contract another sentence using the same set A\n"
            + f"      {formata_conjunto_a(premissas)}\n"
        )
        if permitir_opcao_b:
            texto += (
                "  (2) Possible outcomes of a bounded contraction with lower-bound B\n"
            )
        else:
            texto += "  Note: option 2 is not available - the sentence is a tautology\n"
        texto += "  (3) Start with a new set\n" + "  (0) Exit\n" + "Selected option: "
        resposta = input(texto).strip()
        opcoes = {"1": "formula", "3": "novo", "0": "sair"}
        if permitir_opcao_b:
            opcoes["2"] = "ab"
        if resposta in opcoes:
            return opcoes[resposta]
        if resposta == "2" and not permitir_opcao_b:
            print(
                Fore.RED
                + "Option 2 is not available: the target sentence is a tautology, "
                + "so the bounded contraction outcome is always A "
                + "(already shown above)."
            )
        else:
            print(Fore.RED + "Invalid option. Please choose a valid option.")


def contrair_formula(
    contexto: Mapping[str, BoolRef], premissas: Sequence[BoolRef]
) -> ResultadoAnalise:
    """Lê um alvo, calcula uma vez e apresenta a análise da ronda."""
    formula = pedir_com_retry(ler_formula_alvo, contexto, max_tentativas=None)
    resultado = analisar_contracao(premissas, formula)
    mostrar_resultados(resultado)
    return resultado


def mostrar_contracao_limitada(resultado: ResultadoAnalise) -> None:
    """Seleciona B e usa os resultados já calculados para o alvo corrente."""
    mostrar_premissas(resultado.premissas)
    limite = pedir_com_retry(
        ler_subconjunto_por_indices, resultado.premissas, "B", max_tentativas=None
    )
    conjuntos = analisar_limite(resultado, limite)
    print(Style.BRIGHT + "---Result---")
    mostrar_lista_conjuntos(
        "Possible outcomes of a bounded contraction with a lower-bound "
        + f"B = {formata_conjunto(limite)}:",
        conjuntos,
    )


def menu_interativo() -> None:
    """Executa a sessão e conserva uma análise por par base/fórmula alvo."""
    mostrar_sintaxe()
    contexto, premissas = pedir_dados_iniciais_com_retry()
    mostrar_conjunto_a(premissas)
    while True:
        resultado = contrair_formula(contexto, premissas)
        escolha = perguntar_proximo_passo(premissas, not resultado.eh_tautologia)
        while escolha == "ab":
            mostrar_contracao_limitada(resultado)
            escolha = perguntar_proximo_passo(premissas, not resultado.eh_tautologia)
        if escolha == "sair":
            return
        if escolha == "novo":
            print()
            contexto, premissas = pedir_dados_iniciais_com_retry()
        mostrar_conjunto_a(premissas)
