# Belief Bases Program

Aplicação Python para analisar contrações de bases de crenças em lógica
proposicional, usando Z3 como motor de inferência. A interface de terminal
permite introduzir uma base, escolher uma fórmula a contrair e consultar os
resultados possíveis dos operadores descritos no
[relatório teórico](RelatorioBelifBases.pdf).

## Como executar o projeto

É necessário Python **3.10 ou superior**. As dependências de execução são
`z3-solver` e `colorama`; `itertools`, `re` e as restantes ferramentas da
biblioteca padrão já acompanham o Python.

Clone o repositório e entre na pasta do projeto:

```text
git clone https://github.com/FGouveia7/Belief-Bases-Program.git
cd Belief-Bases-Program
```

Se já tem o projeto no computador, abra um terminal na pasta que contém
`main.py` e `requirements.txt`.

### Windows (PowerShell)

Na primeira execução, crie o ambiente virtual, instale as dependências e
inicie a aplicação:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Se o comando `python` não estiver disponível e tiver o Python Launcher
instalado, use `py -3 -m venv .venv` no primeiro comando. Os comandos seguintes
usam diretamente o Python do ambiente, sem precisar de o ativar.

Nas próximas execuções, basta abrir o terminal na pasta do projeto e correr:

```powershell
.\.venv\Scripts\python.exe main.py
```

### Linux e macOS

Na primeira execução:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python main.py
```

Nas próximas execuções, na pasta do projeto:

```bash
./.venv/bin/python main.py
```

### Executável para Windows

Também pode abrir `BeliefBasesProgram-refatorado.exe`, disponível na raiz
do projeto, sem instalar Python. No PowerShell, execute:

```powershell
.\BeliefBasesProgram-refatorado.exe
```

O executável contém a versão do código usada quando foi gerado. Após alterar
o código-fonte, siga as instruções de geração de um novo executável abaixo.

### Ficheiros de dependências

Se a instalação apresentar `No module named pip`, instale o pip no ambiente
e repita o comando de instalação das dependências. Em Windows:

```powershell
.\.venv\Scripts\python.exe -m ensurepip --upgrade
```

Em Linux/macOS, use `./.venv/bin/python -m ensurepip --upgrade`.

As dependências estão separadas por finalidade:

| Ficheiro | Finalidade |
| --- | --- |
| `requirements.txt` | Execução: Z3 e cores do terminal |
| `requirements-dev.txt` | Execução e Ruff |
| `requirements-build.txt` | Execução e PyInstaller `>=6.11,<7` |

## Sintaxe das fórmulas

| Sintaxe | Operação | Exemplo |
| --- | --- | --- |
| `~` | Negação | `~p` |
| `&` | Conjunção | `p & q` |
| `V` | Disjunção | `p V q` |
| `->` | Implicação | `p -> q` |
| `<->` | Equivalência | `p <-> q` |
| `( ... )` | Agrupamento | `~(p V q)` |

A precedência, da mais forte para a mais fraca, é
`~ > & > V > -> > <->`. A conjunção e a disjunção associam à esquerda;
a negação, a implicação e a equivalência associam à direita. Assim,
`p -> q -> r` significa `p -> (q -> r)`, enquanto `p & q & r` é interpretado
como `(p & q) & r`.

A gramática usada pelo parser é:

```text
iff      := implies ( '<->' iff )?
implies  := or ( '->' implies )?
or       := and ( 'V' and )*
and      := not ( '&' not )*
not      := '~' not | primaria
primaria := IDENTIFICADOR | '(' iff ')'
```

Os nomes de variáveis distinguem maiúsculas de minúsculas. Aceitam letras
ASCII e letras Latin-1, opcionalmente seguidas de algarismos ASCII: `p`,
`q1`, `ação23` e `v` são exemplos válidos. Não aceitam algarismos iniciais,
algarismos no meio das letras, `_`, `×`, `÷` ou letras fora desses intervalos.
O padrão partilhado pelo parser e pela validação da interface é
`[A-UW-Za-zÀ-ÖØ-öø-ÿ]+[0-9]*`.

O **`V` maiúsculo está reservado para disjunção em qualquer posição**.
`pVq` é uma fórmula equivalente a `p V q`, e não um nome de variável.
Nomes como `V` e `Verdade` são inválidos. Os espaços entre os operadores e
as variáveis são opcionais.

A formatação mantém a precedência e explicita o agrupamento de implicações
e equivalências. Pode retirar parênteses associativos de conjunções e
disjunções. As constantes booleanas Z3 são apresentadas como `True` e
`False`, mas esses textos **não são literais especiais do parser**: quando
introduzidos numa fórmula, são procurados como nomes de variáveis no contexto.

## Utilização no terminal

Depois de iniciar a aplicação com o comando indicado acima:

1. Introduza uma base A com sentenças separadas por vírgulas. As chavetas são
   opcionais: `{p, p -> q, q, r}`.
2. Introduza a fórmula a contrair, por exemplo `q`.
3. Consulte os kernels, os remainders e os resultados dos operadores.
4. Use o menu: `1` contrai outra fórmula com a mesma base; `2` seleciona um
   limite inferior B; `3` começa com uma nova base; `0` termina a sessão.

Por exemplo, introduza `{p, p -> q, q, r}` quando for pedida a base e `q`
quando for pedida a fórmula alvo. Depois de consultar os resultados, escolha
`0` e prima Enter para fechar o programa.

A interface exige uma base **não vazia** e infere o contexto de variáveis
apenas a partir das sentenças de A. A fórmula alvo só pode usar essas variáveis;
para usar uma variável nova no terminal, introduza uma nova base que a inclua.
Fórmulas estruturalmente repetidas são normalizadas, preservando a primeira
ocorrência.

Na opção de contração limitada, escolha B pelos números das sentenças de A,
por exemplo `1 3`. Enter seleciona o conjunto vazio. Não são aceites índices
repetidos ou inexistentes. Para um alvo tautológico não existem remainders;
segue-se a convenção do relatório que mantém A como resultado de contração.
A opção de selecionar B fica indisponível nesse caso, porque o resultado
limitado já foi apresentado.

Entradas inválidas recebem uma mensagem e uma nova leitura. Erros inesperados
chegam à fronteira da aplicação com diagnóstico e código de saída `1`.
Fim da entrada (EOF) termina com código `0`; `Ctrl+C` termina com código `130`.
Depois de terminar uma sessão normalmente, Enter fecha o programa e `1`
inicia outra sessão.

### Exemplo matemático

Para `A = {p, p -> q, q, r}` e alvo `q`:

| Resultado | Conjuntos |
| --- | --- |
| Kernels: subconjuntos minimais que implicam `q` | `{q}` e `{p, p -> q}` |
| Remainders: subconjuntos maximais que não implicam `q` | `{p, r}` e `{p -> q, r}` |
| Full meet: interseção de todos os remainders | `{r}` |
| Resultados partial meet | `{p, r}`, `{p -> q, r}` e `{r}` |

Os kernels são os conjuntos minimais que implicam o alvo; não se confundem
com a família de resultados possíveis de uma kernel contraction.

## API Python

O cálculo é independente do terminal. `analisar_contracao()` devolve um objeto
`ResultadoAnalise`; a apresentação apenas recebe esses resultados.

```python
from z3 import Bool

