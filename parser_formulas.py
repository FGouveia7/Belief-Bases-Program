# parser_formulas.py
"""
Parser recursivo-descendente para fórmulas de lógica proposicional na
notação simbólica pedida, em vez das chamadas Z3 (And, Or, Not, ...):

    ~p       -> negação           (NAO p)
    p & q    -> conjunção          (p E q)
    p V q    -> disjunção          (p OU q)
    p -> q   -> implicação         (SE p ENTAO q)
    p <-> q  -> equivalência       (p SSE q)
    ( ... )  -> parênteses para agrupar

Precedência dos operadores, do mais forte ao mais fraco:

    ~   >   &   >   V   >   ->   >   <->

`~` é unário e associa à direita.
`->` e `<->` associam à direita (ex: p -> q -> r  ==  p -> (q -> r)).

IMPORTANTE: a letra maiúscula "V" fica reservada para a disjunção, por
isso não pode existir nenhuma variável proposicional chamada exatamente
"V" (maiúsculo). Isto é validado em interface.py (ler_variaveis).
"""

import re
from z3 import (
    And, Or, Not, Implies,
    is_and, is_or, is_not, is_implies, is_eq, is_true, is_false, is_bool,
)

# Ordem importa: tokens compostos (<->, ->) têm de ser tentados antes dos
# tokens de um só carácter, senão "->" seria lido como dois tokens.
TOKEN_REGEX = re.compile(r'<->|->|[~&()]')
VARIAVEL_REGEX = re.compile(r'^[A-Za-zÀ-ÿ]+[0-9]*$')

OPERADOR_OR = "V"
TOKENS_OPERADOR = {"~", "&", OPERADOR_OR, "->", "<->"}
MENSAGEM_VARIAVEL_INVALIDA = (
    "variables must start with a letter and may end with digits "
    "(e.g.: p, q1, r23) — no leading digits or symbols allowed."
)


class ErroParse(ValueError):
    """Erro de sintaxe ao interpretar uma fórmula."""
    pass


def tokenizar(texto):
    posicao = 0
    tokens = []
    n = len(texto)
    while posicao < n:
        if texto[posicao].isspace():
            posicao += 1
            continue

        if texto.startswith("<->", posicao):
            tokens.append("<->")
            posicao += 3
            continue

        if texto.startswith("->", posicao):
            tokens.append("->")
            posicao += 2
            continue

        if texto[posicao] in "~&()":
            tokens.append(texto[posicao])
            posicao += 1
            continue

        # "V" é sempre o operador de disjunção, mesmo colado a letras
        # (ex: "pVq"), por isso é tratado à parte, antes do varrimento
        # genérico de identificadores abaixo — que também para ao
        # encontrar um "V", em vez de o engolir para dentro do nome.
        if texto[posicao] == OPERADOR_OR:
            tokens.append(OPERADOR_OR)
            posicao += 1
            continue

        if texto[posicao].isalpha() or texto[posicao].isdigit():
            fim = posicao + 1
            while (
                fim < n
                and (texto[fim].isalpha() or texto[fim].isdigit())
                and texto[fim] != OPERADOR_OR
            ):
                fim += 1
            segmento = texto[posicao:fim]
            if not VARIAVEL_REGEX.fullmatch(segmento):
                raise ErroParse(MENSAGEM_VARIAVEL_INVALIDA)
            tokens.append(segmento)
            posicao = fim
            continue

        raise ErroParse(f"unexpected character '{texto[posicao]}' at position {posicao + 1}.")

    return tokens


class ParserFormula:
    """
    Gramática (do nível mais baixo/fraco para o mais alto/forte):

        iff      := implies ( '<->' iff )?
        implies  := or ( '->' implies )?
        or       := and ( 'V' and )*
        and      := not ( '&' not )*
        not      := '~' not | primaria
        primaria := IDENTIFICADOR | '(' iff ')'
    """

    def __init__(self, tokens, contexto):
        self.tokens = tokens
        self.pos = 0
        self.contexto = contexto

    def espreitar(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self):
        tok = self.espreitar()
        self.pos += 1
        return tok

    def esperar(self, token_esperado):
        tok = self.consumir()
        if tok != token_esperado:
            raise ErroParse(f"expected '{token_esperado}' but found "
                             f"{'end of formula' if tok is None else repr(tok)}.")

    def parse(self):
        resultado = self.parse_iff()
        if self.pos != len(self.tokens):
            raise ErroParse(f"extra input starting from '{self.espreitar()}'.")
        return resultado

    def parse_iff(self):
        esquerda = self.parse_implies()
        if self.espreitar() == "<->":
            self.consumir()
            direita = self.parse_iff()
            return esquerda == direita
        return esquerda

    def parse_implies(self):
        esquerda = self.parse_or()
        if self.espreitar() == "->":
            self.consumir()
            direita = self.parse_implies()
            return Implies(esquerda, direita)
        return esquerda

    def parse_or(self):
        esquerda = self.parse_and()
        while self.espreitar() == OPERADOR_OR:
            self.consumir()
            direita = self.parse_and()
            esquerda = Or(esquerda, direita)
        return esquerda

    def parse_and(self):
        esquerda = self.parse_not()
        while self.espreitar() == "&":
            self.consumir()
            direita = self.parse_not()
            esquerda = And(esquerda, direita)
        return esquerda

    def parse_not(self):
        if self.espreitar() == "~":
            self.consumir()
            return Not(self.parse_not())
        return self.parse_primaria()

    def parse_primaria(self):
        tok = self.espreitar()
        if tok is None:
            raise ErroParse("incomplete formula (unexpected end).")
        if tok == "(":
            self.consumir()
            resultado = self.parse_iff()
            self.esperar(")")
            return resultado
        if tok in TOKENS_OPERADOR or tok == ")":
            raise ErroParse(f"unexpected symbol '{tok}'.")
        # identificador -> variável do contexto
        self.consumir()
        if tok not in self.contexto:
            raise ErroParse(f"variável '{tok}' não foi definida.")
        return self.contexto[tok]


