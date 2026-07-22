# motor_logico.py
from z3 import *
from itertools import combinations, chain
from operacoes_conjuntos import conjuntos_sao_iguais


def verifica_deducao(conjunto_premissas: list, formula_alvo: BoolRef) -> bool:
    """
    Verifica se um conjunto de premissas deduz logicamente uma fórmula alvo.

    O teste é feito por refutação: adiciona-se a negação da fórmula alvo às
    premissas e verifica-se se o conjunto resultante é insatisfazível (unsat).
    Se for, as premissas implicam a fórmula.

    Args:
        conjunto_premissas: lista de expressões booleanas Z3 (as premissas).
        formula_alvo: expressão booleana Z3 que se quer provar.

    Returns:
        True se as premissas deduzem a fórmula alvo, False caso contrário.
    """
    s = Solver()
    for premissa in conjunto_premissas:
        s.add(premissa)
    s.add(Not(formula_alvo))
    return s.check() == unsat


def elementos_deduziveis(conjunto_a: list, conjunto_b: list) -> list:
    """
    Devolve os elementos de `conjunto_a` que são dedutíveis a partir de
    `conjunto_b`.

    Para cada elemento de `conjunto_a`, usa-o como fórmula alvo e testa
    se `conjunto_b`, sozinho (usado como conjunto de premissas), o deduz.

    Args:
        conjunto_a: conjunto (lista) de expressões Z3 a testar.
        conjunto_b: conjunto (lista) de expressões Z3 usado como premissas.

    Returns:
        Lista com os elementos de `conjunto_a` que `conjunto_b` deduz,
        pela mesma ordem em que aparecem em `conjunto_a`.
    """
    return [elemento for elemento in conjunto_a if verifica_deducao(conjunto_b, elemento)]


def cria_partes_do_conjunto(conjunto: list) -> list:
    """
    Gera o conjunto das partes (todos os subconjuntos possíveis) de uma lista.

    Inclui o conjunto vazio e o conjunto completo. O número de subconjuntos
    gerados é 2^n, onde n é o número de elementos de `conjunto`.

    Args:
        conjunto: lista de elementos (tipicamente, premissas Z3).

    Returns:
        Lista de listas, uma por cada subconjunto possível.
    """
    gerador = chain.from_iterable(combinations(conjunto, r) for r in range(len(conjunto) + 1))
    return [list(combinacao) for combinacao in gerador]


def esta_contido(subconjunto_menor: list, conjunto_maior: list) -> bool:
    """
    Verifica se todos os elementos de um subconjunto existem noutro conjunto.

    A comparação usa `.eq()` em vez dos operadores normais porque os
    elementos são expressões Z3 (BoolRef): os operadores `==`/`!=` nesses
    objetos constroem novas expressões lógicas, não devolvem um booleano.

    Args:
        subconjunto_menor: subconjunto candidato a estar contido.
        conjunto_maior: conjunto onde se procura a inclusão.

    Returns:
        True se todos os elementos de `subconjunto_menor` estão em
        `conjunto_maior`, False caso contrário.
    """
    return all(
        any(item_menor.eq(item_maior) for item_maior in conjunto_maior) 
        for item_menor in subconjunto_menor
    )


def tem_subconjunto(subconjunto_atual: list, partes_do_conjunto: list, modo: str) -> bool:
    """
    Verifica se existe, na lista de partes, outro conjunto que torne o atual
    não-maximal (modo "maximais") ou não-minimal (modo "minimais").

    Em modo "maximais": procura um conjunto maior que contenha o atual
    (o que faria do atual um subconjunto não-maximal).
    Em modo "minimais": procura um conjunto menor contido no atual
    (o que faria do atual um subconjunto não-minimal).

    Args:
        subconjunto_atual: subconjunto a testar.
        partes_do_conjunto: lista de todos os subconjuntos candidatos.
        modo: "maximais" ou "minimais".

    Returns:
        True se existir um subconjunto que desqualifique o atual como
        maximal/minimal, False caso contrário.
    """
    for subconjunto in partes_do_conjunto:
        if modo == "maximais":
            subconjunto_eh_maior = len(subconjunto) > len(subconjunto_atual)
            if subconjunto_eh_maior and esta_contido(subconjunto_atual, subconjunto):
                return True
                
        elif modo == "minimais":
            subconjunto_atual_eh_maior = len(subconjunto) < len(subconjunto_atual)
            if subconjunto_atual_eh_maior and esta_contido(subconjunto, subconjunto_atual):
                return True
                
    return False


def filtra_conjuntos(subconjuntos: list, modo: str = "maximais") -> list:
    """
    Filtra uma lista de subconjuntos, mantendo apenas os que são maximais
    ou minimais (consoante o modo), por inclusão.

    Args:
        subconjuntos: lista de subconjuntos a filtrar.
        modo: "maximais" para manter só os maximais por inclusão,
            "minimais" para manter só os minimais por inclusão.

    Returns:
        Lista dos subconjuntos que satisfazem o critério de
        maximalidade/minimalidade escolhido.
    """
    return list(filter(
        lambda subconjunto: not tem_subconjunto(subconjunto, subconjuntos, modo), 
        subconjuntos
    ))