from belief_bases.analise import analisar_contracao, analisar_limite
from belief_bases.parser_formulas import formata_lista, parse_formula

contexto = {nome: Bool(nome) for nome in ("p", "q", "r")}
base = [parse_formula(texto, contexto) for texto in ("p", "p -> q", "q", "r")]
resultado = analisar_contracao(base, contexto["q"])
print(formata_lista(resultado.full_meet))  # ['r']

resultados_limitados = analisar_limite(resultado, [contexto["r"]])
for conjunto in resultados_limitados:
    print(formata_lista(conjunto))
```

A API aceita também uma base vazia e um alvo com variáveis que não aparecem
na base, por exemplo `analisar_contracao([], Bool("nova"))`. Essa possibilidade
é independente das restrições de entrada do terminal. Um limite inferior B
tem de ser subconjunto estrutural da base; pode não existir resultado
limitado quando B já implica um alvo não tautológico.

As listas representam conjuntos de fórmulas Z3. A pertença, a inclusão e a
remoção de duplicados usam **igualdade estrutural** (`.eq()`). Fórmulas
logicamente equivalentes com estruturas diferentes não são fundidas.
**Equivalência lógica** e **consequência lógica** exigem inferência: a dedução
é verificada por insatisfatibilidade das premissas em conjunto com a negação
do alvo. Não se devem converter expressões simbólicas Z3 em booleanos Python
para comparar conjuntos.

## Organização do projeto

```text
.
├── main.py
├── belief_bases/
│   ├── __init__.py
│   ├── modelos.py
│   ├── parser_formulas.py
│   ├── operacoes_conjuntos.py
│   ├── deducao.py
│   ├── subconjuntos.py
│   ├── analise.py
│   ├── contracoes/
│   │   ├── __init__.py
│   │   ├── partial_meet.py
│   │   ├── kernel.py
│   │   ├── smooth_kernel.py
│   │   ├── agm.py
│   │   └── limitada.py
│   └── cli/
│       ├── __init__.py
│       ├── entrada.py
│       ├── apresentacao.py
│       └── menu.py
├── scripts/
│   └── benchmark_analise.py
├── requirements.txt
├── requirements-dev.txt
├── requirements-build.txt
├── RelatorioBelifBases.pdf
└── BeliefBasesProgram-refatorado.exe
```

| Módulo | Responsabilidade |
| --- | --- |
| `main.py` | Inicialização, encerramento e erros na fronteira da aplicação |
| `modelos.py` | Tipos partilhados e dataclass `ResultadoAnalise` |
| `parser_formulas.py` | Identificadores, tokenização, gramática e formatação |
| `operacoes_conjuntos.py` | Igualdade estrutural, inclusão, interseções e duplicados |
| `deducao.py` | Inferência com Z3 e verificador com cache por análise |
| `subconjuntos.py` | Conjunto das partes, minimais, maximais, kernels e remainders |
| `contracoes/` | Operadores matemáticos independentes da interface |
| `analise.py` | Coordenação, reutilização de resultados e seleção de B |
| `cli/` | Leitura, validação, apresentação e navegação |

A implementação reside em `belief_bases/`, importado diretamente pela
aplicação e pelos exemplos da API. Os quatro módulos de compatibilidade
que existiam na raiz foram removidos. Dentro do pacote, o nome legado
`encontra_subconjuntos_maximais_com_subconjunto()` continua disponível, mas
corresponde à contração limitada; o nome explícito é
`encontrar_contracoes_limitadas()`.

Estão disponíveis partial meet, full meet, kernel, smooth kernel, basic
AGM-generated base contraction e bounded contraction (contração limitada),
além da família de resultados possíveis de base contraction. A fundamentação
e as convenções matemáticas seguem o [PDF original](RelatorioBelifBases.pdf).

## Desenvolvimento

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m ruff check --target-version py310 --line-length 88 --select E,F,I,UP,B main.py belief_bases scripts
.\.venv\Scripts\python.exe -m ruff format --check --target-version py310 --line-length 88 main.py belief_bases scripts
```

