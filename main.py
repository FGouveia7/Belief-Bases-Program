# main.py
import sys
from colorama import init, Fore, Style
from interface import menu_interativo

init(autoreset=True)

if __name__ == "__main__":
    try:
        while True:
            try:
                menu_interativo()
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n\nProgram interrupted by the user.")
                break
            except EOFError:
                print(Fore.YELLOW + "\n\nInput ended unexpectedly.")
            except Exception as e:
                print(Fore.RED + f"\n\nAn unexpected error occurred: {e}")
                print(Fore.YELLOW + "The current session was stopped, but you can start a new one.")

            try:
                resposta = input(
                    Style.BRIGHT + "\nPress Enter to exit or type 1 to start a new session: "
                ).strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n\nProgram interrupted by the user.")
                break

            if resposta != "1":
                break
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nProgram interrupted by the user.")
    finally:
        try:
            import colorama.initialise
            colorama.initialise.deinit()
        except Exception:
            pass
        sys.exit(0)