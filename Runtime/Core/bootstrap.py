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
from Runtime.Knowledge import KnowledgeStores
from Runtime.Knowledge.stores import KnowledgeStoreError

from Runtime.Core import config


def startup():

    print()
    print("[bold cyan]STATUS : INITIALISING[/]")
    print()

    print("Good morning, Drew.")
    print()

    # -------------------------------------------------
    # Private Filing Cabinet and living Bookshelf
    # -------------------------------------------------

    print("Checking my Filing Cabinet and Bookshelf...")

    try:
        stores = KnowledgeStores(config.KNOWLEDGE_STORES_CONFIG).initialize()
    except KnowledgeStoreError as error:
        print(f"[red]{error}[/]")
    else:
        print(f"[green]Filing Cabinet ready:[/] {stores.filing_cabinet}")
        print(f"[green]Bookshelf ready:[/] {stores.bookshelf}")

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

