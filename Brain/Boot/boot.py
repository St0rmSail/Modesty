from rich import print
import ollama


def boot():

    print()
    print("[bold cyan]Good morning, Drew.[/bold cyan]")
    print()

    print("[cyan]Looking for the Brain...[/cyan]")

    try:
        ollama.list()

        print("    Ollama detected.")
        print("    STATUS : READY")

    except Exception:

        print("    Brain is fuzzy...")
        print("    Ollama not found.")
        print("    Get the coffee.")