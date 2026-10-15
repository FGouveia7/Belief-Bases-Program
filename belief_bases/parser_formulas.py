"""Interpretar e formatar fórmulas proposicionais na notação da aplicação.

A precedência é ``~ > & > V > -> > <->``. A negação, a implicação e a
equivalência associam à direita; a conjunção e a disjunção associam à
esquerda. ``V`` é sempre disjunção, incluindo em ``pVq``; por isso nenhum
nome de variável pode conter essa letra maiúscula.

Os identificadores contêm letras ASCII ou letras do intervalo Latin-1,
seguidas opcionalmente de algarismos ASCII. Não se trata de identificadores
Unicode arbitrários. O contexto associa esses nomes a expressões BoolRef.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence

from z3 import (
    And,
    BoolRef,
    Implies,
    Not,
    Or,
    is_and,
    is_bool,
    is_eq,
    is_false,
    is_implies,
    is_not,
    is_or,
    is_true,
)

# Mantido como constante pública para compatibilidade com o módulo original.
TOKEN_REGEX = re.compile(r"<->|->|[~&()]")
# Os intervalos separados excluem × e ÷; A-U e W-Z excluem o operador V.
VARIAVEL_REGEX = re.compile(r"^[A-UW-Za-zÀ-ÖØ-öø-ÿ]+[0-9]*$")

OPERADOR_OR = "V"
TOKENS_OPERADOR = {"~", "&", OPERADOR_OR, "->", "<->"}
MENSAGEM_VARIAVEL_INVALIDA = (
    "variables must start with a letter and may end with digits "
    "(e.g.: p, q1, r23) — no leading digits or symbols allowed."
)


class ErroParse(ValueError):
    """Erro de sintaxe, de identificador ou de variável desconhecida."""


def nome_variavel_valido(nome: str) -> bool:
    """Indicar se o nome pode ser referenciado como um único identificador."""
    return VARIAVEL_REGEX.fullmatch(nome) is not None


def validar_nome_variavel(nome: str) -> None:
    """Validar o mesmo conjunto de nomes usado pelo tokenizador.

    Raises:
        ErroParse: se o nome contiver o operador V ou violar a sintaxe dos
            identificadores. ErroParse é uma subclasse de ValueError.
    """
    if OPERADOR_OR in nome:
        raise ErroParse(
            f"'{OPERADOR_OR}' cannot appear in a variable name, "
            "it is reserved for disjunction (OR)."
        )
    if not nome_variavel_valido(nome):
        raise ErroParse(MENSAGEM_VARIAVEL_INVALIDA)


def tokenizar(texto: str) -> list[str]:
    """Separar operadores e identificadores, rejeitando caracteres inválidos.

    Os operadores compostos são reconhecidos primeiro. O V maiúsculo é
    reconhecido antes dos identificadores e termina sempre o seu varrimento.
    """
    posicao = 0
    tokens: list[str] = []
    while posicao < len(texto):
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

        if texto[posicao] in "~&()" or texto[posicao] == OPERADOR_OR:
            tokens.append(texto[posicao])
            posicao += 1
            continue

        if texto[posicao].isalpha() or texto[posicao].isdigit():
            fim = posicao + 1
            while (
                fim < len(texto)
                and (texto[fim].isalpha() or texto[fim].isdigit())
                and texto[fim] != OPERADOR_OR
            ):
                fim += 1
            segmento = texto[posicao:fim]
            validar_nome_variavel(segmento)
            tokens.append(segmento)
            posicao = fim
            continue

        raise ErroParse(
            f"unexpected character '{texto[posicao]}' at position {posicao + 1}."
        )

    return tokens


class ParserFormula:
    """Parser recursivo-descendente, do operador mais fraco para o mais forte.

    Gramática::

        iff      := implies ( '<->' iff )?
        implies  := or ( '->' implies )?
        or       := and ( 'V' and )*
        and      := not ( '&' not )*
        not      := '~' not | primaria
        primaria := IDENTIFICADOR | '(' iff ')'
    """

    def __init__(self, tokens: Sequence[str], contexto: Mapping[str, BoolRef]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.contexto = contexto

    def espreitar(self) -> str | None:
        """Obter o token atual ou None no fim da expressão."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self) -> str | None:
        """Devolver o token atual e avançar a posição de leitura."""
        token = self.espreitar()
        self.pos += 1
        return token

    def esperar(self, token_esperado: str) -> None:
        """Consumir o token esperado ou indicar o erro de sintaxe."""
        token = self.consumir()
        if token != token_esperado:
            encontrado = "end of formula" if token is None else repr(token)
            raise ErroParse(f"expected '{token_esperado}' but found {encontrado}.")

    def parse(self) -> BoolRef:
        """Interpretar todos os tokens, rejeitando conteúdo excedente."""
        resultado = self.parse_iff()
        if self.pos != len(self.tokens):
            raise ErroParse(f"extra input starting from '{self.espreitar()}'.")
        return resultado

    def parse_iff(self) -> BoolRef:
        """Interpretar equivalências com associação à direita."""
        esquerda = self.parse_implies()
        if self.espreitar() == "<->":
            self.consumir()
            direita = self.parse_iff()
            return esquerda == direita
        return esquerda

    def parse_implies(self) -> BoolRef:
        """Interpretar implicações com associação à direita."""
        esquerda = self.parse_or()
        if self.espreitar() == "->":
            self.consumir()
            direita = self.parse_implies()
            return Implies(esquerda, direita)
        return esquerda

    def parse_or(self) -> BoolRef:
        """Interpretar disjunções com associação à esquerda."""
        esquerda = self.parse_and()
        while self.espreitar() == OPERADOR_OR:
            self.consumir()
            direita = self.parse_and()
            esquerda = Or(esquerda, direita)
        return esquerda

    def parse_and(self) -> BoolRef:
        """Interpretar conjunções com associação à esquerda."""
        esquerda = self.parse_not()
        while self.espreitar() == "&":
            self.consumir()
            direita = self.parse_not()
            esquerda = And(esquerda, direita)
        return esquerda

    def parse_not(self) -> BoolRef:
        """Interpretar uma cadeia de negações antes da fórmula primária."""
        if self.espreitar() == "~":
            self.consumir()
            return Not(self.parse_not())
        return self.parse_primaria()

    def parse_primaria(self) -> BoolRef:
        """Interpretar uma variável definida ou uma expressão entre parênteses."""
        token = self.espreitar()
        if token is None:
            raise ErroParse("incomplete formula (unexpected end).")
        if token == "(":
            self.consumir()
            resultado = self.parse_iff()
            self.esperar(")")
            return resultado
        if token in TOKENS_OPERADOR or token == ")":
            raise ErroParse(f"unexpected symbol '{token}'.")
        self.consumir()
        if token not in self.contexto:
            raise ErroParse(f"variável '{token}' não foi definida.")
        return self.contexto[token]