Em Linux/macOS, substitua `.\.venv\Scripts\python.exe` por
`./.venv/bin/python` nos comandos de desenvolvimento.

Para medir uma análise de seis premissas e a seleção posterior de B:

```powershell
.\.venv\Scripts\python.exe -m scripts.benchmark_analise
```

O script apresenta tempos e contagens de chamadas a `Solver.check`. Os
tempos dependem da máquina; as contagens permitem comparar a quantidade de
inferência realizada. Estes números medem desempenho, não a correção dos
resultados.

## Gerar um executável

No sistema de destino, com o ambiente virtual já criado, use o respetivo
Python. Em Windows (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --clean --onefile --collect-binaries z3 --name BeliefBasesProgram-refatorado main.py
```

Em Windows, o novo executável será gerado em
`dist/BeliefBasesProgram-refatorado.exe`. Existe também uma cópia do
executável validado na raiz. Após alterações ao código-fonte, gere um novo
executável para o atualizar. A opção `--collect-binaries z3` inclui as
bibliotecas nativas do Z3, necessárias para carregar o motor de inferência.
Confirme o arranque e uma análise completa no executável gerado.

Referência da ferramenta: [manual oficial do PyInstaller](https://pyinstaller.org/en/latest/).

## Desempenho e limites

Os algoritmos enumeram resultados exatos. Uma base com `n` fórmulas pode
gerar `2^n` subconjuntos. Para `m` remainders, a enumeração partial meet pode
considerar `2^m - 1` seleções não vazias. O número de resultados e o consumo
de memória também podem crescer exponencialmente; a aplicação destina-se
a bases pequenas.

Cada análise classifica os subconjuntos uma vez e partilha os kernels, os
remainders e as partes necessárias entre os operadores. A cache de dedução
fica limitada à análise corrente. A apresentação não volta a calcular os
algoritmos; escolher outro B para o mesmo par base/alvo apenas filtra os
resultados existentes, sem novas chamadas ao solver. Não são usadas
aproximações para limitar a enumeração.
