"""Conjuntos estruturais de BoolRef representados por listas ordenadas.

Pertença usa ``formula.eq(outra)``: igualdade da árvore Z3. Equivalência
lógica exige inferência e não identifica elementos de uma base. Repetições
não têm multiplicidade; preserva-se a ordem da primeira ocorrência.
"""

from collections.abc import Iterable, Sequence
from itertools import combinations

from z3 import BoolRef

from .modelos import ConjuntoFormulas, FamiliaConjuntos


def pertence(formula: BoolRef, conjunto: Iterable[BoolRef]) -> bool:
    """Pertença estrutural sem converter fórmulas Z3 em bool Python."""
    return any(formula.eq(elemento) for elemento in conjunto)


def remove_duplicados(conjunto: Iterable[BoolRef]) -> ConjuntoFormulas:
    """Remove repetições estruturais, preservando a primeira ocorrência."""
    resultado: ConjuntoFormulas = []
    for formula in conjunto:
        if not pertence(formula, resultado):
            resultado.append(formula)
    return resultado


def esta_contido(
    subconjunto_menor: Iterable[BoolRef], conjunto_maior: Sequence[BoolRef]
) -> bool:
    """Inclusão estrutural, incluindo o conjunto vazio."""
    return all(pertence(formula, conjunto_maior) for formula in subconjunto_menor)


def conjuntos_sao_iguais(
    conjunto_a: Sequence[BoolRef], conjunto_b: Sequence[BoolRef]
) -> bool:
    """Igualdade independente de ordem e repetições, nas duas direções."""
    return esta_contido(conjunto_a, conjunto_b) and esta_contido(conjunto_b, conjunto_a)


def interseta_varios_conjuntos(
    lista_de_conjuntos: Sequence[Iterable[BoolRef]],
) -> ConjuntoFormulas:
    """Interseção estrutural; uma família vazia devolve [].

    A interseção vazia depende do universo. Os operadores de contração
    tratam explicitamente a seleção {A} quando não há remainders.
    """
    if not lista_de_conjuntos:
        return []
    resultado = remove_duplicados(lista_de_conjuntos[0])
    for conjunto in lista_de_conjuntos[1:]:
        elementos = list(conjunto)
        resultado = [formula for formula in resultado if pertence(formula, elementos)]
    return resultado


def remove_conjuntos_duplicados(
    conjuntos: Iterable[Iterable[BoolRef]],
) -> FamiliaConjuntos:
    """Normaliza uma família, preservando a ordem dos conjuntos distintos."""
    resultado: FamiliaConjuntos = []
    for conjunto in conjuntos:
        normalizado = remove_duplicados(conjunto)
        if not any(conjuntos_sao_iguais(normalizado, outro) for outro in resultado):
            resultado.append(normalizado)
    return resultado


def todas_intersecoes_maximais(
    conjunto_inicial: Sequence[BoolRef], maximais: Sequence[Iterable[BoolRef]]
) -> FamiliaConjuntos:
    """Interseções de seleções não vazias de remainders (§3.4).

    Sem remainders devolve [A]. Um remainder vazio é um membro legítimo
    da família e a sua interseção é vazia, nunca A.
    """
    if not maximais:
        return [remove_duplicados(conjunto_inicial)]
    remainders = remove_conjuntos_duplicados(maximais)
    return remove_conjuntos_duplicados(
        interseta_varios_conjuntos(grupo)
        for tamanho in range(1, len(remainders) + 1)
        for grupo in combinations(remainders, tamanho)
    )
