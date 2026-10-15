# Relatório de refatorização

## 1. Estrutura atual

Este relatório conserva os resultados históricos da refatorização. Depois
dessa validação, o utilizador removeu os quatro módulos de compatibilidade
da raiz e o executável original. A suíte de testes foi também removida a
pedido, para preparar a publicação no GitHub.

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
├── scripts/benchmark_analise.py
├── requirements.txt
├── requirements-dev.txt
├── requirements-build.txt
├── pyproject.toml
├── README.md
├── REFATORACAO.md
├── RelatorioBelifBases.pdf
└── BeliefBasesProgram-refatorado.exe
```

Ambientes `.venv`, `.venv310`, o Python local de validação, caches e artefactos
temporários em `tmp/` são ignorados pelo Git. O PDF original mantém-se.
O executável validado da versão refatorizada foi copiado para a raiz pelo
utilizador.

## 2. Problemas encontrados

- `interface.mostrar_resultados()` misturava inferência, enumeração,
  organização e impressão. Os ciclos de menu repetiam validações e capturavam
  erros de programação como se fossem erros de entrada.
- Kernels e remainders percorriam separadamente o mesmo conjunto das partes.
  Kernel e bounded voltavam a calcular os remainders. Smooth verificava
  inferências inclusive para elementos já presentes no candidato.
- Impressão das famílias e verificações de pertença estavam duplicadas.
- A igualdade de conjuntos podia ser assimétrica na presença de repetições.
  Interseções propagavam duplicados da primeira lista.
- Um remainder vazio representado por `set()` era confundido com ausência
  de remainders. A comparação de listas com coleções Z3 era inadequada.
- O AGM aplicava eliminação disjuntiva, mas omitia vacuidade quando o alvo
  não era consequência da base.
- A validação de nomes aceitava identificadores que o parser não conseguia
  referenciar como uma variável: `pVq`, nomes com `×` e nomes com `÷`.
- O README descrevia um parser baseado em AST; o código real era um parser
  recursivo-descendente. `colorama` não constava das dependências e o
  PyInstaller antigo estava misturado com as dependências de execução.
- `ler_variaveis`, `ler_premissas` e auxiliares de leitura individual já não
  eram usados pelo menu principal. Foram preservados como API legada.

## 3. Alterações por ficheiro na refatorização

As entradas sobre adaptadores e testes descrevem trabalho histórico;
esses ficheiros já não fazem parte da estrutura atual.

| Ficheiro ou grupo | Alteração implementada |
| --- | --- |
| `main.py` | Função `main()`, ciclo de sessões, inicialização/finalização de colorama, tratamento de EOF e interrupção, traceback e estado de erro |
| `belief_bases/modelos.py` | Tipos de conjuntos/famílias, contrato de inferência e `ResultadoAnalise`, sem igualdade automática sobre BoolRef |
| `belief_bases/parser_formulas.py` | Parser movido, tipado e documentado; validação de nomes partilhada e auxiliares comuns de formatação |
| `belief_bases/operacoes_conjuntos.py` | Pertença explícita por `.eq()`, igualdade bidirecional, normalização e interseções consistentes |
| `belief_bases/deducao.py` | Refutação Z3, erro explícito para `unknown`, cache privada de inferência por análise |
| `belief_bases/subconjuntos.py` | Geração de partes, filtros por inclusão, classificação conjunta de kernels/remainders e nomes explícitos |
| `contracoes/partial_meet.py` | Partial meet por seleções e full meet por interseção direta, com convenção de tautologia |
| `contracoes/limitada.py` | Contração limitada e filtro de B sobre candidatos já calculados |
| `contracoes/kernel.py` | Contração limitada pelo full meet, reutilizando as partes dos remainders |
| `contracoes/smooth_kernel.py` | Filtro de fecho relativo, evitando inferência para crenças que já pertencem ao candidato |
| `contracoes/agm.py` | Predicado de eliminação disjuntiva separado do operador e correção de vacuidade |
| `belief_bases/analise.py` | Coordenação de todos os operadores e seleção posterior de B sem inferência |
| `cli/entrada.py` | Validação e repetição apenas de erros de entrada, novas leituras, índices B e normalização estrutural |
| `cli/apresentacao.py` | Apresentação apenas de resultados calculados, com impressão comum de famílias |
| `cli/menu.py` | Ações dedicadas e conservação da análise enquanto se escolhem limites B |
| Quatro módulos originais da raiz, posteriormente removidos | Importações explícitas e adaptadores que preservavam funções e assinaturas anteriores |
| `requirements*.txt` | Separação entre execução, desenvolvimento e empacotamento |
| `pyproject.toml` e `.gitignore` | Ruff para Python 3.10, estilo consistente e exclusão de ambientes/caches; a configuração pytest foi posteriormente removida |
| Suíte de testes, posteriormente removida | Caracterização, regressões, propriedades, oráculos independentes e sessões simuladas |
| `scripts/benchmark_analise.py` | Medição reproduzível de tempos e chamadas reais a `Solver.check` |
| `README.md` | Instruções de instalação, parser, API, execução, desenvolvimento, build e limites |

## 4. Clean Code e SOLID

Aplicou-se responsabilidade única a leitura, apresentação, inferência,
enumeração, operadores e coordenação. A impressão comum, a pertença
estrutural e a validação de identificadores concentram regras antes
repetidas. As funções públicas relevantes têm tipos e docstrings.

Os filtros smooth/AGM e a classificação aceitam uma função de inferência:
isso permite injetar o verificador com cache e testar os algoritmos sem
acoplar a apresentação ao solver. Não foram criadas hierarquias de classes
ou padrões sem necessidade; não se reivindica a aplicação artificial de
Liskov ou segregação de interfaces a um projeto essencialmente funcional.

## 5. Modularidade e compatibilidade

O fluxo de dependências é `CLI → análise → operadores → subconjuntos /
dedução / conjuntos → modelos`. O parser é independente dos operadores.
Os módulos de domínio não importam a CLI nem imprimem resultados.
Não há dependências circulares ou importações com `*`.

Após a refatorização, os testes foram atualizados para importar diretamente
de `belief_bases`. O teste específico do adaptador de apresentação foi
substituído por um teste da apresentação de `ResultadoAnalise`. Essa
atualização retirou a dependência dos quatro adaptadores da raiz.
A validação desta atualização executou os 229 testes com as importações dos
quatro adaptadores explicitamente bloqueadas: todos passaram. Ruff e a
verificação de formatação também passaram. Posteriormente, o utilizador
apagou os adaptadores e pediu a remoção da suíte. A aplicação importa
diretamente de `belief_bases`; os caminhos antigos da raiz já não estão
disponíveis.

Todos os algoritmos originais continuam disponíveis no pacote, assim como
os nomes públicos legados internos. O nome
`encontra_subconjuntos_maximais_com_subconjunto()` descrevia incorretamente
o seu resultado: a função calcula resultados de contração limitada, não
apenas conjuntos maximais. O novo nome é
`encontrar_contracoes_limitadas()`; o antigo delega sem alterar a semântica.

A representação mantém listas de BoolRef. Pertença e inclusão são
estruturais; fórmulas logicamente equivalentes não são fundidas. O operador
`==` do Z3 continua a ser usado corretamente para construir equivalências
no parser, nunca como substituto da igualdade de conjuntos.

## 6. Correções de comportamento, separadas da refatorização

As seguintes correções foram demonstradas por testes antes de serem feitas.
A coluna de evidência resume os casos da suíte histórica, agora removida:

| Bug | Antes | Depois | Evidência |
| --- | --- | --- | --- |
| Igualdade com duplicados | `[p,p]` igual a `[p,q]`, mas o inverso falso | Inclusão nas duas direções, ignorando multiplicidade | Regressão de igualdade de conjuntos |
| Interseção com repetições | Interseção de `[p,p,q]` e `[p]` era `[p,p]` | Resultado `[p]` | Regressão de interseção |
| Remainder vazio | `todas_intersecoes_maximais([p], [set()])` devolvia `[[p]]` | Devolve `[[]]` | Caso derivado da definição 1 do relatório |
| Vacuidade AGM | `A={p}`, alvo `q`, aceitava `∅` e `{p}` | Apenas `{p}` | Caso derivado da Observação 5 do relatório |
| Nomes impossíveis | Regex aceitava `pVq`, `p×q` e `p÷q` | Validação coerente com tokenização | Três regressões de regex e testes CLI |

O predicado `verifica_condicao_AGM()` continua a testar apenas eliminação
disjuntiva. A correção de vacuidade pertence a `calcula_AGM()`; os restantes
operadores não receberam indevidamente essa regra.

Também se tornaram explícitos comportamentos de erro: EOF termina sem nova
leitura, Ctrl+C devolve 130 e falhas inesperadas devolvem 1 com traceback.
Só `ValueError`, incluindo `ErroParse`, desencadeia repetição de entrada.
Uma entrada inválida da base é substituída por nova leitura completa.
Duplicados estruturais de A são normalizados antes de gerar partes. O
resultado `unknown` do Z3 provoca erro explícito em vez de ser confundido
com ausência de dedução.

A mudança de módulos, os adaptadores, os tipos, a separação de impressão
e a reutilização de resultados são refatorizações estruturais. Não mudam
a sintaxe nem as regras dos operadores. Na validação da refatorização, os
testes de caracterização passaram para os casos sem os bugs corrigidos.

### Fundamentação matemática consultada

O PDF foi extraído e as páginas matemáticas relevantes foram renderizadas
para inspeção. Referências pela numeração impressa:

- p. 5: inclusão, sucesso, falha, vacuidade, fecho relativo e eliminação
  disjuntiva;
- pp. 6–8: remainders, kernels, incisões, Observações 3–5 e definição AGM;
- pp. 10–12: procedimentos de partial/full meet, bounded, kernel, smooth
  e AGM.

O §3.9 descreve o filtro disjuntivo sem explicitar vacuidade; a Observação 5
exige-a. Essa diferença é a razão documentada para a correção AGM. O
tratamento de tautologias mantém A conforme os casos especiais do relatório.
O PDF não contém exemplos concretos com p/q: os testes eram casos derivados
das suas definições, identificados como tal.

## 7. Desempenho medido

Medição em Windows, Python 3.13.12, Z3 4.16.0.0, usando
`A={p,p -> q,q,r,s,t}`, alvo `q`, e depois `B={r}`:

| Operação | Original | Refatorizado |
| --- | ---: | ---: |
| Consultas Z3 na análise | 304 | 160 |
| Consultas adicionais ao escolher B | 64 | 0 |
| Tempo da análise, ensaio indicativo | 0,327 s | 0,155 s |

A redução de consultas na análise é aproximadamente 47%. Tempos de um
ensaio não são uma garantia de aceleração noutras bases ou máquinas.
`python -m scripts.benchmark_analise` permite repetir a medição nova.

A classificação dos subconjuntos é partilhada pelos kernels e remainders;
as partes dos remainders são reutilizadas pelos outros operadores. A cache
de dedução existe só durante uma análise e retém as fórmulas consultadas
para evitar reutilização indevida de IDs Z3. Não existe cache global que
possa devolver resultados de outra base ou contexto. Apresentar resultados
e selecionar B são operações sem chamadas ao solver, verificadas na suíte
histórica.

Os adaptadores legados entretanto removidos recebiam base/alvo em vez de
`ResultadoAnalise` e calculavam uma análise própria para preservar as assinaturas.
O menu novo usa sempre o objeto calculado.

## 8. Verificações históricas executadas

Os resultados desta secção foram obtidos durante a refatorização e a
atualização das importações. O código dos testes foi posteriormente
removido a pedido. Não houve nova execução de pytest após essa remoção;
estes números não representam uma nova validação do estado atual.

Antes de modificar a produção: **80 testes passaram e 4 falharam**, sendo
as quatro falhas os bugs de conjuntos e AGM documentados acima. Os 50 testes
iniciais do parser e os 10 da CLI passaram. As três regressões de nomes
foram acrescentadas e também falharam antes da correção.

Validação final da refatorização:

| Verificação | Resultado |
| --- | --- |
| Python 3.10.20: `python -m pytest -q` | **229 passed**, sem avisos, 1,65 s |
| Python 3.13.12: `python -m pytest -q` | **229 passed**, 2,11 s |
| `python -m ruff check .` | **All checks passed!** |
| `python -m ruff format --check .` | **32 files already formatted**, incluindo a documentação |
| `git diff --check` | Sem erros de whitespace |
| PyInstaller 6.22.3, Python 3.13.12, Windows | Build de teste concluído com `--collect-binaries z3` |
| Executável de teste | Sessão base/alvo/B/saída concluída com código **0** |
| PDF e EXE originais, na altura da validação | Sem alterações no diff Git; o EXE original foi posteriormente removido pelo utilizador |

Distribuição dos 229 testes: caracterização 4; parser 69; dedução 5;
conjuntos 5; contrações/propriedades 34; relatório/oráculo 84; CLI 28.
Incluíam inclusão, sucesso, vacuidade onde aplicável, minimalidade e
maximalidade por inclusão, incisões enumeradas independentemente, fecho
relativo, extensionalidade e sessões completas da interface.

Os 84 testes do relatório incluíam **72 casos AGM** comparados com um
oráculo independente que enumera conjuntos de modelos de duas variáveis
e impunha os postulados básicos, incluindo recuperação. Esse oráculo não usava
os filtros de remainders, kernels ou eliminação disjuntiva da implementação.

O primeiro build simples foi gerado mas falhou ao arrancar por não incluir
`libz3.dll`. O comando do README foi corrigido para recolher os binários Z3,
o build foi repetido e a sessão simulada passou. O executável gerado nessa
validação foi posteriormente copiado pelo utilizador para
`BeliefBasesProgram-refatorado.exe` na raiz. O executável original já foi
removido.

As ferramentas auxiliares de leitura/renderização PDF foram usadas apenas
no ambiente de trabalho; não foram acrescentadas às dependências da aplicação.

## 9. Limites da validação

- Testaram-se Python 3.10 e 3.13 em Windows. Outros sistemas, arquiteturas
  e versões intermédias não foram executados nesta sessão.
- O executável foi testado nesta máquina, a partir de uma pasta sem os
  módulos-fonte. Não foi testado numa máquina Windows limpa nem distribuído.
- Os testes executados eram finitos; não constituem prova formal para todas as bases.
  As definições do relatório e os oráculos independentes complementam a
  caracterização da implementação original.
- A enumeração continua exata e exponencial: 2**n partes e até 2**m - 1
  seleções para m remainders. Não se promete escalabilidade para bases grandes.
- A formatação de conjunções/disjunções pode preservar equivalência lógica
  sem preservar a árvore associativa original. True/False formatados pelo Z3
  não são literais especiais do parser.
- `ResultadoAnalise` contém listas mutáveis. Integrações devem tratá-lo como
  resultado de leitura e não alterar as famílias antes de escolher B.

## 10. Melhorias futuras possíveis

Sem implementar funcionalidades fora do âmbito: acrescentar integração
contínua em várias versões/sistemas, testar o executável numa máquina limpa,
medir bases maiores e estudar poda por monotonia ou interseções incrementais
quando as medições justificarem. Qualquer melhoria de enumeração deve manter
os mesmos resultados exatos e continuar coberta por oráculos independentes.
