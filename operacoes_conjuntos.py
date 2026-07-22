# operacoes_conjuntos.py
from itertools import combinations


def interseta_varios_conjuntos(lista_de_conjuntos: list) -> list:
    """
    Calcula a interseção de vários conjuntos de expressões Z3.

    A comparação entre elementos usa `.eq()` em vez dos operadores normais
    porque os elementos são expressões Z3 (BoolRef): os operadores
    `==`/`!=` nesses objetos constroem novas expressões lógicas, não
    devolvem um booleano.

    Args:
        lista_de_conjuntos: lista de conjuntos (cada um, uma lista/set de
            expressões Z3) a intersetar.

    Returns:
        Lista com os elementos comuns a todos os conjuntos. Lista vazia
        se `lista_de_conjuntos` estiver vazia.
    """
    if not lista_de_conjuntos:
        return []
    
    resultado = list(lista_de_conjuntos[0])
    
    for outro_conjunto in lista_de_conjuntos[1:]:
        novo_resultado = []
        for item in resultado:
            if any(item.eq(item_do_outro_conjunto) for item_do_outro_conjunto in outro_conjunto):
                novo_resultado.append(item)
        resultado = novo_resultado
        
    return resultado


def conjuntos_sao_iguais(conjunto_a: list, conjunto_b: list) -> bool:
    """
    Verifica se dois conjuntos de expressões Z3 têm exatamente os mesmos
    elementos, independentemente da ordem.

    Args:
        conjunto_a: primeiro conjunto a comparar.
        conjunto_b: segundo conjunto a comparar.

    Returns:
        True se ambos os conjuntos tiverem o mesmo tamanho e cada
        elemento de `conjunto_a` existir em `conjunto_b`, False caso
        contrário.
    """
    if len(conjunto_a) != len(conjunto_b):
        return False
    return all(
        any(item_a.eq(item_b) for item_b in conjunto_b)
        for item_a in conjunto_a
    )


def todas_intersecoes_maximais(conjunto_inicial: list, maximais: list) -> list:
    """
    Calcula todas as interseções distintas entre combinações dos
    subconjuntos maximais (que não deduzem a fórmula alvo).

    Para cada tamanho de combinação (de 1 até ao número total de
    maximais), calcula a interseção de cada grupo de maximais e guarda-a
    se ainda não tiver sido encontrada uma interseção igual.

    Se não existirem subconjuntos maximais (ou o único maximal for o
    conjunto vazio), significa que qualquer subconjunto prova a fórmula;
    nesse caso devolve-se o conjunto inicial de premissas.

    Args:
        conjunto_inicial: conjunto original de premissas.
        maximais: lista de subconjuntos maximais que não deduzem a
            fórmula alvo.

    Returns:
        Lista de interseções distintas encontradas entre os maximais
        (ou o conjunto inicial de premissas, no caso trivial descrito
        acima).
    """
    if not maximais or maximais == [set()] or maximais == [{}]:
        return [conjunto_inicial]

    todas_as_intersecoes = []
    
    for tamanho_combinacao in range(1, len(maximais) + 1):
        for grupo_de_maximais in combinations(maximais, tamanho_combinacao):
            intersecao_atual = interseta_varios_conjuntos(grupo_de_maximais)
            eh_duplicado = any(
                conjuntos_sao_iguais(intersecao_atual, intersecao_ja_existente)
                for intersecao_ja_existente in todas_as_intersecoes
            )
            
            if not eh_duplicado:
                todas_as_intersecoes.append(intersecao_atual)
                
    return todas_as_intersecoes
