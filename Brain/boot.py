from rich.console import Console
from rich.panel import Panel

import time

from narrator import BOOT_SEQUENCE

from diagnostics import check_ollama

from config import load_config

from status import READY, FAILED

console = Console()

cfg = load_config()

console.print()

console.print(
    Panel.fit(
        f"[bold cyan]{cfg['name']}[/bold cyan]\nBoot Contract v0.0.2",
        border_style="cyan",
    )
)

console.print()

for text, component in BOOT_SEQUENCE:

    console.print(f"[yellow]>[/yellow] {text}")

    time.sleep(0.4)

    if component == "Ollama":

        if check_ollama():

            console.print(f"    Ollama detected.")

            console.print(f"    STATUS : {READY}")

        else:

            console.print(f"    Ollama unavailable.")

            console.print(f"    STATUS : {FAILED}")

console.print()

console.print(f"[bold green]Good morning, {cfg['owner']}.[/bold green]")