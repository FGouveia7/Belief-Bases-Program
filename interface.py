import re
from colorama import init, Fore, Style
from z3 import Bool, Bools
from motor_logico import (
    verifica_deducao,
    encontra_subconjuntos,
    encontra_subconjuntos_maximais_com_subconjunto,
    calcula_smooth_kernel,
    calcula_partes_dos_maximais,
    calcula_AGM,
)
from operacoes_conjuntos import todas_intersecoes_maximais
from parser_formulas import (
    parse_formula,
    formata_formula,
    formata_lista,
    ErroParse,
    OPERADOR_OR,
    tokenizar,
)

init(autoreset=True)


def formata_conjunto(conjunto):
    if not conjunto:
        return "{}"
    elementos = formata_lista(conjunto)
    return "{" + ", ".join(elementos) + "}"


def formata_conjunto_a(premissas):
    return "A = {" + ",".join(formata_formula(p) for p in premissas) + "}"


def mostrar_conjunto_a(premissas):
    print(Style.BRIGHT + formata_conjunto_a(premissas))


def mostrar_sintaxe():
    print(Style.BRIGHT + "Supported syntax:")
    print(Style.BRIGHT + "  ~p        -> negation (NOT p)")
    print(Style.BRIGHT + "  p & q     -> conjunction (p AND q)")
    print(Style.BRIGHT + "  p V q     -> disjunction (p OR q)")
    print(Style.BRIGHT + "  p -> q    -> implication (IF p THEN q)")
    print(Style.BRIGHT + "  p <-> q   -> equivalence (p IFF q)")
    print(Style.BRIGHT + "  ( ... )   -> parentheses for grouping")
    print(Style.BRIGHT + "  Note: the uppercase letter \"V\" is reserved for disjunction,")
    print(Style.BRIGHT + "        so it cannot be used as a variable name.")
    print()


PADRAO_VARIAVEL = re.compile(r'^[A-Za-zÀ-ÿ]+[0-9]*$')


def pedir_com_retry(funcao, *args, max_tentativas=1, **kwargs):
    tentativas = 0
    while True:
        try:
            return funcao(*args, **kwargs)
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            tentativas += 1
            print(Fore.RED + f"Input error: {e}")
            if max_tentativas is not None and tentativas >= max_tentativas:
                print(Fore.YELLOW + f"Too many invalid attempts ({max_tentativas}).")
                raise
            print(Fore.YELLOW + "Please try again.")


def ler_variaveis():
    entrada = input(
        Style.BRIGHT + "Propositional variables (separated by spaces, e.g.: p q r, or q1 q2 q3): "
    ).strip()
    nomes = entrada.split()
    if not nomes:
        raise ValueError("at least one variable must be defined.")
    if not all(PADRAO_VARIAVEL.fullmatch(nome) for nome in nomes):
        raise ValueError(
            "variables must start with a letter and may end with digits "
            "(e.g.: p, q1, r23) — no leading digits or symbols allowed."
        )
    if OPERADOR_OR in nomes:
        raise ValueError(
            f"'{OPERADOR_OR}' cannot be used as a variable name, "
            "it is reserved for disjunction (OR)."
        )
    if len(set(nomes)) != len(nomes):
        raise ValueError("you cannot repeat a variable name.")
    return nomes


def inferir_variaveis(sentencas):
    nomes = []
    vistos = set()
    for texto in sentencas:
        for token in tokenizar(texto):
            if token in {"(", ")", "~", "&", OPERADOR_OR, "->", "<->"}:
                continue
            if not PADRAO_VARIAVEL.fullmatch(token):
                continue
            if token not in vistos:
                vistos.add(token)
                nomes.append(token)
    if not nomes:
        raise ValueError("no propositional variables could be inferred from the sentences.")
    return nomes


def remover_sentencas_duplicadas(sentencas):
    vistas = set()
    unicas = []
    for texto in sentencas:
        texto_limpo = texto.strip()
        if texto_limpo not in vistas:
            vistas.add(texto_limpo)
            unicas.append(texto_limpo)
    return unicas


def ler_conjunto_a():
    entrada = input(
        Style.BRIGHT
        + "Enter set A as a list of sentences (for example: {p, p -> q, q, r}): "
    ).strip()
    if not entrada:
        raise ValueError("set A cannot be empty.")

    if entrada.startswith("{") and entrada.endswith("}"):
        entrada = entrada[1:-1].strip()
    if not entrada:
        raise ValueError("set A cannot be empty.")

    sentencas = [parte.strip() for parte in entrada.split(",") if parte.strip()]
    if not sentencas:
        raise ValueError("set A cannot be empty.")
    return remover_sentencas_duplicadas(sentencas)