def encontra_subconjuntos(conjunto_premissas: list, formula: BoolRef, modo: str = "minimais_implicam") -> list:
    """
    Encontra, entre todos os subconjuntos de premissas, os que satisfazem
    o critério pedido em relação à dedução de uma fórmula.

    Args:
        conjunto_premissas: lista de premissas Z3 a considerar.
        formula: fórmula alvo cuja dedução se está a testar.
        modo: "minimais_implicam" devolve os subconjuntos minimais que
            deduzem a fórmula; "maximais_nao_implicam" devolve os
            subconjuntos maximais que não a deduzem.

    Returns:
        Lista de subconjuntos (sets) que satisfazem o modo escolhido.

    Raises:
        ValueError: se `modo` não for um dos valores suportados.
    """
    partes_do_conjunto = cria_partes_do_conjunto(conjunto_premissas)

    if modo == "minimais_implicam":
        validos = list(filter(lambda sub: verifica_deducao(sub, formula), partes_do_conjunto))
        return filtra_conjuntos(validos, modo="minimais")

    elif modo == "maximais_nao_implicam":
        invalidos = list(filter(lambda sub: not verifica_deducao(sub, formula), partes_do_conjunto))
        return filtra_conjuntos(invalidos, modo="maximais")

    else:
        raise ValueError("Modo inválido! Usa 'minimais_implicam' ou 'maximais_nao_implicam'.")


def remove_duplicados(conjunto: list) -> list:
    """
    Remove elementos duplicados de um conjunto (lista de expressões Z3),
    preservando a primeira ocorrência de cada um.

    Usa `.eq()` em vez de `==`/`set()` nativo pela mesma razão documentada
    em `esta_contido`: os elementos são expressões Z3 (BoolRef).

    Args:
        conjunto: lista de expressões Z3, possivelmente com repetidos.

    Returns:
        Nova lista com os mesmos elementos, sem repetidos, na ordem em
        que apareceram pela primeira vez.
    """
    sem_duplicados = []
    for item in conjunto:
        ja_existe = any(item.eq(existente) for existente in sem_duplicados)
        if not ja_existe:
            sem_duplicados.append(item)
    return sem_duplicados


def calcula_partes_dos_maximais(maximais: list) -> list:
    """
    Calcula todas as partes (subconjuntos) de cada um dos `maximais`
    dados, combinadas numa única lista sem duplicados.

    Cada subconjunto é normalizado com `remove_duplicados` antes de ser
    comparado/adicionado: se algum `maximal` tiver, ele próprio, um
    elemento repetido (ex: a mesma premissa introduzida duas vezes),
    `cria_partes_do_conjunto` pode gerar subconjuntos como `[p, p]`, que
    é o mesmo conjunto que `[p]` mas que `conjuntos_sao_iguais` não
    reconheceria como igual (por terem tamanhos diferentes). Normalizar
    primeiro evita que isso escape à deduplicação.

    Args:
        maximais: lista de subconjuntos maximais que não implicam a
            fórmula alvo (o resultado de
            `encontra_subconjuntos(..., modo="maximais_nao_implicam")`).

    Returns:
        Lista de subconjuntos, sem duplicados, correspondente à união de
        `cria_partes_do_conjunto(maximal)` para cada maximal em
        `maximais`.
    """
    resultado = []
    for maximal in maximais:
        for subconjunto in cria_partes_do_conjunto(maximal):
            subconjunto_normalizado = remove_duplicados(subconjunto)
            ja_existe = any(conjuntos_sao_iguais(subconjunto_normalizado, existente) for existente in resultado)
            if not ja_existe:
                resultado.append(subconjunto_normalizado)
    return resultado