def parse_formula(texto, contexto):
    """
    Recebe a string da fórmula (notação ~, &, V, ->, <->) e o dicionário
    `contexto` (nome de variável -> Bool do Z3) e devolve a fórmula Z3
    correspondente.

    Raises ErroParse (a subclass of ValueError) in case of a
    syntax error or unknown variable.
    """
    tokens = tokenizar(texto)
    if not tokens:
        raise ErroParse("empty formula.")
    parser = ParserFormula(tokens, contexto)
    return parser.parse()


# Nível de precedência de cada tipo de nó, usado só para decidir onde
# colocar parênteses ao reconstruir a string. Quanto maior, mais "junto"
# fica sem precisar de parênteses (mesma ordem do parser, ao contrário).
_PRECEDENCIA = {"atomo": 5, "not": 4, "and": 3, "or": 2, "implies": 1, "iff": 0}


def _formata_no(f):
    """
    Devolve (texto, nivel_precedencia) para a subfórmula `f`.
    """
    if is_true(f):
        return "True", _PRECEDENCIA["atomo"]
    if is_false(f):
        return "False", _PRECEDENCIA["atomo"]

    if is_not(f):
        texto_sub, prec_sub = _formata_no(f.arg(0))
        if prec_sub < _PRECEDENCIA["not"]:
            texto_sub = f"({texto_sub})"
        return f"~{texto_sub}", _PRECEDENCIA["not"]

    if is_and(f):
        nivel = _PRECEDENCIA["and"]
        partes = []
        for filho in f.children():
            texto_f, prec_f = _formata_no(filho)
            partes.append(texto_f if prec_f >= nivel else f"({texto_f})")
        return " & ".join(partes), nivel

    if is_or(f):
        nivel = _PRECEDENCIA["or"]
        partes = []
        for filho in f.children():
            texto_f, prec_f = _formata_no(filho)
            partes.append(texto_f if prec_f >= nivel else f"({texto_f})")
        return f" {OPERADOR_OR} ".join(partes), nivel

    if is_implies(f):
        nivel = _PRECEDENCIA["implies"]
        esquerda, prec_e = _formata_no(f.arg(0))
        direita, prec_d = _formata_no(f.arg(1))
        # Embora "->" seja associativo à direita (tecnicamente "p -> q -> r"
        # reconstrói a mesma árvore que "p -> (q -> r)"), mostrar sempre os
        # parênteses de ambos os lados quando o operando é composto evita
        # ambiguidade visual e reflete fielmente a fórmula original tal
        # como o utilizador a escreveu (ex: "(p->q)->(~q->~p)").
        if prec_e <= nivel:
            esquerda = f"({esquerda})"
        if prec_d <= nivel:
            direita = f"({direita})"
        return f"{esquerda} -> {direita}", nivel

    if is_eq(f) and is_bool(f.arg(0)) and is_bool(f.arg(1)):
        nivel = _PRECEDENCIA["iff"]
        esquerda, prec_e = _formata_no(f.arg(0))
        direita, prec_d = _formata_no(f.arg(1))
        if prec_e <= nivel:
            esquerda = f"({esquerda})"
        if prec_d <= nivel:
            direita = f"({direita})"
        return f"{esquerda} <-> {direita}", nivel

    # variável (ou qualquer outro nó atómico não reconhecido acima)
    return str(f), _PRECEDENCIA["atomo"]


def formata_formula(f):
    """
    Converte uma fórmula Z3 (construída por parse_formula ou por
    combinação de fórmulas Z3) de volta para a notação simbólica
    ~, &, V, ->, <-> usada na interface.
    """
    texto, _ = _formata_no(f)
    return texto


def formata_lista(formulas):
    """Formata uma lista/conjunto de fórmulas Z3, uma a uma, devolvendo
    a lista de strings correspondente (mesma ordem)."""
    return [formata_formula(f) for f in formulas]