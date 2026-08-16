# Belief Bases Program

Programa em Python para manipulação e inferência sobre bases de crenças.

## Objetivo

Fornecer operações de análise, inferência e gestão de bases de crenças.

## Requisitos

- Python 3.10 ou superior

### 3.1 Ambiente de desenvolvimento

1. Linguagem: Python
2. Bibliotecas e ferramentas usadas durante o desenvolvimento:
   1. z3-solver: motor lógico Z3 para avaliação de satisfatibilidade booleana, manipulação de
      variáveis simbólicas e verificação por refutação.
   2. itertools (biblioteca padrão): cálculos de combinações e geração eficiente do espaço potência
      da base de crenças.
   3. ast e re (biblioteca padrão): análise de expressão e tradução da sintaxe lógica de entrada
      para representações internas do Z3 através de travessia e transformação da AST.
3. Executável: empacotamento com PyInstaller 4 para gerar um ficheiro executável único (.exe) que
   inclui o intérprete Python, os módulos e o motor Z3.
4. Reproduzir o ambiente: criar um ambiente virtual e instalar as dependências listadas em
   `requirements.txt`.

## Instalação

1. Clonar o repositório

```powershell
git clone <url-do-repositorio>
cd Belief-Bases-Program
```

2. Criar e ativar um ambiente virtual

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Instalar dependências (se existir `requirements.txt`)

```powershell
pip install -r requirements.txt
```

## Execução

Executar a aplicação principal:

```powershell
python main.py
```

## Arquitetura e responsabilidades

## Contribuição

1. Fork do repositório
2. Criar branch por funcionalidade
3. Submeter pull request com descrição técnica das alterações

## Licença

Sem licença definida no repositório.

## Referências

- RelatorioBelifBases.pdf: descrição técnica de cada operação implementada (documento de
  referência). [RelatorioBelifBases.pdf](RelatorioBelifBases.pdf)

# Belief-Bases-Program