def construir_contexto(nomes):
    objetos = Bools(' '.join(nomes)) if len(nomes) > 1 else [Bool(nomes[0])]
    return dict(zip(nomes, objetos))


def ler_numero_premissas():
    texto_n = input(Style.BRIGHT + "Number of sentences: ").strip()
    try:
        n = int(texto_n)
    except ValueError:
        raise ValueError("the number of sentences only accepts integers.")
    if n < 0:
        raise ValueError("the number of sentences cannot be negative.")
    return n


def ler_uma_premissa(contexto, indice):
    texto = input(Style.BRIGHT + f"  Sentence {indice}: ").strip()
    if not texto:
        raise ValueError("the sentence cannot be empty.")
    return parse_formula(texto, contexto)


def ler_premissas(contexto):
    n = pedir_com_retry(ler_numero_premissas)
    premissas = []
    for i in range(n):
        premissas.append(pedir_com_retry(ler_uma_premissa, contexto, i + 1))
    return premissas


def ler_formula_alvo(contexto):
    texto = input(Style.BRIGHT + "Sentence to contract: ").strip()
    if not texto:
        raise ValueError("the target sentence cannot be empty.")
    return parse_formula(texto, contexto)


def ler_dados_iniciais():
    sentencas = pedir_com_retry(ler_conjunto_a, max_tentativas=None)
    nomes_vars = inferir_variaveis(sentencas)
    contexto = construir_contexto(nomes_vars)
    premissas = []
    for texto in sentencas:
        premissas.append(pedir_com_retry(parse_formula, texto, contexto))
    return contexto, premissas


def pedir_dados_iniciais_com_retry():
    while True:
        try:
            return ler_dados_iniciais()
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            print(Fore.RED + f"Unexpected error: {e}")
            print(Fore.YELLOW + "Let's start over.\n")
            continue


def mostrar_resultados(premissas, formula_alvo, contexto):
    print()
    print(Style.BRIGHT + "Results")
    print(Style.BRIGHT + "-------")

    conjunto_a = formata_conjunto(premissas)
    deduz = verifica_deducao(premissas, formula_alvo)
    cor_deduz = Fore.GREEN if deduz else Fore.RED
    print(Style.BRIGHT + f"{conjunto_a} implies {formata_formula(formula_alvo)}?: {cor_deduz}{deduz}")

    minimais = encontra_subconjuntos(premissas, formula_alvo, modo="minimais_implicam")
    print(Style.BRIGHT + f"\nKernel set of {conjunto_a} with respect to {formata_formula(formula_alvo)}:")
    if minimais:
        for m in minimais:
            print(Fore.GREEN + f"  {formata_conjunto(m)}")
    else:
        print(Fore.RED + "  none")

    maximais = encontra_subconjuntos(premissas, formula_alvo, modo="maximais_nao_implicam")
    print(Style.BRIGHT + f"\nRemainders of {conjunto_a} with respect to {formata_formula(formula_alvo)}:")
    if maximais:
        for m in maximais:
            print(Fore.GREEN + f"  {formata_conjunto(m)}")
    else:
        print(Fore.RED + "  none")

    intersecoes = todas_intersecoes_maximais(premissas, maximais)
    intersecoes.sort(key=len, reverse=True)
    print(Style.BRIGHT + "\nPossible outcomes of a partial meet contraction:")
    if intersecoes:
        for r in intersecoes:
            print(Fore.GREEN + f"  {formata_conjunto(r)}")
    else:
        print(Fore.RED + "  none")

    if intersecoes:
        resultado_full_meet = intersecoes[-1]
        print(Style.BRIGHT + "\nFull meet contraction:")
        print(Fore.GREEN + f"  {formata_conjunto(resultado_full_meet)}")
    else:
        resultado_full_meet = []
        print(Style.BRIGHT + "\nFull meet contraction:")
        print(Fore.RED + "  none")

    print(Style.BRIGHT + "\nPossible outcomes of a base contraction:")
    if maximais:
        partes_dos_maximais = calcula_partes_dos_maximais(maximais)
    else:
        # Fórmula tautológica: não há remainders, logo a única "parte"
        # possível de um remainder é o próprio conjunto A.
        partes_dos_maximais = [premissas]
    if partes_dos_maximais:
        for s in partes_dos_maximais:
            print(Fore.GREEN + f"  {formata_conjunto(s)}")
    else:
        print(Fore.RED + "  none")

    print(Style.BRIGHT + "\nPossible outcomes of a kernel contraction:")
    if resultado_full_meet:
        kernel = encontra_subconjuntos_maximais_com_subconjunto(
            premissas, resultado_full_meet, formula_alvo
        )
    else:
        kernel = []
    if kernel:
        for s in kernel:
            print(Fore.GREEN + f"  {formata_conjunto(s)}")
    else:
        print(Fore.RED + "  none")

    print(Style.BRIGHT + "\nPossible outcomes of a smooth kernel contraction:")
    smooth_kernel = calcula_smooth_kernel(premissas, kernel)
    if smooth_kernel:
        for s in smooth_kernel:
            print(Fore.GREEN + f"  {formata_conjunto(s)}")
    else:
        print(Fore.RED + "  none")

    print(Style.BRIGHT + "\nPossible outcomes of a basic AGM-generated base contraction:")
    resultado_agm = calcula_AGM(premissas, partes_dos_maximais, formula_alvo)
    if resultado_agm:
        for s in resultado_agm:
            print(Fore.GREEN + f"  {formata_conjunto(s)}")
    else:
        print(Fore.RED + "  none")

    eh_tautologia = verifica_deducao([], formula_alvo)
    if eh_tautologia:
        print(Style.BRIGHT + "\nPossible outcomes of a bounded contraction:")
        print(Fore.GREEN + f"  {formata_conjunto(premissas)}")


