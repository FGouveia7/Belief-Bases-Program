"""Ponto de entrada e fronteira de tratamento de erros da aplicação."""

import sys
import traceback

from colorama import Fore, Style, deinit, init

from belief_bases.cli.menu import menu_interativo


def main() -> int:
    """Executa sessões e devolve um estado adequado ao processo chamador."""
    init(autoreset=True)
    try:
        while True:
            menu_interativo()
            resposta = input(
                Style.BRIGHT
                + "\nPress Enter to exit or type 1 to start a new session: "
            ).strip()
            if resposta != "1":
                return 0
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nProgram interrupted by the user.")
        return 130
    except EOFError:
        print(Fore.YELLOW + "\n\nInput ended unexpectedly.")
        return 0
    except Exception as erro:
        # A fronteira da aplicação preserva o diagnóstico de erros inesperados.
        print(Fore.RED + f"\n\nAn unexpected error occurred: {erro}", file=sys.stderr)
        traceback.print_exc()
        return 1
    finally:
        deinit()


if __name__ == "__main__":
    sys.exit(main())
