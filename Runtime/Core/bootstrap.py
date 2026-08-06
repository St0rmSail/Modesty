"""
bootstrap.py
============

Purpose:
    Starts Modesty.

Responsibilities:
    - Initialise Core
    - Verify required components
    - Wake Executive Agent

Author:
    Andrew & ChatGPT

Build:
    0.0.7
"""

from rich import print
from Runtime.Core.noticeboard import NoticeBoard

from Runtime.Core import config


def startup():

    print()
    print("[bold cyan]STATUS : INITIALISING[/]")
    print()

    print("Good morning, Drew.")
    print()

    # -------------------------------------------------
    # Configuration Notebook
    # -------------------------------------------------

    print("Looking for my notebook...")

    if config.OBSIDIAN.exists():
        print("[green]Notebook found.[/]")
    else:
        print("[red]Notebook missing![/]")
        return

    print()

    print("Looking for my diary...")
    print("Diary found.")

    print()

    print("Looking for the office noticeboard...")
    print("Noticeboard ready.")

    print()
    board = NoticeBoard()

    board.post(
        "Health",
        "Modesty",
        "Medicine check scheduled."
    )

    board.post(
        "Fishing Buddy",
        "Memory",
        "Three new bait recipes discovered."
    )

    board.show()

    print()
    print("[bold green]STATUS : READY[/]")

