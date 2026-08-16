# Belief Bases Program

A Python program for the **manipulation and inference of belief bases**.

## Objective

The main objective of this project is to provide operations for the **analysis, inference, and management of belief bases**, using logical reasoning and satisfiability checking.

## Requirements

* Python **3.10 or higher**

## 3.1 Development Environment

1. **Programming language:** Python
2. **Libraries and tools used during development:**

   1. **z3-solver:** Z3 logical reasoning engine used for Boolean satisfiability evaluation, symbolic variable manipulation, and proof by refutation.
   2. **itertools:** Python standard library used for combination calculations and efficient generation of the power set of a belief base.
   3. **ast and re:** Python standard libraries used for expression analysis and translation of the input logical syntax into internal Z3 representations through AST traversal and transformation.
3. **Executable:** The application can be packaged using **PyInstaller 4** to generate a standalone `.exe` executable containing the Python interpreter, project modules, and Z3 engine.
4. **Environment reproduction:** Create a virtual environment and install the dependencies listed in `requirements.txt`.

## Installation

### 1. Clone the repository

```powershell
git clone <repository-url>
cd Belief-Bases-Program
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

If a `requirements.txt` file is available:

```powershell
pip install -r requirements.txt
```

## Usage

Run the main application with:

```powershell
python main.py
```

## Architecture and Responsibilities

The project is organized into several modules, each responsible for a specific part of the application:

* **`main.py`** — Main entry point of the application.
* **`interface.py`** — Handles the command-line interface and user interaction.
* **`motor_logico.py`** — Implements the logical inference engine and reasoning rules.
* **`operacoes_conjuntos.py`** — Provides operations for manipulating sets and belief bases.
* **`parser_formulas.py`** — Parses and transforms logical formulas into representations that can be processed by the Z3 engine.
* **`main.spec`** — PyInstaller specification file used to configure executable generation.

## Contribution

Contributions are welcome.

1. Fork the repository.
2. Create a branch for your feature or fix.
3. Implement and test your changes.
4. Submit a Pull Request with a clear technical description of the changes.

Example:

```bash
git checkout -b feature/new-operation
```

## License

No license has currently been defined for this repository.

## References

* **`RelatorioBelifBases.pdf`** — Technical description of the implemented operations and reference documentation.

[RelatorioBelifBases.pdf](RelatorioBelifBases.pdf)

---

**Belief-Bases-Program**
