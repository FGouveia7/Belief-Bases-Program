"""Apresentação dos resultados calculados, sem executar algoritmos lógicos."""

from collections.abc import Sequence

from colorama import Fore, Style
from z3 import BoolRef

from belief_bases.modelos import ResultadoAnalise
from belief_bases.parser_formulas import formata_formula, formata_lista


def formata_conjunto(conjunto: Sequence[BoolRef]) -> str:
    """Formata um conjunto de fórmulas na notação usada pelo terminal."""
    return "{" + ", ".join(formata_lista(conjunto)) + "}"


def formata_conjunto_a(premissas: Sequence[BoolRef]) -> str:
    """Formata a identificação compacta da base atual."""
    return "A = {" + ",".join(formata_formula(p) for p in premissas) + "}"


def mostrar_conjunto_a(premissas: Sequence[BoolRef]) -> None:
    """Mostra a base atual."""
    print(Style.BRIGHT + formata_conjunto_a(premissas))


def mostrar_sintaxe() -> None:
    """Mostra os operadores e a reserva da letra V."""
    linhas = (
        "Supported syntax:",
        "  ~p        -> negation (NOT p)",
        "  p & q     -> conjunction (p AND q)",
        "  p V q     -> disjunction (p OR q)",
        "  p -> q    -> implication (IF p THEN q)",
        "  p <-> q   -> equivalence (p IFF q)",
        "  ( ... )   -> parentheses for grouping",
        '  Note: the uppercase letter "V" is reserved for disjunction,',
        "        so it cannot be used as a variable name.",
    )
    for linha in linhas:
        print(Style.BRIGHT + linha)
    print()


def mostrar_lista_conjuntos(
    titulo: str, conjuntos: Sequence[Sequence[BoolRef]]
) -> None:
    """Mostra uma família de conjuntos ou a ausência de resultados."""
    print(Style.BRIGHT + "\n" + titulo)
    if not conjuntos:
        print(Fore.RED + "  none")
        return
    for conjunto in conjuntos:
        print(Fore.GREEN + f"  {formata_conjunto(conjunto)}")


def mostrar_resultados(resultado: ResultadoAnalise) -> None:
    """Apresenta uma análise pronta sem repetir inferências ou contrações."""
    print()
    print(Style.BRIGHT + "Results")
    print(Style.BRIGHT + "-------")
    conjunto_a = formata_conjunto(resultado.premissas)
    formula = formata_formula(resultado.formula_alvo)
    cor = Fore.GREEN if resultado.deduz else Fore.RED
    print(Style.BRIGHT + f"{conjunto_a} implies {formula}?: {cor}{resultado.deduz}")
    mostrar_lista_conjuntos(
        f"Kernel set of {conjunto_a} with respect to {formula}:", resultado.kernels
    )
    mostrar_lista_conjuntos(
        f"Remainders of {conjunto_a} with respect to {formula}:", resultado.remainders
    )
    mostrar_lista_conjuntos(
        "Possible outcomes of a partial meet contraction:", resultado.partial_meet
    )
    mostrar_lista_conjuntos(
        "Full meet contraction:",
        [resultado.full_meet] if resultado.partial_meet else [],
    )
    mostrar_lista_conjuntos(
        "Possible outcomes of a base contraction:", resultado.contracoes_base
    )
    mostrar_lista_conjuntos(
        "Possible outcomes of a kernel contraction:", resultado.kernel
    )
    mostrar_lista_conjuntos(
        "Possible outcomes of a smooth kernel contraction:", resultado.smooth_kernel
    )
    mostrar_lista_conjuntos(
        "Possible outcomes of a basic AGM-generated base contraction:", resultado.agm
    )
    if resultado.eh_tautologia:
        mostrar_lista_conjuntos(
            "Possible outcomes of a bounded contraction:", [resultado.premissas]
        )


def mostrar_premissas(premissas: Sequence[BoolRef]) -> None:
    """Mostra a numeração usada para selecionar o limite inferior B."""
    print(Style.BRIGHT + "\nCurrent sentences of A:")
    for indice, premissa in enumerate(premissas, start=1):
        print(Style.BRIGHT + f"  {indice}. {formata_formula(premissa)}")
    print()