def ler_subconjunto_por_indices(premissas, rotulo):
    """
    Pede ao utilizador, numa só linha, os números das premissas (já
    mostradas por `mostrar_premissas`) que formam o conjunto `rotulo` —
    um subconjunto do conjunto inicial de premissas, escolhido por
    número em vez de se escrever cada fórmula de novo (ex: "1 2 3").

    Valida que cada número corresponde a uma premissa existente, e que
    não foram indicados mais números do que o total de premissas do
    conjunto inicial. Uma entrada em branco corresponde ao conjunto
    vazio.

    Args:
        premissas: lista de premissas Z3 da ronda atual (o conjunto A).
        rotulo: nome do conjunto a formar (usado só nas mensagens).

    Returns:
        Lista das fórmulas Z3 de `premissas` correspondentes aos números
        indicados, pela mesma ordem em que foram introduzidos.

    Raises:
        ValueError: se algum número não for inteiro, não corresponder a
            nenhuma premissa existente, ou se forem indicados mais
            números do que o total de premissas do conjunto inicial.
    """
    entrada = input(
        Style.BRIGHT
        + f"Select the lower-bound set {rotulo} to determine the possible outcome of a bounded contraction (e.g., 1 3; press Enter to use the empty set): "    )
    if not entrada.strip():
        return []

    try:
        indices = [int(token) for token in entrada.split()]
    except ValueError:
        raise ValueError("sentence numbers only accept integers.")

    if len(indices) > len(premissas):
        raise ValueError(
            f"set {rotulo} cannot have more elements ({len(indices)}) than the "
            f"initial set of sentences ({len(premissas)})."
        )

    if len(set(indices)) != len(indices):
        raise ValueError("you cannot select the same sentence number twice.")

    for indice in indices:
        if indice < 1 or indice > len(premissas):
            raise ValueError(f"there is no sentence number {indice}.")

    return [premissas[indice - 1] for indice in indices]


def mostrar_deducao_entre_conjuntos(contexto, premissas, formula_atual):
    """
    Mostra de novo o conjunto A (as premissas da ronda atual, numeradas),
    e pede ao utilizador que escolha, por número, quais delas formam o
    conjunto B — um subconjunto do conjunto inicial de premissas.

    Ao contrário do que se fazia antes, aqui NÃO se recalculam os
    remainders, o full meet, o Kernel, o Smooth Kernel nem o AGM: esses
    resultados dependem só de `premissas` e da fórmula alvo já testada
    (`formula_atual`), não do conjunto B — o Kernel, em particular, é
    sempre "as partes dos remainders que contêm o full meet", por
    definição, e continua exatamente igual ao que já foi mostrado.

    O que de facto muda com B é só uma coisa: quais as partes dos
    remainders (da mesma fórmula alvo já testada) que contêm o conjunto
    B escolhido pelo utilizador, em vez do full meet. É só isso que se
    mostra aqui.

    Se ainda não houver nenhuma fórmula alvo válida testada nesta ronda
    (`formula_atual` é None), avisa o utilizador em vez de pedir B.
    """
    if formula_atual is None:
        print(Fore.YELLOW + "No valid target sentence has been tested yet in this round; first choose the option to test a sentence.")
        return

    mostrar_premissas(premissas)

    conjunto_b = pedir_com_retry(ler_subconjunto_por_indices, premissas, "B", max_tentativas=None)
    conjunto_b_formatado = formata_conjunto(conjunto_b)

    print(
        Style.BRIGHT
        + "---Result---\n"
        + f"\nPossible outcomes of a bounded contraction with a lower-bound B = {conjunto_b_formatado}:"
    )
    resultado = encontra_subconjuntos_maximais_com_subconjunto(premissas, conjunto_b, formula_atual)
    if resultado:
        for s in resultado:
            print(Fore.GREEN + f"  {formata_conjunto(s)}")
    else:
        print(Fore.RED + "  none")