def encontra_subconjuntos_maximais_com_subconjunto(
    conjunto_inicial: list, subconjunto_utilizador: list, formula: BoolRef
) -> list:
    """
    Encontra todos os subconjuntos dos conjuntos maximais de `conjunto_inicial`
    que não implicam `formula`, filtrando apenas os que contêm
    `subconjunto_utilizador`.

    Processo:
      1. Calcula os subconjuntos maximais de `conjunto_inicial` que não
         deduzem `formula` (via `encontra_subconjuntos`).
      2. Calcula todas as partes desses maximais, sem duplicados (via
         `calcula_partes_dos_maximais`).
      3. Mantém apenas as partes que contêm `subconjunto_utilizador`.

    Args:
        conjunto_inicial: conjunto completo de premissas (o "A" do enunciado).
        subconjunto_utilizador: subconjunto de `conjunto_inicial` introduzido
            pelo utilizador; só interessam os resultados que o contenham.
        formula: fórmula alvo cuja dedução se está a testar.

    Returns:
        Lista de subconjuntos (sem duplicados) que:
          - são subconjuntos de algum maximal de `conjunto_inicial` que não
            implica `formula`, e
          - contêm `subconjunto_utilizador`.

        Casos especiais:
          - Se `formula` for uma tautologia (não existem maximais que não
            a implicam), devolve `[conjunto_inicial]` — o conjunto completo
            que a função recebeu, não o do utilizador.
          - Se `subconjunto_utilizador` for `[]`, a condição de conter o
            subconjunto do utilizador é satisfeita por qualquer conjunto,
            logo o resultado passa a ser todos os subconjuntos de todos
            os maximais (sem filtro adicional).

    Raises:
        ValueError: se `subconjunto_utilizador` não for, de facto, um
            subconjunto de `conjunto_inicial`.
    """
    if not esta_contido(subconjunto_utilizador, conjunto_inicial):
        raise ValueError("O subconjunto introduzido tem de ser um subconjunto do conjunto inicial.")

    maximais = encontra_subconjuntos(conjunto_inicial, formula, modo="maximais_nao_implicam")

    # Caso especial: fórmula tautológica -> não há maximais que não a impliquem.
    if not maximais:
        return [conjunto_inicial]

    partes = calcula_partes_dos_maximais(maximais)
    return [subconjunto for subconjunto in partes if esta_contido(subconjunto_utilizador, subconjunto)]


def verifica_condicao_smooth(conjunto_inicial: list, subconjunto: list) -> bool:
    """
    Função principal do smooth kernel.
    Percorre todos os elementos do conjunto inicial. Se o elemento se deduzir 
    a partir do subconjunto e não pertencer ao subconjunto, devolve False. 
    Caso contrário, retorna True.
    """
    for elemento in conjunto_inicial:
        if verifica_deducao(subconjunto, elemento):
            pertence = any(elemento.eq(item) for item in subconjunto)
            if not pertence:
                return False
    return True


def calcula_smooth_kernel(conjunto_inicial: list, kernel: list) -> list:
    """
    Recebe o conjunto inicial e o kernel. Para cada subconjunto dentro do kernel,
    aplica a função de verificação. Devolve apenas os subconjuntos que dão True.
    """
    smooth_kernel = []
    for subconjunto in kernel:
        if verifica_condicao_smooth(conjunto_inicial, subconjunto):
            smooth_kernel.append(subconjunto)
    return smooth_kernel


def verifica_condicao_AGM(conjunto_inicial: list, conjunto_b: list, formula_inicial: BoolRef) -> bool:
    """
    Função principal: verifica se `conjunto_b` é "seguro" em relação ao
    `conjunto_inicial` (A) e à `formula_inicial`.

    Percorre todos os elementos de A. Para cada elemento que NÃO pertence
    a `conjunto_b`, testa se `conjunto_b` deduz a disjunção entre
    `formula_inicial` e esse elemento (`formula_inicial V elemento`). Se
    deduzir, `conjunto_b` não é seguro e a função devolve False de
    imediato. Se nenhum elemento fizer essa condição falhar, devolve True.

    Args:
        conjunto_inicial: conjunto completo de premissas (A) a percorrer.
        conjunto_b: subconjunto candidato a ser "seguro" (B).
        formula_inicial: fórmula usada na disjunção com cada elemento.

    Returns:
        False se existir algum elemento de `conjunto_inicial` fora de
        `conjunto_b` tal que `conjunto_b` deduza `formula_inicial V`
        esse elemento; True caso contrário.
    """
    for elemento in conjunto_inicial:
        pertence = any(elemento.eq(item) for item in conjunto_b)
        if not pertence:
            p = Or(formula_inicial, elemento)
            if verifica_deducao(conjunto_b, p):
                return False
    return True


def calcula_AGM(conjunto_inicial: list, partes_pre_kernel: list, formula_inicial: BoolRef) -> list:
    """
    Função secundária: usa `verifica_condicao_AGM` para filtrar
    `partes_pre_kernel`.

    `partes_pre_kernel` é tipicamente o passo anterior ao Kernel: as
    partes de cada subconjunto maximal que não implica `formula_inicial`
    (obtidas com as funções já implementadas `encontra_subconjuntos`,
    modo "maximais_nao_implicam", e `cria_partes_do_conjunto` aplicada a
    cada maximal) — ainda sem o filtro adicional que dá o Kernel.

    Para cada subconjunto de `partes_pre_kernel`, aplica a função
    principal (`verifica_condicao_AGM`) com `conjunto_inicial` e
    `formula_inicial`; guarda-o na lista de resultado só se o resultado
    for True.

    Args:
        conjunto_inicial: conjunto completo de premissas (A).
        partes_pre_kernel: lista de subconjuntos candidatos a testar.
        formula_inicial: fórmula alvo usada no teste de segurança.

    Returns:
        Lista dos subconjuntos de `partes_pre_kernel` para os quais
        `verifica_condicao_AGM` devolveu True.
    """
    resultado = []
    for subconjunto in partes_pre_kernel:
        if verifica_condicao_AGM(conjunto_inicial, subconjunto, formula_inicial):
            resultado.append(subconjunto)
    return resultado