def parse_formula(texto: str, contexto: Mapping[str, BoolRef]) -> BoolRef:
    """Converter a notação ``~, &, V, ->, <->`` numa expressão booleana Z3.

    Raises:
        ErroParse: se a fórmula estiver vazia, tiver sintaxe inválida ou
            referir uma variável ausente do contexto.
    """
    tokens = tokenizar(texto)
    if not tokens:
        raise ErroParse("empty formula.")
    return ParserFormula(tokens, contexto).parse()


_PRECEDENCIA = {"atomo": 5, "not": 4, "and": 3, "or": 2, "implies": 1, "iff": 0}


def _formata_associativa(
    formula: BoolRef, operador: str, nivel: int
) -> tuple[str, int]:
    """Formatar conjunções/disjunções sem parênteses associativos redundantes."""
    partes = []
    for filho in formula.children():
        texto, precedencia = _formata_no(filho)
        partes.append(texto if precedencia >= nivel else f"({texto})")
    return f" {operador} ".join(partes), nivel


def _formata_binaria(formula: BoolRef, operador: str, nivel: int) -> tuple[str, int]:
    """Explicitar parênteses para operandos de precedência igual ou menor."""
    esquerda, precedencia_esquerda = _formata_no(formula.arg(0))
    direita, precedencia_direita = _formata_no(formula.arg(1))
    if precedencia_esquerda <= nivel:
        esquerda = f"({esquerda})"
    if precedencia_direita <= nivel:
        direita = f"({direita})"
    return f"{esquerda} {operador} {direita}", nivel


def _formata_no(formula: BoolRef) -> tuple[str, int]:
    """Obter o texto e a precedência de uma subfórmula."""
    if is_true(formula):
        return "True", _PRECEDENCIA["atomo"]
    if is_false(formula):
        return "False", _PRECEDENCIA["atomo"]

    if is_not(formula):
        texto, precedencia = _formata_no(formula.arg(0))
        if precedencia < _PRECEDENCIA["not"]:
            texto = f"({texto})"
        return f"~{texto}", _PRECEDENCIA["not"]

    if is_and(formula):
        return _formata_associativa(formula, "&", _PRECEDENCIA["and"])
    if is_or(formula):
        return _formata_associativa(formula, OPERADOR_OR, _PRECEDENCIA["or"])
    if is_implies(formula):
        return _formata_binaria(formula, "->", _PRECEDENCIA["implies"])
    if is_eq(formula) and is_bool(formula.arg(0)) and is_bool(formula.arg(1)):
        return _formata_binaria(formula, "<->", _PRECEDENCIA["iff"])

    return str(formula), _PRECEDENCIA["atomo"]


def formata_formula(f: BoolRef) -> str:
    """Converter uma fórmula Z3 para a notação simbólica da interface.

    A formatação conserva a precedência e explicita o agrupamento de
    implicações e equivalências. Conjunções/disjunções podem perder
    parênteses associativos, preservando a equivalência lógica. As
    constantes Z3 são apresentadas como True/False; o parser não define
    literais booleanos e interpreta esses nomes através do contexto.
    """
    texto, _ = _formata_no(f)
    return texto


def formata_lista(formulas: Iterable[BoolRef]) -> list[str]:
    """Formatar as fórmulas pela ordem recebida, sem remover duplicados."""
    return [formata_formula(formula) for formula in formulas]