def perguntar_proximo_passo(premissas, permitir_opcao_b=True):
    print()
    while True:
        texto_menu = (
            Style.BRIGHT
            + "Choose an option:\n"
            + "  (1) Contract another sentence using the same set A\n"
            + f"      {formata_conjunto_a(premissas)}\n"
        )
        if permitir_opcao_b:
            texto_menu += "  (2) Possible outcomes of a bounded contraction with lower-bound B\n"
        else:
            texto_menu += ( "  Note: option 2 is not available - the sentence is a tautology\n"
    
                + Style.BRIGHT
            )
        texto_menu += (
            "  (3) Start with a new set\n"
            + "  (0) Exit\n"
            + "Selected option: "
        )
        try:
            resposta = input(texto_menu).strip()
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            print(Fore.RED + f"Input error: {e}")
            print(Fore.YELLOW + "Please choose a valid option.")
            continue

        if resposta == "1":
            return "formula"
        if resposta == "2" and permitir_opcao_b:
            return "ab"
        if resposta == "3":
            return "novo"
        if resposta == "0":
            return "sair"

        if resposta == "2" and not permitir_opcao_b:
            print(Fore.RED + "Option 2 is not available: the target sentence is a tautology, "
                              "so the bounded contraction outcome is always A (already shown above).")
        else:
            print(Fore.RED + "Invalid option. Please choose a valid option.")


def mostrar_premissas(premissas):
    print(Style.BRIGHT + "\nCurrent sentences of A:")
    for indice, premissa in enumerate(premissas, start=1):
        print(Style.BRIGHT + f"  {indice}. {formata_formula(premissa)}")
    print()


def menu_interativo():
    mostrar_sintaxe()

    contexto, premissas = pedir_dados_iniciais_com_retry()
    mostrar_conjunto_a(premissas)

    repetir_formula = False
    formula_atual = None
    while True:
        if repetir_formula:
            mostrar_conjunto_a(premissas)

        try:
            formula_alvo = pedir_com_retry(ler_formula_alvo, contexto, max_tentativas=None)
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            print(Fore.RED + f"Unexpected error while reading the target sentence: {e}")
            print(Fore.YELLOW + "The session will continue; please try again.")
            continue

        try:
            mostrar_resultados(premissas, formula_alvo, contexto)
        except Exception as e:
            print(Fore.RED + f"Unexpected error while computing the results: {e}")
            print(Fore.YELLOW + "The sentences were kept; you can try another one.")
        else:
            formula_atual = formula_alvo

        # Se a fórmula for uma tautologia, não há remainders (o conjunto vazio
        # já a implica), pelo que qualquer contração limitada por um B daria
        # sempre A — resultado que já aparece nos resultados acima. Por isso
        # a opção 2 não é oferecida neste caso.
        eh_tautologia = formula_atual is not None and verifica_deducao([], formula_atual)

        try:
            escolha = pedir_com_retry(perguntar_proximo_passo, premissas, not eh_tautologia)
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception:
            print(Fore.YELLOW + "No valid option was selected. Exiting the session.")
            break

        while escolha == "ab":
            try:
                mostrar_deducao_entre_conjuntos(contexto, premissas, formula_atual)
            except (KeyboardInterrupt, EOFError):
                raise
            except Exception as e:
                print(Fore.RED + f"Unexpected error while computing the bounded contraction: {e}")
                print(Fore.YELLOW + "Returning to the menu.")
            try:
                escolha = pedir_com_retry(perguntar_proximo_passo, premissas, not eh_tautologia)
            except (KeyboardInterrupt, EOFError):
                raise
            except Exception:
                print(Fore.YELLOW + "No valid option was selected. Exiting the session.")
                escolha = "sair"

        if escolha == "formula":
            repetir_formula = True
            continue

        elif escolha == "novo":
            print()
            contexto, premissas = pedir_dados_iniciais_com_retry()
            mostrar_conjunto_a(premissas)
            formula_atual = None
            repetir_formula = False
            continue

        else:
            break